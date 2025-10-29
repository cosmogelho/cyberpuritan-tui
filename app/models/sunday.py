from app.core.connections import db_manager

class SundayManager:
    def log_preparation(self, prep_date: str, checks: dict):
        if not db_manager.dados_conn: return
        sql = """INSERT OR REPLACE INTO sunday_prep_logs (prep_date, pastor_prayer, sermon_reading, confession_prayer, worldliness_aside, congregation_prayer) VALUES (?, ?, ?, ?, ?, ?)"""
        params = (prep_date, int(checks.get('pastor', False)), int(checks.get('leitura', False)), int(checks.get('confissao', False)), int(checks.get('mundo', False)), int(checks.get('congregacao', False)))
        cursor = db_manager.dados_conn.cursor()
        cursor.execute(sql, params)
        db_manager.dados_conn.commit()
