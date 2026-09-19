from flask import Flask, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
import traceback

from document_loader import load_document
from chunker import chunk_text
from embedding import create_embeddings
from vector_store import add_documents
from rag import ask_question
from custom_tools import get_document_stats

from memory import (
    initialize_memory,
    save_message,
    get_history
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    static_folder="../app",
    static_url_path=""
)


# =========================================================
# CONFIGURATION
# =========================================================

UPLOAD_FOLDER = Path("../data/documents")

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".png",
    ".jpg",
    ".jpeg"
}


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# =========================================================
# INITIALIZE PERSISTENT MEMORY
# =========================================================

initialize_memory()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def allowed_file(filename):

    extension = Path(filename).suffix.lower()

    return extension in ALLOWED_EXTENSIONS


def create_safe_filename(filename):

    safe_name = secure_filename(filename)

    if not safe_name:

        safe_name = "uploaded_document"


    original_path = UPLOAD_FOLDER / safe_name


    if not original_path.exists():

        return safe_name


    stem = Path(safe_name).stem

    extension = Path(safe_name).suffix


    unique_name = (
        f"{stem}_{uuid.uuid4().hex[:8]}{extension}"
    )


    return unique_name


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return app.send_static_file(
        "index.html"
    )


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    file_path = None

    try:

        # -------------------------------------------------
        # Get uploaded file
        # -------------------------------------------------

        file = request.files.get("file")


        if not file:

            return jsonify({
                "error": "No file was uploaded."
            }), 400


        # -------------------------------------------------
        # Check filename
        # -------------------------------------------------

        if not file.filename:

            return jsonify({
                "error": "Please select a file."
            }), 400


        # -------------------------------------------------
        # Check extension
        # -------------------------------------------------

        if not allowed_file(
            file.filename
        ):

            supported = ", ".join(
                sorted(ALLOWED_EXTENSIONS)
            )

            return jsonify({
                "error": (
                    "Unsupported file type. "
                    f"Supported formats: {supported}"
                )
            }), 400


        # -------------------------------------------------
        # Check file size
        # -------------------------------------------------

        file.seek(
            0,
            2
        )

        file_size = file.tell()

        file.seek(0)


        if file_size == 0:

            return jsonify({
                "error": "The uploaded file is empty."
            }), 400


        if file_size > MAX_FILE_SIZE:

            return jsonify({
                "error": (
                    "File is too large. "
                    "Maximum allowed size is 10 MB."
                )
            }), 400


        # -------------------------------------------------
        # Create document ID
        # -------------------------------------------------

        document_id = str(
            uuid.uuid4()
        )


        # -------------------------------------------------
        # Create safe filename
        # -------------------------------------------------

        filename = create_safe_filename(
            file.filename
        )

        file_path = (
            UPLOAD_FOLDER / filename
        )


        # -------------------------------------------------
        # Save file
        # -------------------------------------------------

        file.save(file_path)


        # -------------------------------------------------
        # Extract text
        # -------------------------------------------------

        text = load_document(
            file_path
        )


        if not text or not text.strip():

            raise ValueError(
                "No readable text could be extracted "
                "from this document."
            )


        # -------------------------------------------------
        # Create chunks
        # -------------------------------------------------

        chunks = chunk_text(text)


        if not chunks:

            raise ValueError(
                "The document could not be divided "
                "into text chunks."
            )


        # -------------------------------------------------
        # Create embeddings
        # -------------------------------------------------

        embeddings = create_embeddings(
            chunks
        )


        # -------------------------------------------------
        # Store in ChromaDB
        # -------------------------------------------------

        add_documents(
            chunks,
            embeddings,
            document_id
        )


        # -------------------------------------------------
        # Success
        # -------------------------------------------------

        return jsonify({

            "message":
                "File uploaded and processed successfully.",

            "filename":
                filename,

            "document_id":
                document_id,

            "chunks":
                len(chunks)

        }), 200


    except ValueError as error:

        if (
            file_path
            and file_path.exists()
        ):

            file_path.unlink()


        return jsonify({
            "error": str(error)
        }), 400


    except Exception as error:

        if (
            file_path
            and file_path.exists()
        ):

            file_path.unlink()


        print(
            "\nUPLOAD ERROR:"
        )

        traceback.print_exc()


        return jsonify({
            "error": (
                "Something went wrong while processing "
                "the document. Please try another file."
            )
        }), 500


# =========================================================
# ASK QUESTION
# =========================================================

@app.route(
    "/ask",
    methods=["POST"]
)
def ask():

    try:

        data = request.get_json(
            silent=True
        )


        # -------------------------------------------------
        # Validate request
        # -------------------------------------------------

        if not data:

            return jsonify({
                "error": "Invalid request."
            }), 400


        # -------------------------------------------------
        # Get question
        # -------------------------------------------------

        question = data.get(
            "question"
        )


        if (
            not question
            or not question.strip()
        ):

            return jsonify({
                "error": "Please enter a question."
            }), 400


        question = question.strip()


        # -------------------------------------------------
        # Get document ID
        # -------------------------------------------------

        document_id = data.get(
            "document_id"
        )


        if not document_id:

            return jsonify({
                "error": "No document is selected."
            }), 400


        # -------------------------------------------------
        # GET PERSISTENT MEMORY
        # -------------------------------------------------

        history = get_history(
            document_id
        )


        # -------------------------------------------------
        # ASK RAG AGENT
        # -------------------------------------------------

        answer = ask_question(

            question,

            document_id,

            history

        )


        # -------------------------------------------------
        # Validate answer
        # -------------------------------------------------

        if not answer:

            return jsonify({
                "error":
                    "The agent could not generate an answer."
            }), 500


        # -------------------------------------------------
        # SAVE TO PERSISTENT MEMORY
        # -------------------------------------------------

        save_message(

            document_id,

            question,

            answer

        )


        # -------------------------------------------------
        # RETURN ANSWER
        # -------------------------------------------------

        return jsonify({

            "answer":
                answer

        }), 200


    except Exception as error:

        print(
            "\nQUESTION ERROR:"
        )

        traceback.print_exc()


        return jsonify({
            "error": (
                "Something went wrong while generating "
                "the answer. Please try again."
            )
        }), 500


# =========================================================
# DOCUMENT STATISTICS
# =========================================================

@app.route(
    "/stats/<document_id>",
    methods=["GET"]
)
def document_stats(
    document_id
):

    try:

        stats = get_document_stats(
            document_id
        )


        return jsonify(
            stats
        ), 200


    except Exception as error:

        print(
            "\nSTATS ERROR:"
        )

        traceback.print_exc()


        return jsonify({
            "error": (
                "Unable to retrieve document statistics."
            )
        }), 500


# =========================================================
# RUN FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )