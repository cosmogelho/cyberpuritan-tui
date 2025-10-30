# app/models/psaltery.py
from app.core.db import get_db_connection

def get_psalm_by_id(psalm_id: int):
    """Busca um salmo pelo seu número/ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM salterio WHERE id = ?", (psalm_id,))
    psalm = cursor.fetchone()
    conn.close()
    return psalm

def get_all_psalms_references():
    """Retorna uma lista de todas as referências de salmos para consulta."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, referencia, metrica, melodia FROM salterio ORDER BY id")
    references = cursor.fetchall()
    conn.close()
    return references
