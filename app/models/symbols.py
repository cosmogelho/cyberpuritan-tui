# app/models/symbols.py
from app.core.db import get_data_conn

def obter_simbolo(tipo: str, numero: int, secao: int | None = None) -> list | dict:
    cursor = get_data_conn().cursor()
    
    if tipo == 'cfw':
        query = "SELECT chapter, section, title, text FROM cfw_articles WHERE chapter = ? AND (? IS NULL OR section = ?)"
        params = (numero, secao, secao)
    else:
        # Assumindo que as tabelas se chamam 'cmw' e 'bcw'
        query = f"SELECT id, question, answer FROM {tipo} WHERE id = ?"
        params = (numero,)
        
    resultados = cursor.execute(query, params).fetchall()
    
    if not resultados:
        return {"erro": "Item não encontrado."}
        
    return [dict(row) for row in resultados]
