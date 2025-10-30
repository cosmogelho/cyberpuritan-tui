# app/models/journal_model.py
import sqlite3
from app.core.db import get_db_connection

def add_entry(entry_date: str, content: str, tags: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO journal (entry_date, content, tags) VALUES (?, ?, ?)",
        (entry_date, content, tags)
    )
    conn.commit()
    conn.close()

def get_entries_by_tag(tag: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM journal WHERE tags LIKE ? ORDER BY entry_date DESC", (f'%{tag}%',))
    entries = cursor.fetchall()
    conn.close()
    return entries

def get_all_entries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM journal ORDER BY entry_date DESC")
    entries = cursor.fetchall()
    conn.close()
    return entries
