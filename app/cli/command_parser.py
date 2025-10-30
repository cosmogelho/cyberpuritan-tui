# app/cli/command_parser.py
DEFAULT_ALIASES = {
    "j": "journal",      # Diário (journal)
    "a": "actions",      # Ações (resoluções e orações)
    "n": "notes",        # Notas (commonplace book)
    "b": "bible",        # Bíblia
    "s": "symbols",      # Símbolos de Fé
    "p": "psaltery",     # Saltério
    "h": "help",
    "q": "exit",
    "cls": "clear"
}

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
