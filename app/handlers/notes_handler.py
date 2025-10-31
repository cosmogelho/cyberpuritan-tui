# app/handlers/notes_handler.py
from rich.table import Table
from rich.panel import Panel
from rich.markup import escape
from app.models import notes_model

def handle_notes_command(args: list[str]):
    if not args or args[0] not in ['view', 'read']:
        return Panel("[bold red]Uso:[/bold red] notes [view|read <id>]", border_style="red")

    sub_cmd = args[0]

    if sub_cmd == 'view':
        notes = notes_model.get_all_notes()
        table = Table(title="Notas de Estudo (Commonplace Book)")
        table.add_column("ID", style="cyan")
        table.add_column("Título", style="white")
        table.add_column("Tags", style="yellow")
        for note in notes:
            table.add_row(str(note['id']), note['title'], note['tags'])
        return table
        
    elif sub_cmd == 'read':
        try:
            note_id = int(args[1])
            note = notes_model.get_note_by_id(note_id)
            if note:
                return Panel(escape(note['content']), title=f"[#fabd2f]{note['title']}[/] | Tags: [#8ec07c]{note['tags']}[/]", border_style="cyan")
            else:
                return Panel("[yellow]Nota não encontrada.[/yellow]", border_style="yellow")
        except (IndexError, ValueError):
            return Panel("[bold red]Uso:[/bold red] notes read <id>", border_style="red")
