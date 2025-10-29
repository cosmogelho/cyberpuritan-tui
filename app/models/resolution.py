# app/models/resolution.py
from datetime import datetime
from app.core.connections import db_manager
from app.core.data_models import Resolution

class ResolutionManager:
    def add_resolution(self, text: str, category: str) -> str | None:
        if not db_manager.dados_conn: return None
        now, sql = datetime.now().isoformat(), "INSERT INTO resolutions (text, category, created_at, review_count) VALUES (?, ?, ?, 0)"
        cursor = db_manager.dados_conn.cursor()
        cursor.execute(sql, (text, category, now))
        db_manager.dados_conn.commit()
        return str(cursor.lastrowid)
    def get_all_resolutions(self) -> list[Resolution]:
        if not db_manager.dados_conn: return []
        cursor = db_manager.dados_conn.cursor()
        rows = cursor.execute("SELECT * FROM resolutions ORDER BY id").fetchall()
        return [Resolution(**row) for row in rows]
    def update_review_stats(self, res_id: str):
        if not db_manager.dados_conn: return
        now, sql = datetime.now().isoformat(), "UPDATE resolutions SET review_count = review_count + 1, last_reviewed_at = ? WHERE id = ?"
        cursor = db_manager.dados_conn.cursor()
        cursor.execute(sql, (now, int(res_id)))
        db_manager.dados_conn.commit()
    def _get_one_resolution(self, query: str) -> Resolution | None:
        if not db_manager.dados_conn: return None
        cursor = db_manager.dados_conn.cursor()
        row = cursor.execute(query).fetchone()
        return Resolution(**row) if row else None
    def get_random_resolution(self) -> Resolution | None:
        return self._get_one_resolution("SELECT * FROM resolutions ORDER BY RANDOM() LIMIT 1")
    def get_least_reviewed_resolution(self) -> Resolution | None:
        return self._get_one_resolution("SELECT * FROM resolutions ORDER BY review_count ASC, last_reviewed_at ASC NULLS FIRST LIMIT 1")
