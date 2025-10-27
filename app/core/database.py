import sqlite3
import os
from .config import DATA_DIR, DB_ESTUDO_PATH
from .theme import console

def _criar_conexao(db_path: str) -> sqlite3.Connection | None:
    """Cria e retorna uma conexão com um banco de dados SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        console.print(f"[erro]ERRO: Não foi possível conectar ao banco de dados em '{db_path}'.[/erro]")
        console.print(f"[info]Detalhes: {e}[/info]")
        return None

def conectar_estudo() -> sqlite3.Connection | None:
    """Conecta ao banco de dados de estudo."""
    return _criar_conexao(DB_ESTUDO_PATH)

def conectar_biblia(versao: str) -> sqlite3.Connection | None:
    """Conecta a um banco de dados da Bíblia específico."""
    db_file = f"{versao.upper()}.sqlite"
    db_path = os.path.join(DATA_DIR, db_file)
    if not os.path.exists(db_path):
        console.print(f"[erro]ERRO: Arquivo da Bíblia '{db_file}' não encontrado.[/erro]")
        return None
    return _criar_conexao(db_path)
