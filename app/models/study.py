# app/models/study.py
import sqlite3
from datetime import datetime
# A única mudança é a função de conexão importada e usada
from app.core.database import conectar_dados_pessoais
from app.core.theme import console # Importar o console para padronizar logs de erro

class StudyManager:
    def __init__(self):
        # Alterado de conectar_estudo() para conectar_dados_pessoais()
        self.conn = conectar_dados_pessoais()
        if self.conn:
            self._initialize_db()

    def _initialize_db(self):
        """Garante que a tabela 'notes' exista no banco de dados."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            # Corrigido de print() para console.print para manter o padrão
            console.print(f"[erro]Erro ao inicializar o banco de dados de estudos: {e}[/erro]")

    def add_note(self, title: str, content: str, tags: str) -> int | None:
        """Adiciona uma nova anotação e retorna seu ID."""
        now = datetime.now().isoformat()
        sql = "INSERT INTO notes (title, content, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (title, content, tags, now, now))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao adicionar anotação: {e}[/erro]")
            return None

    def get_all_notes(self) -> list[dict] | None:
        """Retorna uma lista resumida de todas as anotações."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, title, tags, created_at FROM notes ORDER BY updated_at DESC")
            notes = cursor.fetchall()
            return [dict(row) for row in notes]
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao buscar anotações: {e}[/erro]")
            return None

    def get_note_by_id(self, note_id: int) -> dict | None:
        """Busca uma anotação completa pelo seu ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            note = cursor.fetchone()
            return dict(note) if note else None
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao buscar anotação por ID: {e}[/erro]")
            return None

    def __del__(self):
        """Garante que a conexão com o banco de dados seja fechada."""
        if self.conn:
            self.conn.close()
