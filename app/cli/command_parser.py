# app/cli/command_parser.py
from pathlib import Path

DEFAULT_ALIASES = {
    "b": "biblia", "r": "registros", "res": "resolucoes", "f": "fast",
    "s": "simbolos", "h": "help", "q": "exit", "rel": "relatorios",
    "dom": "domingo"
}

# Em uma futura implementação, você pode carregar aliases de um arquivo de configuração
ALIASES = DEFAULT_ALIASES

def parse(raw: str) -> dict | None:
    """Recebe a linha do usuário e a transforma em um comando e argumentos."""
    raw = raw.strip()
    if not raw:
        return None

    parts = raw.split()
    
    cmd_or_alias = parts[0].lower()
    command = ALIASES.get(cmd_or_alias, cmd_or_alias)

    return {"cmd": command, "args": parts[1:]}
