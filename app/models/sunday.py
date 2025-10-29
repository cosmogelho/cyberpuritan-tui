# app/models/sunday.py
from app.core.db import get_data_conn

class SundayManager:
    def log_preparation(self, prep_date: str, checks: dict):
        conn = get_data_conn()
        sql = """INSERT OR REPLACE INTO sunday_prep_logs (prep_date, pastor_prayer, sermon_reading, confession_prayer, worldliness_aside, congregation_prayer) VALUES (?, ?, ?, ?, ?, ?)"""
        params = (
            prep_date, int(checks.get('pastor', False)), int(checks.get('leitura', False)),
            int(checks.get('confissao', False)), int(checks.get('mundo', False)),
            int(checks.get('congregacao', False))
        )
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
