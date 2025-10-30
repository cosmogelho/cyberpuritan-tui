# app/models/notes_model.py
from app.core.db import get_db_connection

def add_note(title: str, content: str, tags: str, created_at: str):
    """Adiciona uma nova nota de estudo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (title, content, tags, created_at, created_at)
    )
    conn.commit()
    conn.close()

def get_all_notes():
    """Retorna todas as notas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, tags, created_at FROM notes ORDER BY updated_at DESC")
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id: int):
    """Busca uma nota completa pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    return note
