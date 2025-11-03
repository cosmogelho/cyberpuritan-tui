import subprocess
import shutil
from datetime import datetime
import sqlite3
from app.core.db import get_db_connection
from app.core.config import DB_PATH, AUDIO_PATH

ITENS_POR_PAGINA_SALTERIO = 15
ITENS_POR_PAGINA_DIARIO = 5
ITENS_POR_PAGINA_CATECISMO = 15

# ... (funções listar_salmos e tocar_audio_salmo permanecem as mesmas)
def listar_salmos(pagina=1):
    offset = (pagina - 1) * ITENS_POR_PAGINA_SALTERIO
    conn = get_db_connection()
    query = "SELECT referencia, melodia, tema FROM salterio ORDER BY id LIMIT ? OFFSET ?"
    salmos_pagina = conn.execute(query, (ITENS_POR_PAGINA_SALTERIO, offset)).fetchall()
    total_itens = conn.execute("SELECT COUNT(*) FROM salterio").fetchone()[0]
    conn.close()
    total_paginas = (total_itens + ITENS_POR_PAGINA_SALTERIO - 1) // ITENS_POR_PAGINA_SALTERIO
    return {"salmos": salmos_pagina, "total_paginas": total_paginas, "pagina_atual": pagina}

def tocar_audio_salmo(referencia, tipo_audio='instrumental'):
    if not shutil.which("mpv"): return None, "Player 'mpv' não encontrado."
    coluna = "instrumental" if tipo_audio == 'instrumental' else "à_capela"
    conn = get_db_connection()
    resultado = conn.execute(f"SELECT {coluna} FROM salterio WHERE lower(referencia) = ?", (referencia.lower(),)).fetchone()
    conn.close()
    if not resultado or not resultado[coluna]: return None, f"Áudio para '{referencia}' não encontrado."
    caminho_completo = AUDIO_PATH / resultado[coluna]
    if not caminho_completo.exists(): return None, f"Arquivo não encontrado: {resultado[coluna]}"
    processo = subprocess.Popen(["mpv", "--no-video", "--really-quiet", str(caminho_completo)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return processo, f"Tocando {resultado[coluna]}"

# ... (funções do Diário permanecem as mesmas)
def salvar_entrada_diario(texto):
    conn = sqlite3.connect(DB_PATH)
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO diario (data, texto) VALUES (?, ?)", (data_atual, texto))
    conn.commit()
    conn.close()
    return "Entrada do diário salva com sucesso."

def listar_entradas_diario(pagina=1):
    offset = (pagina - 1) * ITENS_POR_PAGINA_DIARIO
    conn = get_db_connection()
    query = "SELECT data, texto FROM diario ORDER BY data DESC LIMIT ? OFFSET ?"
    entradas = conn.execute(query, (ITENS_POR_PAGINA_DIARIO, offset)).fetchall()
    total_itens = conn.execute("SELECT COUNT(*) FROM diario").fetchone()[0]
    conn.close()
    total_paginas = (total_itens + ITENS_POR_PAGINA_DIARIO - 1) // ITENS_POR_PAGINA_DIARIO
    return {"entradas": entradas, "total_paginas": total_paginas, "pagina_atual": pagina}

# --- Funções dos Símbolos (Expandidas) ---
def listar_capitulos_cfw():
    conn = get_db_connection()
    capitulos = conn.execute("SELECT DISTINCT chapter, title FROM cfw ORDER BY chapter").fetchall()
    conn.close()
    return {"capitulos": capitulos}

def ler_capitulo_cfw(numero_capitulo):
    conn = get_db_connection()
    secoes = conn.execute("SELECT section, text, title FROM cfw WHERE chapter = ? ORDER BY section", (numero_capitulo,)).fetchall()
    conn.close()
    return {"numero": numero_capitulo, "titulo": secoes[0]['title'], "secoes": secoes} if secoes else None

def buscar_provas_cfw(capitulo, secao):
    conn = get_db_connection()
    location = f"{capitulo}.{secao}"
    query = """
        SELECT b.name, pt.chapter, pt.verse, v.text
        FROM texts t JOIN proof_texts pt ON t.id = pt.text_id
        JOIN verse v ON pt.book_id = v.book_id AND pt.chapter = v.chapter AND pt.verse = v.verse
        JOIN book b ON pt.book_id = b.id
        WHERE t.document = 'CFW' AND t.location = ? AND v.version = 'NVI'
    """
    provas = conn.execute(query, (location,)).fetchall()
    conn.close()
    return {"location": location, "provas": provas} if provas else None

def _listar_perguntas_catecismo(tabela, pagina):
    """Função auxiliar para listar perguntas do CMW ou BCW."""
    offset = (pagina - 1) * ITENS_POR_PAGINA_CATECISMO
    conn = get_db_connection()
    query = f"SELECT id, question FROM {tabela} ORDER BY id LIMIT ? OFFSET ?"
    perguntas = conn.execute(query, (ITENS_POR_PAGINA_CATECISMO, offset)).fetchall()
    total_itens = conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    conn.close()
    total_paginas = (total_itens + ITENS_POR_PAGINA_CATECISMO - 1) // ITENS_POR_PAGINA_CATECISMO
    return {"perguntas": perguntas, "total_paginas": total_paginas, "pagina_atual": pagina}

def listar_perguntas_cmw(pagina=1):
    return _listar_perguntas_catecismo("cmw", pagina)

def listar_perguntas_bcw(pagina=1):
    return _listar_perguntas_catecismo("bcw", pagina)

def _ler_pergunta_catecismo(tabela, id):
    """Função auxiliar para ler uma pergunta/resposta do CMW ou BCW."""
    conn = get_db_connection()
    resultado = conn.execute(f"SELECT question, answer FROM {tabela} WHERE id = ?", (id,)).fetchone()
    conn.close()
    return {"id": id, "pergunta": resultado['question'], "resposta": resultado['answer']} if resultado else None

def ler_pergunta_cmw(id):
    return _ler_pergunta_catecismo("cmw", id)

def ler_pergunta_bcw(id):
    return _ler_pergunta_catecismo("bcw", id)

# --- Funções das Ações de Santificação ---

def listar_acoes():
    """Busca todas as ações, ordenadas por status e data."""
    conn = get_db_connection()
    query = "SELECT id, descricao, status FROM acoes ORDER BY status, data_criacao DESC"
    acoes = conn.execute(query).fetchall()
    conn.close()
    return {"acoes": acoes}

def criar_acao(descricao):
    """Cria uma nova ação de santificação."""
    conn = get_db_connection()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO acoes (descricao, data_criacao) VALUES (?, ?)",
        (descricao, data_atual)
    )
    conn.commit()
    conn.close()
    return f"Ação criada: '{descricao[:30]}...'"

def atualizar_status_acao(id, novo_status):
    """Atualiza o status de uma ação para 'completo' ou 'pendente'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE acoes SET status = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    if rows_affected > 0:
        return f"Ação {id} marcada como '{novo_status}'."
    return f"Ação {id} não encontrada."

def deletar_acao(id):
    """Remove uma ação do banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM acoes WHERE id = ?", (id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    if rows_affected > 0:
        return f"Ação {id} deletada."
    return f"Ação {id} não encontrada."

def listar_resolucoes():
    """Busca todas as resoluções, ordenadas por ID."""
    conn = get_db_connection()
    query = "SELECT id, texto FROM resolucoes ORDER BY id"
    resolucoes = conn.execute(query).fetchall()
    conn.close()
    return {"resolucoes": resolucoes}

def criar_resolucao(texto):
    """Cria uma nova resolução."""
    conn = get_db_connection()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO resolucoes (texto, data_criacao) VALUES (?, ?)",
        (texto, data_atual)
    )
    conn.commit()
    conn.close()
    return "Resolução salva."

def deletar_resolucao(id):
    """Remove uma resolução do banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resolucoes WHERE id = ?", (id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return f"Resolução {id} deletada." if rows_affected > 0 else f"Resolução {id} não encontrada."

# --- Funções da Bíblia ---

def ler_capitulo_biblia(nome_livro, capitulo):
    """Busca todos os versículos de um capítulo específico da Bíblia."""
    conn = get_db_connection()
    
    # Encontra o ID do livro (case-insensitive)
    livro_row = conn.execute("SELECT id, name FROM book WHERE lower(name) = ?", (nome_livro.lower(),)).fetchone()
    if not livro_row:
        conn.close()
        return None, f"Livro '{nome_livro}' não encontrado."

    book_id = livro_row['id']
    nome_livro_canonico = livro_row['name']

    # Busca os versículos
    query = "SELECT verse, text FROM verse WHERE book_id = ? AND chapter = ? AND version = 'NVI' ORDER BY verse"
    versiculos = conn.execute(query, (book_id, capitulo)).fetchall()
    conn.close()

    if not versiculos:
        return None, f"Capítulo {capitulo} não encontrado em {nome_livro_canonico}."

    return {
        "livro": nome_livro_canonico,
        "capitulo": capitulo,
        "versiculos": versiculos
    }, None

# --- Funções do Autoexame Noturno ---

PERGUNTAS_EXAME = [
    "Quais pecados cometi hoje em pensamento, palavra e obra?",
    "Que deveres negligenciei?",
    "Como pequei contra a luz do conhecimento e da consciência?",
    "Quais misericórdias recebi e quão grato fui por elas?",
    "Que tentações enfrentei e como lhes resisti ou cedi?",
    "Como guardei meu coração hoje?",
]

def formatar_resultado_exame(respostas):
    """Formata as perguntas e respostas do exame para salvar no diário."""
    data_str = datetime.now().strftime("%Y-%m-%d")
    texto_formatado = f"**AUTOEXAME NOTURNO - {data_str}**\n"
    
    for i, pergunta in enumerate(PERGUNTAS_EXAME):
        resposta = respostas.get(i, "(sem resposta)")
        texto_formatado += f"\n[bold]{i+1}. {pergunta}[/bold]\n> {resposta}\n"
        
    return texto_formatado.strip()

# --- Funções da Vigília Sabática ---

PASSOS_VIGILIA = [
    "Faça um balanço da semana que passou. Quais foram as principais misericórdias de Deus e suas maiores falhas?",
    "Ore pelo culto de amanhã. Interceda por seu pastor, pelos oficiais e pelos membros da igreja.",
    "Medite no Salmo 122. O que significa para você 'alegrar-se quando lhe disseram: Vamos à casa do Senhor'?",
]

def formatar_resultado_vigilia(respostas):
    """Formata os passos da vigília e as respostas para salvar no diário."""
    data_str = datetime.now().strftime("%Y-%m-%d")
    texto_formatado = f"**VIGÍLIA SABÁTICA - {data_str}**\n"
    
    for i, passo in enumerate(PASSOS_VIGILIA):
        resposta = respostas.get(i, "(sem anotação)")
        texto_formatado += f"\n[bold]{i+1}. {passo}[/bold]\n> {resposta}\n"
        
    return texto_formatado.strip()

# --- Funções do Arquivo de Sermões ---

ITENS_POR_PAGINA_SERMOES = 10

def listar_sermoes(pagina=1):
    """Busca uma lista paginada de sermões arquivados."""
    offset = (pagina - 1) * ITENS_POR_PAGINA_SERMOES
    conn = get_db_connection()
    query = "SELECT id, titulo, pregador, passagem_principal FROM sermoes ORDER BY data DESC LIMIT ? OFFSET ?"
    sermoes = conn.execute(query, (ITENS_POR_PAGINA_SERMOES, offset)).fetchall()
    total_itens = conn.execute("SELECT COUNT(*) FROM sermoes").fetchone()[0]
    conn.close()
    
    total_paginas = (total_itens + ITENS_POR_PAGINA_SERMOES - 1) // ITENS_POR_PAGINA_SERMOES
    
    return {
        "sermoes": sermoes,
        "total_paginas": total_paginas if total_paginas > 0 else 1,
        "pagina_atual": pagina
    }

def ver_sermao(id):
    """Busca todos os detalhes de um sermão específico."""
    conn = get_db_connection()
    query = "SELECT * FROM sermoes WHERE id = ?"
    sermao = conn.execute(query, (id,)).fetchone()
    conn.close()
    return sermao # Retorna o objeto Row ou None

def adicionar_sermao(dados_sermao):
    """Adiciona um novo sermão ao banco de dados."""
    conn = get_db_connection()
    query = """
        INSERT INTO sermoes (titulo, tema, pregador, local, data, link, passagem_principal)
        VALUES (:titulo, :tema, :pregador, :local, :data, :link, :passagem_principal)
    """
    conn.execute(query, dados_sermao)
    conn.commit()
    conn.close()
    return "Sermão arquivado com sucesso."

# --- Funções das Notas de Estudo ---

def listar_notas_por_referencia(referencia_capitulo):
    """Busca todas as notas para um capítulo específico (ex: 'genesis 1')."""
    conn = get_db_connection()
    # Usa LIKE para pegar notas de versos específicos dentro do capítulo
    query = "SELECT id, referencia_biblica, texto FROM notas_estudo WHERE referencia_biblica LIKE ? ORDER BY id"
    notas = conn.execute(query, (f"{referencia_capitulo}%",)).fetchall()
    conn.close()
    return notas # Retorna uma lista de Rows

def criar_nota_estudo(referencia, texto):
    """Cria uma nova nota de estudo."""
    conn = get_db_connection()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO notas_estudo (referencia_biblica, texto, data_criacao) VALUES (?, ?, ?)",
        (referencia, texto, data_atual)
    )
    conn.commit()
    conn.close()
    return f"Nota salva para '{referencia}'."

def deletar_nota_estudo(id):
    """Remove uma nota de estudo do banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notas_estudo WHERE id = ?", (id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return f"Nota {id} deletada." if rows_affected > 0 else f"Nota {id} não encontrada."
