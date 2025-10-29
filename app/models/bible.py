from app.core.database import conectar_biblia
from app.core.config import MAPA_ABREVIACOES, LIVROS_E_ABREVIACOES

def _normalizar_nome_livro(nome_input: str) -> str | None:
    """Converte uma abreviação ou nome de livro para seu nome canônico."""
    input_lower = nome_input.lower()
    if input_lower in MAPA_ABREVIACOES:
        return MAPA_ABREVIACOES[input_lower]
    for nome_canonico, _ in LIVROS_E_ABREVIACOES:
        if nome_canonico.lower() == input_lower:
            return nome_canonico
    return None

def obter_passagem(versao: str, livro: str, capitulo: int, versiculo: int | None = None) -> dict:
    """Busca um capítulo ou versículo e retorna um dicionário com os dados ou um erro."""
    # A conexão agora é única, sem a versão como parâmetro.
    conn = conectar_biblia()
    if not conn:
        # A mensagem de erro da conexão já é exibida em _criar_conexao
        return {"erro": f"Não foi possível conectar ao banco de dados da Bíblia."}

    try:
        cursor = conn.cursor()
        nome_canonico = _normalizar_nome_livro(livro)
        if not nome_canonico:
            return {"erro": f"Livro '{livro}' não encontrado."}

        # A tabela `book` não contém `version`, então a busca do ID do livro permanece a mesma
        cursor.execute("SELECT id FROM book WHERE name = ?", (nome_canonico,))
        resultado_livro = cursor.fetchone()
        if not resultado_livro:
            return {"erro": f"ID do livro '{nome_canonico}' não encontrado no banco de dados."}
        livro_id = resultado_livro['id']

        ref = f"{nome_canonico} {capitulo}"
        versao_upper = versao.upper()
        
        # A coluna 'version' foi adicionada à consulta
        if versiculo:
            ref += f":{versiculo}"
            query = "SELECT verse, text FROM verse WHERE book_id = ? AND chapter = ? AND verse = ? AND version = ?"
            params = (livro_id, capitulo, versiculo, versao_upper)
        else:
            query = "SELECT verse, text FROM verse WHERE book_id = ? AND chapter = ? AND version = ? ORDER BY verse"
            params = (livro_id, capitulo, versao_upper)

        resultados = cursor.execute(query, params).fetchall()
        if not resultados:
            return {"erro": f"Passagem não encontrada: {ref} ({versao_upper})"}

        return {
            "referencia": ref,
            "versao": versao_upper,
            "versiculos": [{"numero": r['verse'], "texto": r['text']} for r in resultados]
        }
    finally:
        if conn:
            conn.close()
