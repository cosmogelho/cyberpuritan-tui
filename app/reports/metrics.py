# app/reports/metrics.py
from collections import Counter
from datetime import datetime, timedelta
from rich.panel import Panel
from rich.table import Table
from app.core.theme import console
from app.models import journal_model, action_item_model

def generate_weekly_report():
    """
    Gera e exibe um relatório de métricas devocionais da última semana.
    """
    console.print(Panel("[bold cyan]Relatório Devocional Semanal[/bold cyan]", expand=False))

    # 1. Análise do Diário (Journal)
    entries = journal_model.get_all_entries()
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    
    recent_entries = [e for e in entries if datetime.strptime(e['entry_date'], '%Y-%m-%d %H:%M:%S') > one_week_ago]
    
    console.print(f"\n[info]Diário:[/info]")
    console.print(f" - Você escreveu [bold green]{len(recent_entries)}[/bold green] entradas nos últimos 7 dias.")

    # Análise de Tags
    all_tags = []
    for entry in recent_entries:
        tags = [tag.strip() for tag in entry['tags'].split(',') if tag.strip()]
        all_tags.extend(tags)
    
    if all_tags:
        tag_counts = Counter(all_tags)
        most_common_tags = tag_counts.most_common(3)
        tags_str = ", ".join([f"'{tag}' ({count}x)" for tag, count in most_common_tags])
        console.print(f" - Suas tags mais comuns na semana foram: [yellow]{tags_str}[/yellow].")

    # 2. Análise das Ações (Actions)
    console.print(f"\n[info]Ações:[/info]")
    
    # Resoluções
    resolutions = action_item_model.get_items('Resolução')
    active_resolutions = [r for r in resolutions if r['status'] == 'Ativo']
    console.print(f" - Você tem [bold green]{len(active_resolutions)}[/bold green] resoluções ativas.")
    
    # Pedidos de Oração
    prayers = action_item_model.get_items('Pedido de Oração')
    active_prayers = [p for p in prayers if p['status'] == 'Ativo']
    answered_prayers_total = len(prayers) - len(active_prayers)
    
    console.print(f" - Você tem [bold green]{len(active_prayers)}[/bold green] pedidos de oração ativos.")
    if answered_prayers_total > 0:
        console.print(f" - Deus já respondeu a [bold green]{answered_prayers_total}[/bold green] orações registradas!")

    console.print("\n[italic]Continue perseverando na piedade, pois \"o exercício físico para pouco é proveitoso, mas a piedade para tudo é proveitosa\" (1 Timóteo 4:8).[/italic]")
