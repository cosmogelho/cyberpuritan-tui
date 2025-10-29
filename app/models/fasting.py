# app/models/fasting.py
from datetime import datetime
from app.core.connections import db_manager

class FastingManager:
    def start_fast(self, purpose: str, scripture: str) -> int | None:
        if not db_manager.dados_conn: return None
        cursor = db_manager.dados_conn.cursor()
        sql = "INSERT INTO fasting_logs (start_date, purpose, scripture_focus, status) VALUES (?, ?, ?, 'ativo')"
        cursor.execute(sql, (datetime.now().isoformat(), purpose, scripture))
        db_manager.dados_conn.commit()
        return cursor.lastrowid

    def get_active_fast(self) -> dict | None:
        if not db_manager.dados_conn: return None
        # A linha abaixo é a que foi corrigida (não tem mais a duplicata)
        cursor = db_manager.dados_conn.cursor()
        row = cursor.execute("SELECT * FROM fasting_logs WHERE status = 'ativo' ORDER BY start_date DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def finish_fast(self, fast_id: int, reflection: str):
        if not db_manager.dados_conn: return
        # A linha abaixo é a que foi corrigida
        cursor = db_manager.dados_conn.cursor()
        sql = "UPDATE fasting_logs SET end_date = ?, reflection = ?, status = 'concluido' WHERE id = ?"
        cursor.execute(sql, (datetime.now().isoformat(), reflection, fast_id))
        db_manager.dados_conn.commit()
