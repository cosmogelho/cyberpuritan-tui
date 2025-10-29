# app/models/psaltery.py
# A única mudança é a função de conexão importada e usada
from app.core.database import conectar_dados_pessoais

def buscar_versoes_salmo(numero_salmo: str) -> list | dict:
    """Busca no banco de dados todas as versões disponíveis para um salmo."""
    # Alterado de conectar_estudo() para conectar_dados_pessoais()
    conn = conectar_dados_pessoais()
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
    finally:
        if conn:
            conn.close()
