# app/models/piety.py
import json
from datetime import date, timedelta
from app.core.config import PIEDADE_METRICAS_FILE_PATH

class PiedadeManager:
    """Gerencia o registro e a análise dos dados de piedade."""
    def __init__(self):
        self.filepath = PIEDADE_METRICAS_FILE_PATH
        self.registros = self._carregar_registros()

    def _carregar_registros(self) -> dict:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _salvar_registros(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.registros, f, indent=4, ensure_ascii=False, sort_keys=True)

    def registrar_dia(self, data_str: str, dados: dict):
        """Salva ou atualiza os dados de um dia específico."""
        self.registros[data_str] = dados
        self._salvar_registros()

    def get_registro_dia(self, data_str: str) -> dict | None:
        """Retorna os dados de um dia específico, se existirem."""
        return self.registros.get(data_str)

    def gerar_analise(self, periodo_dias: int = 30) -> dict | None:
        """Calcula as estatísticas de piedade para um determinado período."""
        hoje = date.today()
        data_inicio = hoje - timedelta(days=periodo_dias)
        
        registros_periodo = {
            data: dados for data, dados in self.registros.items()
            if data_inicio <= date.fromisoformat(data) <= hoje
        }
        
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

        for dados in registros_periodo.values():
            # Contabiliza consistência (booleano)
            for metrica, valor in dados.get('consistencia', {}).items():
                if valor:
                    analise['consistencia'][metrica] += 1
            
            # Contabiliza qualitativos (strings)
            qual_oracao = dados.get('qualitativo', {}).get('oracao_qualidade', 'N/A')
            analise['qualitativo_oracao'][qual_oracao] = analise['qualitativo_oracao'].get(qual_oracao, 0) + 1
            
            qual_pecado = dados.get('qualitativo', {}).get('pecado_atitude', 'N/A')
            analise['qualitativo_pecado'][qual_pecado] = analise['qualitativo_pecado'].get(qual_pecado, 0) + 1

        return analise
