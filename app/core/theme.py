from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "titulo": "bold cyan",
    "subtitulo": "dim white",
    "prompt": "bold green",
    "referencia": "yellow",
    "erro": "bold red",
    "sucesso": "bold green",
    "info": "dim white",
    "painel_borda": "cyan",
    "destaque": "bold magenta",
})

console = Console(theme=custom_theme)
