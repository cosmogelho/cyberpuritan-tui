# app/models/symbols.py
# A única mudança é a função de conexão importada e usada
from app.core.database import conectar_dados_pessoais

def obter_simbolo(tipo: str, numero: int, secao: int | None = None) -> list | dict:
    """Busca um item de um símbolo de fé no banco de dados."""
    # Alterado de conectar_estudo() para conectar_dados_pessoais()
    conn = conectar_dados_pessoais()
    if not conn:
        return {"erro": "Não foi possível conectar ao banco de dados."}

    try:
        cursor = conn.cursor()
        if tipo == 'cfw': # Confissão de Fé de Westminster
            query = "SELECT chapter, section, title, text FROM cfw_articles WHERE chapter = ? AND (? IS NULL OR section = ?)"
            params = (numero, secao, secao)
        else: # Catecismos (cmw ou bcw)
            query = f"SELECT id, question, answer FROM {tipo} WHERE id = ?"
            params = (numero,)

        resultados = cursor.execute(query, params).fetchall()

        if not resultados:
            return {"erro": "Item não encontrado."}
        
        return [dict(row) for row in resultados]
    finally:
        if conn:
            conn.close()
