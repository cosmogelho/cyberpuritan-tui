# app/models/piety.py
import sqlite3
from datetime import date, timedelta
# Importa a nova função de conexão
from app.core.database import conectar_dados_pessoais
from app.core.theme import console

class PiedadeManager:
    """Gerencia o registro e a análise dos dados de piedade usando o banco de dados SQLite."""

    def registrar_dia(self, data_str: str, dados: dict):
        """Salva ou atualiza os dados de um dia específico no banco de dados."""
        conn = conectar_dados_pessoais()
        if not conn:
            return

        consistencia = dados.get('consistencia', {})
        qualitativo = dados.get('qualitativo', {})

        # Usamos INSERT OR REPLACE para inserir ou sobrescrever o registro do dia (já que a data é PRIMARY KEY)
        sql = """
            INSERT OR REPLACE INTO piety 
            (date, leitura_biblica, oracao, catecismo, oracao_qualidade, pecado_atitude)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            data_str,
            int(consistencia.get('leitura_biblica', False)),
            int(consistencia.get('oracao', False)),
            int(consistencia.get('catecismo', False)),
            qualitativo.get('oracao_qualidade'),
            qualitativo.get('pecado_atitude')
        )

        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
        except sqlite3.Error as e:
            console.print(f"[erro]Erro ao registrar o dia no banco de dados: {e}[/erro]")
        finally:
            if conn:
                conn.close()

    def get_registro_dia(self, data_str: str) -> dict | None:
        """Retorna os dados de um dia específico, se existirem, a partir do banco de dados."""
        conn = conectar_dados_pessoais()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM piety WHERE date = ?", (data_str,))
            row = cursor.fetchone()
            if not row:
                return None
            
            # Reconstrói o dicionário no formato que a view espera
            return {
                "consistencia": {
                    "leitura_biblica": bool(row['leitura_biblica']),
                    "oracao": bool(row['oracao']),
                    "catecismo": bool(row['catecismo']),
                },
                "qualitativo": {
                    "oracao_qualidade": row['oracao_qualidade'],
                    "pecado_atitude": row['pecado_atitude'],
                }
            }
        finally:
            if conn:
                conn.close()

    def gerar_analise(self, periodo_dias: int = 30) -> dict | None:
        """Calcula as estatísticas de piedade para um determinado período usando o banco de dados."""
        hoje = date.today()
        data_inicio = hoje - timedelta(days=periodo_dias)

        conn = conectar_dados_pessoais()
        if not conn:
            return None

        try:
            # Consulta SQL para buscar todos os registros no período desejado
            query = "SELECT * FROM piety WHERE date BETWEEN ? AND ?"
            params = (data_inicio.isoformat(), hoje.isoformat())
            cursor = conn.cursor()
            registros_periodo = cursor.execute(query, params).fetchall()

            if not registros_periodo:
                return None

            total_dias = len(registros_periodo)
            analise = {
                'periodo_dias': periodo_dias,
                'total_dias_registrados': total_dias,
                'consistencia': {'leitura_biblica': 0, 'oracao': 0, 'catecismo': 0},
                'qualitativo_oracao': {},
                'qualitativo_pecado': {}
            }

            for row in registros_periodo:
                # Contabiliza consistência
                if row['leitura_biblica']: analise['consistencia']['leitura_biblica'] += 1
                if row['oracao']: analise['consistencia']['oracao'] += 1
                if row['catecismo']: analise['consistencia']['catecismo'] += 1
                
                # Contabiliza qualitativos
                qual_oracao = row.get('oracao_qualidade', 'N/A')
                analise['qualitativo_oracao'][qual_oracao] = analise['qualitativo_oracao'].get(qual_oracao, 0) + 1
                
                qual_pecado = row.get('pecado_atitude', 'N/A')
                analise['qualitativo_pecado'][qual_pecado] = analise['qualitativo_pecado'].get(qual_pecado, 0) + 1

            return analise
        finally:
            if conn:
                conn.close()
