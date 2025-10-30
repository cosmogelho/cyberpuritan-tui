# app/models/symbols.py
from app.core.db import get_db_connection

def get_cfw_article(chapter: int, section: int):
    """Busca um artigo da Confissão de Fé de Westminster."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cfw_articles WHERE chapter = ? AND section = ?", 
        (chapter, section)
    )
    article = cursor.fetchone()
    conn.close()
    return article

def get_cmw_question(question_id: int):
    """Busca uma pergunta do Catecismo Maior de Westminster."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cmw WHERE id = ?", (question_id,))
    question = cursor.fetchone()
    conn.close()
    return question

def get_bcw_question(question_id: int):
    """Busca uma pergunta do Breve Catecismo de Westminster."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bcw WHERE id = ?", (question_id,))
    question = cursor.fetchone()
    conn.close()
    return question
