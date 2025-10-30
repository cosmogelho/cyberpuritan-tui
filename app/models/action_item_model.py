# app/models/action_item_model.py
import sqlite3
from app.core.db import get_db_connection

def add_item(item_type: str, text: str, created_at: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO action_items (item_type, text, status, created_at) VALUES (?, ?, 'Ativo', ?)",
        (item_type, text, created_at)
    )
    conn.commit()
    conn.close()

def get_items(item_type: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM action_items WHERE item_type = ? ORDER BY created_at DESC", (item_type,))
    items = cursor.fetchall()
    conn.close()
    return items

def update_item_status(item_id: int, new_status: str, updated_at: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE action_items SET status = ?, last_updated_at = ? WHERE id = ?",
        (new_status, updated_at, item_id)
    )
    conn.commit()
    conn.close()
