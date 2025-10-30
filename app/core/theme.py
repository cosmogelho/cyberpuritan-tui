# app/core/theme.py
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "erro": "bold red",
    "titulo": "bold cyan",
    "prompt": "bold green",
    "ref": "italic yellow"
})

console = Console(theme=custom_theme)
