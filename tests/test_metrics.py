# tests/test_metrics.py
import os
import sys

# Adiciona o diretório raiz do projeto ao path para que possamos importar de 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.reports import metrics

def test_piety_summary_runs_and_returns_dict():
    """
    Verifica se a função de resumo de piedade executa sem erros
    e retorna um dicionário (ou None se não houver dados).
    """
    summary = metrics.get_piety_summary()
    
    # Se houver dados, o resultado deve ser um dicionário.
    # Se não houver, deve ser None. O teste aceita ambos.
    assert isinstance(summary, dict) or summary is None
    
    # Se for um dicionário, verifica se contém as chaves esperadas.
    if isinstance(summary, dict):
        assert "periodo_dias" in summary
        assert "consistencia" in summary
        assert "Leitura Bíblica" in summary["consistencia"]

def test_resolution_summary_runs_and_returns_dict():
    """
    Verifica se a função de resumo de resoluções executa sem erros
    e retorna um dicionário (ou None se não houver dados).
    """
    summary = metrics.get_resolution_summary()
    
    assert isinstance(summary, dict) or summary is None

    if isinstance(summary, dict):
        assert "total_resolucoes" in summary
        assert "media_revisoes" in summary
        assert "dist_categorias" in summary
