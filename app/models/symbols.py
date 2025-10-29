# app/models/symbols.py
from app.core.connections import db_manager

def obter_simbolo(tipo: str, numero: int, secao: int | None = None) -> list | dict:
    if not db_manager.dados_conn:
        return {"erro": "Não foi possível conectar ao banco de dados."}
    cursor = db_manager.dados_conn.cursor()
    if tipo == 'cfw':
        query = "SELECT chapter, section, title, text FROM cfw_articles WHERE chapter = ? AND (? IS NULL OR section = ?)"
        params = (numero, secao, secao)
    else:
        query = f"SELECT id, question, answer FROM {tipo} WHERE id = ?"
        params = (numero,)
    resultados = cursor.execute(query, params).fetchall()
    if not resultados:
        return {"erro": "Item não encontrado."}
    return [dict(row) for row in resultados]
