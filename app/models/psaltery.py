# app/models/psaltery.py
from app.core.database import conectar_estudo

def buscar_versoes_salmo(numero_salmo: str) -> list | dict:
    """Busca no banco de dados todas as versões disponíveis para um salmo."""
    conn = conectar_estudo()
    if not conn:
        return {"erro": "Não foi possível conectar ao banco de dados de estudo."}
        
    try:
        # Garante que estamos comparando um número inteiro
        num_salmo_int = int(numero_salmo)
        cursor = conn.cursor()
        
        # --- ESTRATÉGIA CORRIGIDA E EFICIENTE ---
        # Usamos CAST para converter a parte inicial da coluna de texto 'referencia'
        # para um número inteiro. Assim, '10' se torna o número 10, e '1A' se
        # torna o número 1. A comparação é feita numericamente, que é o correto.
        query = "SELECT * FROM salterio WHERE CAST(referencia AS INTEGER) = ? ORDER BY referencia"
        
        resultados = cursor.execute(query, (num_salmo_int,)).fetchall()
        # --- FIM DA MUDANÇA ---

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
