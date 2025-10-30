# app/models/bible.py
from app.core.db import get_bible_db_connection

def get_verses(book_name: str, chapter: int, start_verse: int, end_verse: int = None):
    """
    Busca um ou mais versículos da Bíblia usando o NOME COMPLETO e EXATO do livro.
    Isso garante que não haja buscas ambíguas.
    """
    conn = get_bible_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT b.name AS book_name, v.chapter, v.verse, v.text
    FROM verse v
    JOIN book b ON v.book_id = b.id
    WHERE b.name = ? AND v.chapter = ? AND v.verse >= ?
    """
    params = [book_name, chapter, start_verse]
    
    if end_verse:
        query += " AND v.verse <= ?"
        params.append(end_verse)
        
    query += " ORDER BY v.verse"
    
    cursor.execute(query, tuple(params))
    verses = cursor.fetchall()
    conn.close()
    return verses

def get_all_book_names():
    """Retorna uma lista de todos os livros da Bíblia para consulta."""
    conn = get_bible_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM book ORDER BY id")
    books = cursor.fetchall()
    conn.close()
    return books
