import sqlite3
import uuid
from datetime import datetime, timezone
from app.config import settings

# plain sqlite, no server needed. content holds the extracted text for search
SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    original_name TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    extension TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def get_conn():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.execute(SCHEMA)


def to_public(row):
    return {
        "_id": row["id"],
        "originalName": row["original_name"],
        "extension": row["extension"],
        "mimeType": row["mime_type"],
        "size": row["size"],
        "createdAt": row["created_at"],
    }


def insert_document(original_name, stored_name, extension, mime_type, size, content):
    doc_id = uuid.uuid4().hex
    created_at = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (doc_id, original_name, stored_name, extension, mime_type, size, content, created_at),
        )
    return get_document(doc_id)


def list_documents():
    with get_conn() as conn:
        # rowid breaks ties when two uploads land in the same microsecond
        return conn.execute("SELECT * FROM documents ORDER BY created_at DESC, rowid DESC").fetchall()


def get_document(doc_id):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()


def delete_document(doc_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
