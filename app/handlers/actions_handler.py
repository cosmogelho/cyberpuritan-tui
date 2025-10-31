# app/handlers/actions_handler.py
from datetime import datetime
from rich.table import Table
from rich.panel import Panel
from app.models import action_item_model

def handle_actions_command(args: list[str]):
    if len(args) < 2 or args[0] not in ['view', 'update'] or args[1] not in ['res', 'ora']:
        return Panel("[bold red]Uso:[/bold red] actions [view|update] [res|ora] [argumentos...]", border_style="red")

    sub_cmd, item_type_arg = args[0], args[1]
    item_type = 'Resolução' if item_type_arg == 'res' else 'Pedido de Oração'

    if sub_cmd == 'view':
        items = action_item_model.get_items(item_type)
        table = Table(title=f"Lista de {item_type}s")
        table.add_column("ID", style="cyan")
        table.add_column("Texto", style="white")
        table.add_column("Status", style="yellow")
        for item in items:
            table.add_row(str(item['id']), item['text'], item['status'])
        return table
        
    elif sub_cmd == 'update':
        try:
            item_id = int(args[2])
            new_status = args[3]
            action_item_model.update_item_status(item_id, new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return Panel(f"[green]Status do item {item_id} atualizado para '{new_status}'.[/green]", border_style="green")
        except (IndexError, ValueError):
            return Panel("[bold red]Uso:[/bold red] actions update [res|ora] <id> <novo_status>", border_style="red")
