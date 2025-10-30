# app/core/db.py
import sqlite3

# O caminho para o banco de dados de dados do usuário.
DB_PATH = 'data/dados.db'

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados principal (dados.db).
    Levanta um erro se a conexão falhar.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Isso permite acessar colunas pelo nome
    return conn

# Se você precisar de uma conexão separada para a Bíblia em algum ponto:
BIBLE_DB_PATH = 'data/Biblia.sqlite'

def get_bible_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados da Bíblia.
    """
    conn = sqlite3.connect(BIBLE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
