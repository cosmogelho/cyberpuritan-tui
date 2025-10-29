# app/core/db.py
import sqlite3
from pathlib import Path
from .config import DB_BIBLIA_PATH, DB_DADOS_PATH

class _Singleton:
    """Mantém duas conexões SQLite únicas (uma para a Bíblia, outra para os dados pessoais)."""
    _biblia_conn: sqlite3.Connection | None = None
    _dados_conn: sqlite3.Connection | None = None

    @classmethod
    def bible(cls) -> sqlite3.Connection:
        if cls._biblia_conn is None:
            # str(Path(...)) garante que o caminho funcione em qualquer sistema operacional.
            cls._biblia_conn = sqlite3.connect(str(Path(DB_BIBLIA_PATH)))
            cls._biblia_conn.row_factory = sqlite3.Row
        return cls._biblia_conn

    @classmethod
    def data(cls) -> sqlite3.Connection:
        if cls._dados_conn is None:
            cls._dados_conn = sqlite3.connect(str(Path(DB_DADOS_PATH)))
            cls._dados_conn.row_factory = sqlite3.Row
        return cls._dados_conn

# Exporta nomes curtos e claros para serem usados no resto do programa
def get_bible_conn() -> sqlite3.Connection:
    return _Singleton.bible()

def get_data_conn() -> sqlite3.Connection:
    return _Singleton.data()
