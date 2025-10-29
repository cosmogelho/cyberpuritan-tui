# app/models/sermon.py
import sqlite3
from datetime import datetime
from app.core.database import conectar_dados_pessoais
from app.core.theme import console

class SermonManager:
    """Gerencia todas as operações de dados relacionadas a sermões, usando SQLite."""

    def add_sermon(self, dados_sermon: dict) -> str | None:
        """Adiciona um novo sermão ao banco de dados e retorna seu ID."""
        conn = conectar_dados_pessoais()
        if not conn: return None

        sql = """
            INSERT INTO sermons (
                titulo, pregador, data, passagem_principal, outras_passagens,
                tema, anotacoes, aplicacoes, is_church
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            dados_sermon.get('titulo'),
            dados_sermon.get('pregador'),
            dados_sermon.get('data'),
            dados_sermon.get('passagem_principal'),
            dados_sermon.get('outras_passagens'),
            dados_sermon.get('tema'),
            dados_sermon.get('anotacoes'),
            dados_sermon.get('aplicacoes'),
            int(dados_sermon.get('is_church', False))
        )
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return str(cursor.lastrowid)
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao adicionar sermão: {e}[/erro]")
            return None
        finally:
            if conn: conn.close()

    def get_all_sermoes(self) -> list[tuple[str, dict]]:
        """Retorna uma lista de tuplas (id, dados) de todos os sermões, ordenados por data."""
        conn = conectar_dados_pessoais()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM sermons ORDER BY data DESC").fetchall()
            # Converte o resultado para o formato que a view espera: (id, dict_de_dados)
            return [(str(row['id']), dict(row)) for row in rows]
        finally:
            if conn: conn.close()

    def get_sermon_by_id(self, sermon_id: str) -> dict | None:
        """Busca um sermão completo pelo seu ID."""
        conn = conectar_dados_pessoais()
        if not conn: return None
        
        try:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM sermons WHERE id = ?", (int(sermon_id),)).fetchone()
            return dict(row) if row else None
        finally:
            if conn: conn.close()
