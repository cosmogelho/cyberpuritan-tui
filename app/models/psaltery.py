# app/models/psaltery.py
from app.core.db import get_data_conn # CORRIGIDO: Importa a função correta

def buscar_versoes_salmo(numero_salmo: str) -> list | dict:
    """Busca no banco de dados todas as versões disponíveis para um salmo."""
    conn = get_data_conn() # CORRIGIDO: Usa a função de conexão correta
    if not conn:
        return {"erro": "Não foi possível conectar ao banco de dados."}
        
    try:
        num_salmo_int = int(numero_salmo)
        cursor = conn.cursor()
        
        query = "SELECT * FROM salterio WHERE CAST(referencia AS INTEGER) = ? ORDER BY referencia"
        
        resultados = cursor.execute(query, (num_salmo_int,)).fetchall()

        if not resultados:
            return {"erro": f"Nenhuma versão encontrada para o Salmo {numero_salmo}."}
            
        return [dict(row) for row in resultados]
    except ValueError:
        return {"erro": f"O número do salmo '{numero_salmo}' é inválido. Por favor, digite apenas números."}
    except Exception as e:
        return {"erro": f"Ocorreu um erro ao buscar o salmo: {e}"}
    # REMOVIDO: O bloco 'finally' que fechava a conexão foi removido.
