# app/core/connections.py
import sqlite3
from .config import DB_DADOS_PATH, DB_BIBLIA_PATH

class ConnectionManager:
    def __init__(self):
        self.dados_conn = None
        self.biblia_conn = None

    def start(self):
        try:
            self.dados_conn = sqlite3.connect(DB_DADOS_PATH)
            self.dados_conn.row_factory = sqlite3.Row
            self.biblia_conn = sqlite3.connect(DB_BIBLIA_PATH)
            self.biblia_conn.row_factory = sqlite3.Row
            print("Conexões com o banco de dados inicializadas.")
        except sqlite3.Error as e:
            print(f"ERRO CRÍTICO AO CONECTAR AO BANCO DE DADOS: {e}")
            self.dados_conn = None
            self.biblia_conn = None
    
    def close(self):
        if self.dados_conn:
            self.dados_conn.close()
        if self.biblia_conn:
            self.biblia_conn.close()
        print("Conexões com o banco de dados fechadas.")

db_manager = ConnectionManager()