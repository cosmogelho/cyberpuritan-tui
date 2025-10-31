# app/handlers/bible_handler.py
import re
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from app.models import bible
from app.core.config import LIVROS_E_ABREVIACOES

# Constrói um mapa de abreviações mais robusto
BOOK_MAP = {}
for nome, abrev in LIVROS_E_ABREVIACOES:
    BOOK_MAP[nome.lower().replace(" ", "")] = nome
    BOOK_MAP[abrev.lower().replace(" ", "")] = nome

def _parse_reference(ref_string: str):
    pattern = re.compile(r'^\s*([1-3]?\s*[a-zA-Záéíóúâêôãõç]+)\.?\s*(\d+)(?::(\d+)(?:-(\d+))?)?\s*$')
    match = pattern.match(ref_string)
    if not match: return None
    groups = match.groups()
    book, chapter, start_v, end_v = groups
    return book.strip(), int(chapter), int(start_v) if start_v else 1, int(end_v) if end_v else (int(start_v) if start_v else None)

def handle_bible_command(args: list[str]):
    if not args:
        return Panel("[bold red]Uso:[/bold red] bible <referência>", border_style="red")

    ref_string = " ".join(args)
    parsed_ref = _parse_reference(ref_string)
    if not parsed_ref:
        return Panel(f"[bold red]Referência inválida:[/bold red] '{ref_string}'", border_style="red")

    book_input, chapter, start_verse, end_verse = parsed_ref
    book_key = book_input.lower().replace(" ", "").replace(".", "")
    book_full_name = BOOK_MAP.get(book_key)
    
    if not book_full_name:
        return Panel(f"[bold red]Livro não reconhecido:[/bold red] '{book_input}'", border_style="red")

    verses = bible.get_verses(book_full_name, chapter, start_verse, end_verse)
    if not verses:
        return Panel("[yellow]Referência não encontrada.[/yellow]", border_style="yellow")

    title = f"📖 {book_full_name} {chapter}:{start_verse}"
    if end_verse and end_verse != start_verse: title += f"-{end_verse}"
    
    content = [Text.assemble((f"[{v['verse']}] ", "yellow"), v['text']) for v in verses]
    return Panel(Group(*content), title=title, border_style="#fabd2f")
