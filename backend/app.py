import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import DictCursor
from sentence_transformers import SentenceTransformer
import google.generativeai as genai  # API 
import fitz  # PyMuPDF
import csv
import ast
import re
from flask_cors import CORS  # To allow CORS requests from React
from psycopg2.extras import execute_values
import warnings
import csv
from groq import Groq
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from scraping_pipeline import process_pdfs_in_folder
from werkzeug.utils import secure_filename
import pandas as pd


# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes, allowing communication with React frontend


# Load SBERT model
load_dotenv()
warnings.filterwarnings("ignore", category=FutureWarning)

# Load SBERT model
model = SentenceTransformer('paraphrase-distilroberta-base-v1')
# Initialize Groq API
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print(os.getenv("GROQ_API_KEY"))

#  genrative model  using Gemini API
def genrative_model(train_text,query):
    GOOGLE_API_KEY = "AIzaSyBWbxD6T1RZU45V3EerkMnNjwU7w8r5NL0"
    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')
    # train_text = "Provide a response in a single paragraph: "
    full_query = train_text + query

    # Generate the content
    response = model.generate_content(full_query)

    return response.text


# ------------------------------------------------------------------------Basic DB/Operation------------------
def check_for_alphanumeric(s):
    pattern = r'[A-Za-z(){}\[\]0-9:;,.?"\'/\-\u00E9\u2018\u2019\u2014*\u2013\u2014\u2014\u2013]'
    temp = re.sub(pattern, '', s)
    return temp

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        host="localhost",            # Your local PostgreSQL host
        database="smartsearch_db",   # Replace with your local database name
        user="postgres",             # Replace with your PostgreSQL username
        password="Rajat@1234"        # Replace with your PostgreSQL password
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

# ----------------------------------------------- Genrative Model--------------------------------------
# Rephrased System Prompt
system_prompt = (
    "You are a highly precise and concise assistant. Follow these principles when generating responses:\n\n"
    "1. Keep responses as short as possible while fully addressing the user's query.\n"
    "2. Provide only essential information—avoid unnecessary details or elaboration.\n"
    "3. Ensure factual accuracy and avoid guessing or fabricating information.\n"
    "4. Use bullet points or numbered lists for clarity if needed.\n"
    "5. If clarification is required, ask brief and specific follow-up questions.\n"
    "6. Acknowledge uncertainty and suggest external resources only if necessary.\n\n"
    "Additional Behavior:\n"
    "- If asked your name, respond with: 'EVA'.\n"
    "- If asked about your designed or developed or developers or created, respond with: 'Rajat, Satyam, Sandeep, students from Sitare University under the guidance of Dr. Kushal Shah.'\n"
    "- If asked about your purpose or work, respond with: 'I am designed to assist with AI/ML-related queries and provide support for technical tasks.'\n"
    "- Always stay precise, relevant, and focused on the query."
)
# Compute embeddings for text
def compute_embedding(text):
    return model.encode(text).tolist()


# 1. Filtering functions
def contains_inappropriate_content(text):
    """
    Check if the text contains inappropriate or flagged content using regex patterns.
    """
    inappropriate_patterns = [
        r"\b(?:f\*?u\*?c\*?k|s\*?h\*?i\*?t|b\*?i\*?t\*?c\*?h)\b",  # Common profanities with optional masking
        r"\b(?:a\*?s\*?s|d\*?a\*?mn|c\*?u\*?n\*?t)\b",
        r"[^\w\s]{3,}",  # Strings with excessive symbols
        r"(.)\1{3,}",  # Repeated characters like "aaaa" or "!!!!"
    ]

    for pattern in inappropriate_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    if is_random_string(text):
        return True

    return False

def is_random_string(text):
    """
    Check for random-like strings using length and entropy heuristics.
    """
    if len(text.split()) < 5:
        return True

    unique_chars = set(text)
    entropy = len(unique_chars) / len(text)
    return entropy > 0.8

# 2. Main refinement function
def refine_and_answer_with_groq(question, paragraphs):
    # Combine all paragraphs into a single context
    context = "\n\n".join([f"Paragraph {idx + 1}: {para['text']}" for idx, para in enumerate(paragraphs)])
    
    # Filter inappropriate paragraphs
    filtered_paragraphs = [para['text'] for para in paragraphs if not contains_inappropriate_content(para['text'])]
    
    # Calculate relevance using cosine similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([question] + filtered_paragraphs)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    top_indices = similarities.argsort()[-3:][::-1]
    top_paragraphs = [filtered_paragraphs[idx] for idx in top_indices]
    top_context = "\n\n".join([f"Paragraph {idx + 1}: {filtered_paragraphs[idx]}" for idx in top_indices])

    # Generate response using system prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {question}\n\nContext:\n{top_context}"}
    ]
    chat_completion = groq_client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
    )
    response = chat_completion.choices[0].message.content.strip()

    return {
        "response": response,
        "top_paragraphs": top_paragraphs
    }


def query_paragraphs(question):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Generate embedding for the question
    query_embedding = model.encode(question).tolist()

    # Query the database
    cur.execute("""
        SELECT *, 1 - (embedding <=> %s::vector) AS similarity
        FROM smartsearch
        ORDER BY embedding <=> %s::vector
        LIMIT 10
    """, (query_embedding, query_embedding))

    results = cur.fetchall()
    cur.close()
    conn.close()
    # print("reultes ->  ", results)
    return results


# -------------------------API route -----------------------
@app.route("/member")
def members():
    return {"member":["rajat,mayank"]}


# Configure upload and output folders
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_pdf():
    try:
        # Retrieve the uploaded file
        file = request.files.get('file')
        
        # Parse and validate form data
        try:
            form_data = {
                "book_name": request.form.get('bookName'),
                "author_name": request.form.get('authorName'),
                "content_start_page": int(request.form.get('contentStartPage')),
                "content_end_page": int(request.form.get('contentEndPage')),
                "chapter_start_page": int(request.form.get('chapterStartPage')),
                "chapter_end_page": int(request.form.get('chapterEndPage')),
            }
        except (TypeError, ValueError) as e:
            return jsonify({"error": "Invalid form data. Please ensure all fields are filled correctly."}), 400

        print("Form Data:", form_data)

        if not file or not all(form_data.values()):
            return jsonify({"error": "All fields are required."}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        print(f"File saved to: {file_path}")

        # Process PDF files using the provided pipeline function
        process_pdfs_in_folder(
            folder_path=app.config['UPLOAD_FOLDER'],
            tex_file_path_for_heading='./heading_elements.tex',  # Path to the .tex file
            form_data=form_data
        )

        # Generate paths for CSV and Pickle files
        csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.csv")
        df = pd.read_csv(csv_file_path)
        print(df.sample(2))
        pickle_file_path = os.path.join(app.config['OUTPUT_FOLDER'], "output.pkl")

        # Validate if the CSV file exists
        if os.path.exists(csv_file_path):
            # Load the CSV and save it as a Pickle file
            df = pd.read_csv(csv_file_path)
            df.to_pickle(pickle_file_path)

            return jsonify({
                "message": "File uploaded and processed successfully.",
                "csv_path": csv_file_path,
                "pickle_path": pickle_file_path,
            }), 200
        else:
            return jsonify({"error": "Processing failed; CSV not generated."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get("message")
    
    if not os.path.exists('db_initialized.flag'):
        # print("Initializing database...")
        init_db()
        with open('db_initialized.flag', 'w') as flag_file:
            flag_file.write('Database initialized')
        # print("Database initialized.")
    else:
        print("Database already initialized.")

    # print("\nSearching for relevant paragraphs...\n")
    top_results = query_paragraphs(question)

    if len(top_results) == 0:
        # print("No relevant results found.")
        return jsonify({"error": "No relevant results found"}), 404

    answer = refine_and_answer_with_groq(question, top_results)
    # print("answer ", answer['top_paragraphs'])
    # print("top_results ", top_results)
    # print("\n\n")
    # print("\nGenerated Answer:")   
    # for key, value in answer.items():
    #     print(key, value)
    #     print("\n")
        
    response = answer['response']
    arr = answer["top_paragraphs"]
    top_three_relative_ans = []
    for ans in arr:
        found = False
        for idx, result in enumerate(top_results):
            # Assuming the 8th element of each result contains the relevant text
            if ans in result[8]:
                # print(f"Answer found at index {idx} in top_results")
                result.pop(10)
                top_three_relative_ans.append(result)
                found = True
                break
        if not found:
            print("Answer not found in top_results")

    # Return the JSON response
    return jsonify({
        "response": response,
        "top_three_relative_ans": top_three_relative_ans
    })
    



if __name__ == '__main__':
    print("Starting Flask API on port 3002")
    app.run(host='0.0.0.0', port=3002)
