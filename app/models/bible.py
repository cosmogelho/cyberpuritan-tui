# app/models/bible.py
from app.core.db import get_bible_db_connection

def get_verses(book: str, chapter: int, start_verse: int, end_verse: int = None):
    """
    Busca um ou mais versículos da Bíblia.
    O nome do livro deve corresponder ao usado no banco de dados.
    """
    conn = get_bible_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT b.name AS book_name, v.chapter, v.verse, v.text
    FROM verse v
    JOIN book b ON v.book_id = b.id
    WHERE b.name LIKE ? AND v.chapter = ? AND v.verse >= ?
    """
    params = [f'%{book}%', chapter, start_verse]
    
    if end_verse:
        query += " AND v.verse <= ?"
        params.append(end_verse)
        
    query += " ORDER BY v.verse"
    
    cursor.execute(query, tuple(params))
    verses = cursor.fetchall()
    conn.close()
    return verses
