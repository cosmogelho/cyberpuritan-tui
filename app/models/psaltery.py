# app/models/psaltery.py
from app.core.db import get_db_connection

def get_psalm_by_reference(reference: str):
    """
    Busca um salmo pela sua referência exata (ex: '1A', '23', '99C').
    Esta é a forma mais precisa de buscar.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Seleciona todas as colunas para garantir que todos os dados estejam disponíveis
    cursor.execute("SELECT * FROM salterio WHERE referencia = ?", (reference,))
    psalm = cursor.fetchone()
    conn.close()
    return psalm

def get_all_psalms_references():
    """Retorna uma lista de todas as referências de salmos para consulta."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # (CORRIGIDO) Seleciona todas as colunas para ter acesso aos campos de áudio.
    cursor.execute("SELECT * FROM salterio ORDER BY id")
    references = cursor.fetchall()
    conn.close()
    return references
