# app/models/piety.py
import sqlite3
from datetime import date, timedelta
from app.core.connections import db_manager
from app.core.theme import console

class PiedadeManager:
    def registrar_dia(self, data_str: str, dados: dict):
        if not db_manager.dados_conn: return
        consistencia = dados.get('consistencia', {})
        qualitativo = dados.get('qualitativo', {})
        sql = """INSERT OR REPLACE INTO piety (date, leitura_biblica, oracao, catecismo, oracao_qualidade, pecado_atitude) VALUES (?, ?, ?, ?, ?, ?)"""
        params = (data_str, int(consistencia.get('leitura_biblica', False)), int(consistencia.get('oracao', False)), int(consistencia.get('catecismo', False)), qualitativo.get('oracao_qualidade'), qualitativo.get('pecado_atitude'))
        try:
            cursor = db_manager.dados_conn.cursor()
            cursor.execute(sql, params)
            db_manager.dados_conn.commit()
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao registrar o dia: {e}[/erro]")
    def get_registro_dia(self, data_str: str) -> dict | None:
        if not db_manager.dados_conn: return None
        cursor = db_manager.dados_conn.cursor()
        cursor.execute("SELECT * FROM piety WHERE date = ?", (data_str,))
        row = cursor.fetchone()
        if not row: return None
        return {
            "consistencia": {"leitura_biblica": bool(row['leitura_biblica']), "oracao": bool(row['oracao']), "catecismo": bool(row['catecismo'])},
            "qualitativo": {"oracao_qualidade": row['oracao_qualidade'], "pecado_atitude": row['pecado_atitude']}
        }
    def gerar_analise(self, periodo_dias: int = 30) -> dict | None:
        if not db_manager.dados_conn: return None
        hoje, data_inicio = date.today(), date.today() - timedelta(days=periodo_dias)
        cursor = db_manager.dados_conn.cursor()
        query = "SELECT * FROM piety WHERE date BETWEEN ? AND ?"
        registros_periodo = cursor.execute(query, (data_inicio.isoformat(), hoje.isoformat())).fetchall()
        if not registros_periodo: return None
        total_dias = len(registros_periodo)
        analise = {'periodo_dias': periodo_dias, 'total_dias_registrados': total_dias, 'consistencia': {'leitura_biblica': 0, 'oracao': 0, 'catecismo': 0}, 'qualitativo_oracao': {}, 'qualitativo_pecado': {}}
        for row in registros_periodo:
            if row['leitura_biblica']: analise['consistencia']['leitura_biblica'] += 1
            if row['oracao']: analise['consistencia']['oracao'] += 1
            if row['catecismo']: analise['consistencia']['catecismo'] += 1
            qual_oracao = row.get('oracao_qualidade', 'N/A')
            analise['qualitativo_oracao'][qual_oracao] = analise['qualitativo_oracao'].get(qual_oracao, 0) + 1
            qual_pecado = row.get('pecado_atitude', 'N/A')
            analise['qualitativo_pecado'][qual_pecado] = analise['qualitativo_pecado'].get(qual_pecado, 0) + 1
        return analise
