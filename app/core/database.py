import sqlite3
import os
from .config import DB_DADOS_PATH, DB_BIBLIA_PATH
from .theme import console

def _criar_conexao(db_path: str) -> sqlite3.Connection | None:
    """Cria e retorna uma conexão com um banco de dados SQLite."""
    if not os.path.exists(db_path):
        console.print(f"[erro]ERRO: Arquivo de banco de dados não encontrado em '{db_path}'.[/erro]")
        return None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        console.print(f"[erro]ERRO: Não foi possível conectar ao banco de dados em '{db_path}'.[/erro]")
        console.print(f"[info]Detalhes: {e}[/info]")
        return None

def conectar_dados_pessoais() -> sqlite3.Connection | None:
    """Conecta ao banco de dados com notas, sermões, resoluções, etc."""
    return _criar_conexao(DB_DADOS_PATH)

def conectar_biblia() -> sqlite3.Connection | None:
    """Conecta ao banco de dados unificado da Bíblia."""
    return _criar_conexao(DB_BIBLIA_PATH)
