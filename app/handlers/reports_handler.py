# app/handlers/reports_handler.py
from collections import Counter
from datetime import datetime, timedelta
from rich.panel import Panel
from rich.text import Text
from app.models import journal_model, action_item_model

def handle_reports_command(args: list[str]):
    """Gera um relatório semanal e o retorna como um widget Rich."""
    # 1. Diário
    entries = journal_model.get_all_entries()
    one_week_ago = datetime.now() - timedelta(days=7)
    recent = [e for e in entries if datetime.strptime(e['entry_date'], '%Y-%m-%d %H:%M:%S') > one_week_ago]
    
    journal_txt = f"- Você escreveu [bold green]{len(recent)}[/bold green] entradas nos últimos 7 dias."
    all_tags = [tag.strip() for e in recent for tag in e['tags'].split(',') if tag.strip()]
    if all_tags:
        tags_str = ", ".join([f"'{t}' ({c}x)" for t, c in Counter(all_tags).most_common(3)])
        journal_txt += f"\n- Tags mais comuns: [yellow]{tags_str}[/yellow]."

    # 2. Ações
    res = action_item_model.get_items('Resolução')
    active_res = len([r for r in res if r['status'] == 'Ativo'])
    
    pray = action_item_model.get_items('Pedido de Oração')
    active_pray = len([p for p in pray if p['status'] == 'Ativo'])
    
    actions_txt = f"- Você tem [bold green]{active_res}[/bold green] resoluções e [bold green]{active_pray}[/bold green] orações ativas."

    # Monta o texto final
    content = Text.assemble(
        ("Diário:\n", "bold info"), journal_txt,
        ("\n\n", ""),
        ("Ações:\n", "bold info"), actions_txt,
        ("\n\n", ""),
        ("[italic]Continue perseverando na piedade (1 Timóteo 4:8).[/italic]", "dim")
    )
    
    return Panel(content, title="Relatório Devocional Semanal", border_style="green")
