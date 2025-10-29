# app/reports/metrics.py
from datetime import date, timedelta
from app.core.database import conectar_dados_pessoais

def get_piety_summary(periodo_dias: int = 30) -> dict | None:
    """Busca e calcula um resumo de consistência do diário de piedade."""
    hoje = date.today()
    data_inicio = hoje - timedelta(days=periodo_dias)
    conn = conectar_dados_pessoais()
    if not conn: return None

    try:
        cursor = conn.cursor()
        query = """
            SELECT
                COUNT(*) as total_dias,
                AVG(leitura_biblica) as avg_leitura,
                AVG(oracao) as avg_oracao,
                AVG(catecismo) as avg_catecismo
            FROM piety
            WHERE date BETWEEN ? AND ?
        """
        params = (data_inicio.isoformat(), hoje.isoformat())
        summary = cursor.execute(query, params).fetchone()

        if not summary or summary['total_dias'] == 0:
            return None
        
        # Busca as distribuições qualitativas
        oracao_dist = cursor.execute(
            "SELECT oracao_qualidade, COUNT(*) as count FROM piety WHERE date BETWEEN ? AND ? GROUP BY oracao_qualidade",
            params
        ).fetchall()
        
        pecado_dist = cursor.execute(
            "SELECT pecado_atitude, COUNT(*) as count FROM piety WHERE date BETWEEN ? AND ? GROUP BY pecado_atitude",
            params
        ).fetchall()

        return {
            "periodo_dias": periodo_dias,
            "total_dias_registrados": summary['total_dias'],
            "consistencia": {
                "Leitura Bíblica": (summary['avg_leitura'] or 0) * 100,
                "Oração": (summary['avg_oracao'] or 0) * 100,
                "Estudo dos Símbolos": (summary['avg_catecismo'] or 0) * 100,
            },
            "qualitativo_oracao": {row['oracao_qualidade']: row['count'] for row in oracao_dist},
            "qualitativo_pecado": {row['pecado_atitude']: row['count'] for row in pecado_dist},
        }
    finally:
        if conn: conn.close()

def get_resolution_summary() -> dict | None:
    """Busca e calcula um resumo das resoluções pessoais."""
    conn = conectar_dados_pessoais()
    if not conn: return None

    try:
        cursor = conn.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM resolutions").fetchone()[0]
        if total == 0:
            return None

        avg_reviews = cursor.execute("SELECT AVG(review_count) FROM resolutions").fetchone()[0]
        categories = cursor.execute("SELECT category, COUNT(*) as count FROM resolutions GROUP BY category").fetchall()

        return {
            "total_resolucoes": total,
            "media_revisoes": avg_reviews or 0,
            "dist_categorias": {row['category']: row['count'] for row in categories}
        }
    finally:
        if conn: conn.close()
