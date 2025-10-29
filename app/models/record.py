# app/models/record.py
import sqlite3
from app.core.db import get_data_conn
from app.core.data_models import Record
from app.core.bible_parser import parse_references
from app.core.theme import console

class RecordManager:
    def _link_verses_to_record(self, cursor: sqlite3.Cursor, record_id: int, text_with_refs: str):
        refs = parse_references(text_with_refs)
        if not refs: return
        sql = "INSERT INTO verse_references (book, chapter, verse, record_id) VALUES (?, ?, ?, ?)"
        for ref in refs:
            cursor.execute(sql, (ref['book'], ref['chapter'], ref['verse'], record_id))

    def add_record(self, dados: dict) -> str | None:
        conn = get_data_conn()
        sql = """INSERT INTO church_records (category, titulo, author, context, data, passagem_principal, anotacoes, aplicacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        params = (dados.get('category'), dados.get('titulo'), dados.get('author'), dados.get('context'), dados.get('data'), dados.get('passagem_principal'), dados.get('anotacoes'), dados.get('aplicacoes'))
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            record_id = cursor.lastrowid
            if dados.get('passagem_principal'):
                self._link_verses_to_record(cursor, record_id, dados['passagem_principal'])
            conn.commit()
            return str(record_id)
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao adicionar registro: {e}[/erro]")
            return None

    def get_all_records(self) -> list[Record]:
        cursor = get_data_conn().cursor()
        rows = cursor.execute("SELECT id, category, data, titulo, author FROM church_records ORDER BY data DESC").fetchall()
        return [Record(**row) for row in rows]

    def get_record_by_id(self, record_id: str) -> Record | None:
        cursor = get_data_conn().cursor()
        row = cursor.execute("SELECT * FROM church_records WHERE id = ?", (int(record_id),)).fetchone()
        return Record(**row) if row else None
