# app/models/psaltery.py
from app.core.db import get_db_connection

def get_psalm_by_reference(reference: str):
    """
    Busca um salmo pela sua referência exata (ex: '1A', '23', '99C').
    Esta é a forma mais precisa de buscar.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Usamos a coluna 'referencia' que contém valores como '15A', '15B', etc.
    cursor.execute("SELECT * FROM salterio WHERE referencia = ?", (reference,))
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
