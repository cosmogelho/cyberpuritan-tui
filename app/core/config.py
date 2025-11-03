from pathlib import Path

# Define o caminho raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Define os caminhos para os dados
DB_PATH = PROJECT_ROOT / "data" / "dados.db"
AUDIO_PATH = PROJECT_ROOT / "data" / "saltério"
