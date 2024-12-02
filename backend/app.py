
import os
from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import execute_values
import warnings
import csv
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from sentence_transformers import SentenceTransformer
import google.generativeai as genai  # API 
import re


# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load SBERT model
# model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('paraphrase-distilroberta-base-v1')

# Database connection function
# def get_db_connection():
#     return psycopg2.connect(os.environ['DATABASE_URL'])

def check_for_alphanumeric(s):
    pattern = r'[A-Za-z(){}\[\]0-9:;,.?"\'/\-\u00E9\u2018\u2019\u2014*\u2013\u2014\u2014\u2013]'
    temp = re.sub(pattern, '', s)
    return temp


def get_db_connection():
    return psycopg2.connect(
        host="localhost",            # Your local PostgreSQL host
        database="smartsearch_db",   # Replace with your local database name
        user="postgres",             # Replace with your PostgreSQL username
        password="Rajat@1234"     # Replace with your PostgreSQL password
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create pgvector extension if it doesn't exist
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create table if it doesn't exist
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

    # Create an index on the embedding column for faster similarity searches
    cur.execute("""
        CREATE INDEX IF NOT EXISTS embedding_idx ON smartsearch USING ivfflat (embedding vector_cosine_ops)
    """)

    conn.commit()
    cur.close()
    conn.close()

def check_and_initialize_db():
    print("Checking database initialization...")
    if not os.path.exists('db_initialized.flag'):
        print("Initializing database...")
        init_db()
        print("Processing CSV files...")
        process_all_csv_files()
        with open('db_initialized.flag', 'w') as flag_file:
            flag_file.write('Database initialized')
        print("Database initialized and CSV files processed.")
    else:
        print("Database already initialized. Skipping initialization.")

def compute_embedding(text):
    return model.encode(text).tolist()

def process_csv_chunk(chunk):
    embeddings = []
    for row in chunk:
        embedding = compute_embedding(row['Text'])
        embeddings.append((
            row['Book Author'], row['Book Name'], row['Book URL'], row['Chapter Name'],
            row['Chapter Number'], int(row['Page']), int(row['Paragraph']),
            row['Text'], row['Topic'], embedding
        ))
    return embeddings

def process_csv_file(csv_file, batch_size=1000):
    conn = get_db_connection()
    cur = conn.cursor()

    with open(csv_file, 'r', encoding='utf-8') as file:
        csvreader = csv.DictReader(file)
        chunk = []
        for i, row in enumerate(csvreader):
            chunk.append(row)
            if len(chunk) == batch_size:
                with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                    results = list(executor.map(process_csv_chunk, [chunk]))
                
                flattened_results = [item for sublist in results for item in sublist]
                
                # Use execute_values for bulk insert
                execute_values(cur, """
                    INSERT INTO smartsearch (book_author, book_name, book_url, chapter_name, chapter_number, page, paragraph, text, topic, embedding)
                    VALUES %s
                """, flattened_results)
                
                conn.commit()
                chunk = []

        # Process remaining rows
        if chunk:
            with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                results = list(executor.map(process_csv_chunk, [chunk]))
            
            flattened_results = [item for sublist in results for item in sublist]
            
            execute_values(cur, """
                INSERT INTO smartsearch (book_author, book_name, book_url, chapter_name, chapter_number, page, paragraph, text, topic, embedding)
                VALUES %s
            """, flattened_results)
            
            conn.commit()

    cur.close()
    conn.close()


def process_all_csv_files():
    current_directory = os.getcwd()
    # List all CSV files in the current directory
    csv_files = ["/home/rajat_malviya/Documents/SmartSearch/TestChatBoat/"+f for f in os.listdir(current_directory) if f.endswith('.csv')]
    

    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        process_csv_file(csv_file)
        print(f"Finished processing {csv_file}")

#  genrative model 
def genrative_model(train_text,query):
    GOOGLE_API_KEY = "AIzaSyBWbxD6T1RZU45V3EerkMnNjwU7w8r5NL0"
    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')
    # train_text = "Provide a response in a single paragraph: "
    full_query = train_text + query

    # Generate the content
    response = model.generate_content(full_query)

    return response.text

# responce  = genrative_model()

# Flask application code
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_paragraphs():
    data = request.json
    question = data['question']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    train_query ="Provide a response in a single paragraph: "
    query_responce_gemmini = genrative_model(train_query,question)

    print("query_responce_gemmini responce " ,query_responce_gemmini) 
    query_embedding = model.encode(query_responce_gemmini)

    cur.execute("""
        SELECT *, 1 - (embedding <=> %s::vector) AS similarity
        FROM smartsearch
        ORDER BY embedding <=> %s::vector
        LIMIT 5
    """, (query_embedding.tolist(), query_embedding.tolist()))

    results = cur.fetchall()

    cur.close()
    conn.close()
    
    # Filter results with similarity > 0.5  
    filtered_results = [row for row in results if float(row['similarity']) > 0.5]
    # if not filtered_results:
    #     return jsonify({"message": "Sorry, no relevant results found."})

    # Take the top 3 results with the highest similarity
    top_results = filtered_results[:3]
    
    # # Correct the grammar of each chunk
    train_query = 'Correct the grammar and format this text, ensuring that the meaning and information remains unchanged: '

    corrected_chunks = [genrative_model(train_query, row['text']) for row in top_results]
    print("corrrected_chunks ",corrected_chunks)


    # print("top results ",top_results[0])
    # # Combine the grammar-corrected chunks into a final response
    # train_query = "After grammar correction, create a final well-formed, cohesive paragraph that combines all three chunks. The combined paragraph should maintain the context of all chunks, present them in a logical order, and ensure smooth transitions between them without introducing any new information or hallucinations: "
    # combined_response = genrative_model(train_query, " ".join(corrected_chunks))

    if not corrected_chunks:
        return jsonify({"message": "Sorry, no relevant results found."})

    for i in range(len(top_results)):
        top_results[i][8] = check_for_alphanumeric(top_results[i][8])

    for i in range(len(corrected_chunks)):
        top_results[i][8] = corrected_chunks[i]
    
    # print(top_results)

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
        # "combined_response": combined_response  # Add the combined response in the response data
    } for row in top_results])


if __name__ == '__main__':
    print("Starting application...")
    port = int(os.environ.get('PORT', 10000))
    print(f"Attempting to run app on port {port}")
    app.run(host='0.0.0.0', port=port)
    print("App finished running.")
