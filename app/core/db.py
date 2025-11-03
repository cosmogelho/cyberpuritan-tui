import sqlite3
from app.core.config import DB_PATH

def inicializar_banco():
    """Garante que todas as tabelas necessárias existam."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS diario (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, texto TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS acoes (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pendente', data_criacao TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS resolucoes (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT NOT NULL, data_criacao TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS sermoes (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, tema TEXT, pregador TEXT, local TEXT, data TEXT, link TEXT, passagem_principal TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS notas_estudo (id INTEGER PRIMARY KEY AUTOINCREMENT, referencia_biblica TEXT NOT NULL, texto TEXT NOT NULL, data_criacao TEXT NOT NULL)")
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
