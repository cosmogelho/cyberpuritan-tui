# app/models/fasting.py
from datetime import datetime
from app.core.db import get_data_conn

class FastingManager:
    def start_fast(self, purpose: str, scripture: str) -> int | None:
        conn = get_data_conn()
        cursor = conn.cursor()
        sql = "INSERT INTO fasting_logs (start_date, purpose, scripture_focus, status) VALUES (?, ?, ?, 'ativo')"
        cursor.execute(sql, (datetime.now().isoformat(), purpose, scripture))
        conn.commit()
        return cursor.lastrowid

    def get_active_fast(self) -> dict | None:
        cursor = get_data_conn().cursor()
        row = cursor.execute("SELECT * FROM fasting_logs WHERE status = 'ativo' ORDER BY start_date DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def finish_fast(self, fast_id: int, reflection: str):
        conn = get_data_conn()
        cursor = conn.cursor()
        sql = "UPDATE fasting_logs SET end_date = ?, reflection = ?, status = 'concluido' WHERE id = ?"
        cursor.execute(sql, (datetime.now().isoformat(), reflection, fast_id))
        conn.commit()
