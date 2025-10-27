# app/models/resolution.py
import json
import random
from datetime import datetime, date
from pathlib import Path

# Configuração de caminhos
APP_DIR = Path(__file__).parent.parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
RESOLUTIONS_FILE_PATH = DATA_DIR / 'resolutions.json'

class ResolutionManager:
    """Gerencia todas as operações de dados relacionadas às resoluções."""

    def __init__(self):
        self.filepath = RESOLUTIONS_FILE_PATH
        self.resolutions = self._carregar_resolucoes()

    def _carregar_resolucoes(self) -> dict:
        """Carrega as resoluções do arquivo JSON."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _salvar_resolucoes(self):
        """Salva o dicionário de resoluções de volta no arquivo JSON."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.resolutions, f, indent=4, ensure_ascii=False, sort_keys=True)

    def _proximo_id(self) -> str:
        """Calcula o próximo ID numérico para uma nova resolução."""
        ids_numericos = [int(k) for k in self.resolutions.keys() if k.isdigit()]
        return str(max(ids_numericos + [0]) + 1)

    def add_resolution(self, text: str, category: str) -> str:
        """Adiciona uma nova resolução ao arquivo."""
        novo_id = self._proximo_id()
        now = datetime.now().isoformat()

        self.resolutions[novo_id] = {
            "text": text,
            "category": category,
            "created_at": now,
            "last_reviewed_at": None,
            "review_count": 0
        }
        self._salvar_resolucoes()
        return novo_id

    def get_all_resolutions(self) -> list[tuple[str, dict]]:
        """Retorna uma lista de tuplas (id, dados) de todas as resoluções."""
        if not self.resolutions:
            return []
        return sorted(self.resolutions.items(), key=lambda item: int(item[0]))

    def update_review_stats(self, res_id: str):
        """Atualiza os metadados de uma resolução após ela ser revisada."""
        if res_id in self.resolutions:
            self.resolutions[res_id]['review_count'] += 1
            self.resolutions[res_id]['last_reviewed_at'] = datetime.now().isoformat()
            self._salvar_resolucoes()

    def get_random_resolution(self) -> tuple[str, dict] | None:
        """Retorna uma tupla (id, dados) de uma resolução aleatória."""
        if not self.resolutions:
            return None
        
        random_id = random.choice(list(self.resolutions.keys()))
        return random_id, self.resolutions[random_id]

    def get_least_reviewed_resolution(self) -> tuple[str, dict] | None:
        """Encontra e retorna a resolução que foi menos revisada ou a mais antiga."""
        if not self.resolutions:
            return None

        def sort_key(item):
            res_id, data = item
            review_count = data.get('review_count', 0)
            
            last_reviewed_str = data.get('last_reviewed_at')
            if last_reviewed_str is None:
                last_reviewed_date = date.min
            else:
                last_reviewed_date = date.fromisoformat(last_reviewed_str.split('T')[0])
                
            return (review_count, last_reviewed_date)

        sorted_resolutions = sorted(self.resolutions.items(), key=sort_key)
        return sorted_resolutions[0]
