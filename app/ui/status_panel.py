# app/ui/status_panel.py
from datetime import datetime, date, timedelta
from rich.panel import Panel
from rich.table import Table
from app.core.config import CALENDARIO_SEMANAL
from app.models.fasting import FastingManager

def render_status_panel() -> Panel:
    """Cria e retorna o painel de status dinâmico para a tela inicial."""
    now = datetime.now()
    today = now.date()
    weekday = today.weekday() # Monday is 0, Sunday is 6

    status_table = Table(box=None, show_header=False, padding=(0, 1))
    status_table.add_column(style="prompt")
    status_table.add_column()

    # 1. Status do Dia
    day_status = ""
    if weekday == 6:
        day_status = "O Dia do Senhor"
    elif weekday == 5:
        day_status = "Dia de Preparação"
    elif weekday in CALENDARIO_SEMANAL:
        day_status = CALENDARIO_SEMANAL[weekday]
    
    if day_status:
        status_table.add_row("Status do Dia:", day_status)

    # 2. Status Pessoal (Jejum)
    fm = FastingManager()
    active_fast = fm.get_active_fast()
    if active_fast:
        status_table.add_row("Status Pessoal:", f"[bold red]Em Jejum[/bold red] (Propósito: {active_fast['purpose']})")
    
    # 3. Lembretes e Contagem
    reminder = ""
    if weekday == 6: # Domingo
        reminder = "Santifique este dia. (Use: 'domingo guardar')"
    elif weekday == 5: # Sábado
        reminder = "Prepare seu coração. (Use: 'domingo preparar')"
    else:
        days_to_sunday = (6 - weekday)
        reminder = f"Faltam {days_to_sunday} dias para o Dia do Senhor."

    if reminder:
        status_table.add_row("Lembrete:", reminder)
    
    title = f"Status ({now.strftime('%d de %B de %Y, %A')})"
    return Panel(status_table, title=title, border_style="dim white")
