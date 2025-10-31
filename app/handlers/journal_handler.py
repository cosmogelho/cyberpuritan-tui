# app/handlers/journal_handler.py
from rich.panel import Panel
from rich.markup import escape
from rich.console import Group
from app.models import journal_model

def handle_journal_command(args: list[str]):
    if not args or args[0] not in ['view', 'find']:
        return Panel("[bold red]Uso:[/bold red] journal [view|find <tag>]", border_style="red")

    sub_cmd = args[0]
    
    if sub_cmd == 'view':
        entries = journal_model.get_all_entries()
        if not entries:
            return Panel("[yellow]Nenhuma entrada no diário ainda.[/yellow]", border_style="yellow")
        
        panels = [Panel(escape(e['content']), title=f"[#fabd2f]{e['entry_date']}[/] | Tags: [#8ec07c]{e['tags']}[/]", border_style="cyan") for e in entries]
        return Group(*panels)
        
    elif sub_cmd == 'find':
        if len(args) < 2:
            return Panel("[bold red]Uso:[/bold red] journal find <tag>", border_style="red")
        tag = args[1]
        entries = journal_model.get_entries_by_tag(tag)
        if not entries:
            return Panel(f"[yellow]Nenhuma entrada encontrada com a tag '{tag}'.[/yellow]", border_style="yellow")
            
        panels = [Panel(escape(e['content']), title=f"[#fabd2f]{e['entry_date']}[/] | Tags: [#8ec07c]{e['tags']}[/]", border_style="cyan") for e in entries]
        return Group(*panels)
