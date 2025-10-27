# app/models/sermon.py
import json
from datetime import datetime
from app.core.config import SERMONARIO_FILE_PATH

class SermonManager:
    """Gerencia todas as operações de dados relacionadas a sermões."""
    def __init__(self):
        self.filepath = SERMONARIO_FILE_PATH
        self.sermoes = self._carregar_sermoes()

    def _carregar_sermoes(self) -> dict:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _salvar_sermoes(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.sermoes, f, indent=4, ensure_ascii=False, sort_keys=True)

    def _proximo_id(self) -> str:
        ids_numericos = [int(k) for k in self.sermoes.keys() if k.isdigit()]
        return str(max(ids_numericos + [0]) + 1)

    def add_sermon(self, dados_sermon: dict) -> str:
        """Adiciona um novo sermão e retorna seu ID."""
        novo_id = self._proximo_id()
        self.sermoes[novo_id] = {
            **dados_sermon,
            'adicionado_em': datetime.now().isoformat()
        }
        self._salvar_sermoes()
        return novo_id

    def get_all_sermoes(self) -> list[tuple[str, dict]]:
        """Retorna uma lista de tuplas (id, dados) de todos os sermões, ordenados por data."""
        if not self.sermoes:
            return []
        
        # Ordena os itens do dicionário pela chave 'data' em ordem decrescente
        return sorted(
            self.sermoes.items(),
            key=lambda item: item[1].get('data', '1900-01-01'),
            reverse=True
        )

    def get_sermon_by_id(self, sermon_id: str) -> dict | None:
        return self.sermoes.get(sermon_id)
