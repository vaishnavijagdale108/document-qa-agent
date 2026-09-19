import sqlite3
from pathlib import Path


# ==========================================
# DATABASE
# ==========================================

DB_PATH = Path("../data/conversation.db")

DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================
# INITIALIZE MEMORY DATABASE
# ==========================================

def initialize_memory():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# SAVE CONVERSATION
# ==========================================

def save_message(
    document_id,
    question,
    answer
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO conversations
        (
            document_id,
            question,
            answer
        )
        VALUES (?, ?, ?)
        """,
        (
            document_id,
            question,
            answer
        )
    )

    connection.commit()
    connection.close()


# ==========================================
# GET CONVERSATION HISTORY
# ==========================================

def get_history(document_id):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            question,
            answer
        FROM conversations
        WHERE document_id = ?
        ORDER BY id ASC
        """,
        (document_id,)
    ).fetchall()

    connection.close()

    return [
        {
            "question": row[0],
            "answer": row[1]
        }
        for row in rows
    ]