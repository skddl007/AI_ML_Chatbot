import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import DictCursor, execute_values
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import csv
import re
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import warnings

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Load environment variables and suppress warnings
load_dotenv()
warnings.filterwarnings("ignore", category=FutureWarning)

# Load SBERT model
model = SentenceTransformer('paraphrase-distilroberta-base-v1')

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="smartsearch_db",
        user="postgres",
        password="Rajat@1234"
    )

# Initialize database
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS smartsearch (
            id SERIAL PRIMARY KEY,
            book_author TEXT,
            book_name TEXT,
            book_url TEXT,
            chapter_name TEXT,
            chapter_number TEXT,
            page INTEGER,
            paragraph INTEGER,
            text TEXT,
            topic TEXT,
            embedding vector(768)
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS embedding_idx ON smartsearch USING ivfflat (embedding vector_cosine_ops)
    """)
    conn.commit()
    cur.close()
    conn.close()

# Check and initialize the database
def check_and_initialize_db():
    if not os.path.exists('db_initialized.flag'):
        init_db()
        process_all_csv_files()
        with open('db_initialized.flag', 'w') as flag_file:
            flag_file.write('Database initialized')

# Compute text embedding
def compute_embedding(text):
    return model.encode(text).tolist()

# Process a CSV file and insert data into the database
def process_csv_file(csv_file, batch_size=1000):
    conn = get_db_connection()
    cur = conn.cursor()

    with open(csv_file, 'r', encoding='utf-8') as file:
        csvreader = csv.DictReader(file)
        chunk = []
        for row in csvreader:
            chunk.append(row)
            if len(chunk) == batch_size:
                with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                    results = executor.map(compute_embedding_for_chunk, [chunk])
                execute_values(cur, """
                    INSERT INTO smartsearch (book_author, book_name, book_url, chapter_name, chapter_number, page, paragraph, text, topic, embedding)
                    VALUES %s
                """, [item for sublist in results for item in sublist])
                conn.commit()
                chunk = []
        if chunk:
            with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                results = executor.map(compute_embedding_for_chunk, [chunk])
            execute_values(cur, """
                INSERT INTO smartsearch (book_author, book_name, book_url, chapter_name, chapter_number, page, paragraph, text, topic, embedding)
                VALUES %s
            """, [item for sublist in results for item in sublist])
            conn.commit()

    cur.close()
    conn.close()

# Process all CSV files in the directory
def process_all_csv_files():
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    for csv_file in csv_files:
        process_csv_file(csv_file)

# Query for relevant paragraphs
@app.route('/query', methods=['POST'])
def query_paragraphs():
    data = request.json
    question = data.get('question', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    query_embedding = compute_embedding(question)

    cur.execute("""
        SELECT *, 1 - (embedding <=> %s::vector) AS similarity
        FROM smartsearch
        ORDER BY embedding <=> %s::vector
        LIMIT 10
    """, (query_embedding, query_embedding))

    results = cur.fetchall()
    cur.close()
    conn.close()

    filtered_results = [row for row in results if float(row['similarity']) > 0.5]
    if not filtered_results:
        return jsonify({"message": "Sorry, no relevant results found."})

    return jsonify([{
        "content": row['text'],
        "similarity": float(row['similarity']),
        "book_author": row['book_author'],
        "book_name": row['book_name'],
        "book_url": row['book_url'],
        "chapter_name": row['chapter_name'],
        "chapter_number": row['chapter_number'],
        "page": row['page'],
        "paragraph": row['paragraph'],
        "topic": row['topic'],
    } for row in filtered_results[:3]])

# Simple test route
@app.route("/member")
def members():
    return {"members": ["rajat"]}

if __name__ == '__main__':
    check_and_initialize_db()
    print("Starting Flask API on port 3002")
    app.run(host='0.0.0.0', port=3002)
