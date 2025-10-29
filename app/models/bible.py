# app/models/bible.py
from app.core.db import get_bible_conn, get_data_conn
from app.core.config import MAPA_ABREVIACOES, LIVROS_E_ABREVIACOES

def _normalizar_nome_livro(nome_input: str) -> str | None:
    # Remove espaços e acentos para uma busca mais flexível
    input_lower = nome_input.lower().replace(" ", "")
    
    # 1. Tenta encontrar pela abreviação (mais rápido)
    if input_lower in MAPA_ABREVIACOES:
        return MAPA_ABREVIACOES[input_lower]
        
    # 2. Se não for abreviação, procura pelo nome completo
    for nome_canonico, _ in LIVROS_E_ABREVIACOES:
        # AQUI ESTÁ A CORREÇÃO: removemos o espaço do nome canônico também
        if nome_canonico.lower().replace(" ", "") == input_lower:
            return nome_canonico
            
    return None # Retorna None se não encontrar de jeito nenhum

def _get_cross_references(book: str, chapter: int, verse: int) -> list:
    cursor = get_data_conn().cursor()
    sql = """
        SELECT cr.titulo, cr.author, vr.record_id
        FROM verse_references vr
        JOIN church_records cr ON vr.record_id = cr.id
        WHERE vr.book = ? AND vr.chapter = ? AND vr.verse = ?
    """
    rows = cursor.execute(sql, (book, chapter, verse)).fetchall()
    return [dict(row) for row in rows]

def obter_passagem(versao: str, livro: str, capitulo: int, versiculo: int | None = None) -> dict:
    cursor = get_bible_conn().cursor()
    nome_canonico = _normalizar_nome_livro(livro)
    if not nome_canonico:
        return {"erro": f"Livro '{livro}' não encontrado."}

    cursor.execute("SELECT id FROM book WHERE name = ?", (nome_canonico,))
    resultado_livro = cursor.fetchone()
    if not resultado_livro:
        return {"erro": f"ID do livro '{nome_canonico}' não encontrado na base da Bíblia."}

    livro_id = resultado_livro['id']
    ref_str = f"{nome_canonico} {capitulo}"
    versao_upper = versao.upper()

    if versiculo:
        ref_str += f":{versiculo}"
        query = "SELECT verse, text FROM verse WHERE book_id = ? AND chapter = ? AND verse = ? AND version = ?"
        params = (livro_id, capitulo, versiculo, versao_upper)
    else:
        query = "SELECT verse, text FROM verse WHERE book_id = ? AND chapter = ? AND version = ? ORDER BY verse"
        params = (livro_id, capitulo, versao_upper)

    resultados = cursor.execute(query, params).fetchall()
    if not resultados:
        return {"erro": f"Passagem não encontrada: {ref_str} ({versao_upper})"}

    cross_references = []
    if versiculo:
        cross_references = _get_cross_references(nome_canonico, capitulo, versiculo)

    return {
        "referencia": ref_str,
        "versao": versao_upper,
        "versiculos": [{"numero": r['verse'], "texto": r['text']} for r in resultados],
        "cross_references": cross_references
    }
