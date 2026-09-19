from flask import Flask, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid

from document_loader import load_document
from chunker import chunk_text
from embedding import create_embeddings
from vector_store import add_documents
from rag import ask_question
from custom_tools import get_document_stats

# ==========================================
# UPLOAD FOLDER
# ==========================================

UPLOAD_FOLDER = Path("../data/documents")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


# ==========================================
# FLASK APP
# ==========================================

app = Flask(
    __name__,
    static_folder="../app",
    static_url_path=""
)


# ==========================================
# CONVERSATION MEMORY
# ==========================================

# Stores conversation history separately
# for each uploaded document.

conversation_history = {}


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return app.send_static_file("index.html")


# ==========================================
# UPLOAD DOCUMENT
# ==========================================

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("file")

    # Create a unique ID for every uploaded document
    document_id = str(uuid.uuid4())


    # Check if file exists
    if not file:

        return jsonify({
            "error": "No file uploaded"
        }), 400


    # Secure filename
    filename = secure_filename(file.filename)


    # Create file path
    file_path = UPLOAD_FOLDER / filename


    # Save uploaded file
    file.save(file_path)


    # ==========================================
    # PROCESS DOCUMENT
    # ==========================================

    # Extract text
    text = load_document(file_path)


    # Split text into chunks
    chunks = chunk_text(text)


    # Create embeddings
    embeddings = create_embeddings(chunks)


    # Store chunks + embeddings in ChromaDB
    add_documents(
        chunks,
        embeddings,
        document_id
    )


    # ==========================================
    # CREATE MEMORY FOR THIS DOCUMENT
    # ==========================================

    conversation_history[document_id] = []


    # ==========================================
    # RESPONSE
    # ==========================================

    return jsonify({

        "message": "File uploaded and processed successfully",

        "filename": filename,

        "document_id": document_id,

        "chunks": len(chunks)

    })


# ==========================================
# ASK QUESTION
# ==========================================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()


    # Get question
    question = data.get("question")


    # Get current document ID
    document_id = data.get("document_id")


    # ==========================================
    # VALIDATION
    # ==========================================

    if not question:

        return jsonify({
            "error": "Question is required"
        }), 400


    if not document_id:

        return jsonify({
            "error": "Document ID is required"
        }), 400


    # ==========================================
    # MAKE SURE MEMORY EXISTS
    # ==========================================

    if document_id not in conversation_history:

        conversation_history[document_id] = []


    # ==========================================
    # GET ANSWER FROM RAG
    # ==========================================

    answer = ask_question(
    question,
    document_id,
    conversation_history[document_id]
)


    # ==========================================
    # SAVE CONVERSATION
    # ==========================================

    conversation_history[document_id].append({

        "question": question,

        "answer": answer

    })


    # ==========================================
    # RESPONSE
    # ==========================================

    return jsonify({

        "answer": answer

    })


# ==========================================
# RUN SERVER
# ==========================================


@app.route("/stats/<document_id>", methods=["GET"])
def document_stats(document_id):

    stats = get_document_stats(document_id)

    return jsonify(stats)


if __name__ == "__main__":

    app.run(debug=True)