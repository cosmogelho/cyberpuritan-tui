# app/models/resolution.py
import sqlite3
from datetime import datetime
from app.core.database import conectar_dados_pessoais
from app.core.theme import console

class ResolutionManager:
    """Gerencia todas as operações de dados relacionadas às resoluções, usando SQLite."""

    def add_resolution(self, text: str, category: str) -> str | None:
        """Adiciona uma nova resolução ao banco de dados."""
        conn = conectar_dados_pessoais()
        if not conn: return None

        now = datetime.now().isoformat()
        sql = """
            INSERT INTO resolutions (text, category, created_at, last_reviewed_at, review_count)
            VALUES (?, ?, ?, NULL, 0)
        """
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (text, category, now))
            conn.commit()
            return str(cursor.lastrowid)
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao adicionar resolução: {e}[/erro]")
            return None
        finally:
            if conn: conn.close()

    def get_all_resolutions(self) -> list[tuple[str, dict]]:
        """Retorna uma lista de tuplas (id, dados) de todas as resoluções."""
        conn = conectar_dados_pessoais()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM resolutions ORDER BY id").fetchall()
            # Converte o resultado para o formato que a view espera: (id, dict_de_dados)
            return [(str(row['id']), dict(row)) for row in rows]
        finally:
            if conn: conn.close()

    def update_review_stats(self, res_id: str):
        """Atualiza os metadados de uma resolução após ela ser revisada."""
        conn = conectar_dados_pessoais()
        if not conn: return

        now = datetime.now().isoformat()
        sql = "UPDATE resolutions SET review_count = review_count + 1, last_reviewed_at = ? WHERE id = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (now, int(res_id)))
            conn.commit()
        finally:
            if conn: conn.close()
    
    def _get_one_resolution(self, query: str) -> tuple[str, dict] | None:
        """Função auxiliar para buscar uma única resolução."""
        conn = conectar_dados_pessoais()
        if not conn: return None

        try:
            cursor = conn.cursor()
            row = cursor.execute(query).fetchone()
            if row:
                return str(row['id']), dict(row)
            return None
        finally:
            if conn: conn.close()

    def get_random_resolution(self) -> tuple[str, dict] | None:
        """Retorna uma tupla (id, dados) de uma resolução aleatória."""
        return self._get_one_resolution("SELECT * FROM resolutions ORDER BY RANDOM() LIMIT 1")

    def get_least_reviewed_resolution(self) -> tuple[str, dict] | None:
        """Encontra e retorna a resolução que foi menos revisada ou a mais antiga."""
        return self._get_one_resolution("SELECT * FROM resolutions ORDER BY review_count ASC, last_reviewed_at ASC NULLS FIRST LIMIT 1")
