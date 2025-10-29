# app/ui/reports_view.py
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.align import Align
from rich.text import Text
from app.core.theme import console

def display_piety_report(summary: dict | None):
    """Exibe o painel de relatório do Diário de Piedade."""
    if not summary:
        console.print(Panel("[info]Não há dados suficientes no Diário de Piedade para gerar um relatório.[/info]", title="Relatório de Piedade"))
        return

    # Tabela de Consistência
    t_cons = Table(title=f"Consistência (baseado em {summary['total_dias_registrados']} dias)")
    t_cons.add_column("Métrica", style="cyan")
    t_cons.add_column("Taxa", style="yellow", justify="right")
    for metrica, taxa in summary['consistencia'].items():
        t_cons.add_row(metrica, f"{taxa:.1f}%")

    # Tabela de Qualidade da Oração
    t_oracao = Table(title="Qualidade da Oração")
    t_oracao.add_column("Classificação", style="cyan")
    t_oracao.add_column("Dias", style="yellow", justify="right")
    for label, count in summary['qualitativo_oracao'].items():
        t_oracao.add_row(label, str(count))
        
    # Tabela de Atitude perante o Pecado
    t_pecado = Table(title="Atitude Perante o Pecado")
    t_pecado.add_column("Classificação", style="cyan")
    t_pecado.add_column("Dias", style="yellow", justify="right")
    for label, count in summary['qualitativo_pecado'].items():
        t_pecado.add_row(label, str(count))

    render_group = Group(
        Align.center(t_cons),
        Text("---", justify="center"),
        Align.center(t_oracao),
        Align.center(t_pecado),
    )
    console.print(Panel(
        render_group,
        title=f"Relatório de Piedade - Últimos {summary['periodo_dias']} dias",
        border_style="painel_borda"
    ))

def display_resolutions_report(summary: dict | None):
    """Exibe o painel de relatório das Resoluções."""
    if not summary:
        console.print(Panel("[info]Nenhuma resolução cadastrada para gerar um relatório.[/info]", title="Relatório de Resoluções"))
        return
    
    # Tabela de Resumo
    t_resumo = Table(title="Visão Geral")
    t_resumo.add_column("Métrica", style="cyan")
    t_resumo.add_column("Valor", style="yellow", justify="right")
    t_resumo.add_row("Total de Resoluções", str(summary['total_resolucoes']))
    t_resumo.add_row("Média de Revisões por Resolução", f"{summary['media_revisoes']:.1f}")

    # Tabela de Categorias
    t_cat = Table(title="Distribuição por Categoria")
    t_cat.add_column("Categoria", style="cyan")
    t_cat.add_column("Quantidade", style="yellow", justify="right")
    for cat, count in summary['dist_categorias'].items():
        t_cat.add_row(cat, str(count))

    render_group = Group(
        Align.center(t_resumo),
        Text("---", justify="center"),
        Align.center(t_cat),
    )
    console.print(Panel(
        render_group,
        title="Relatório de Resoluções",
        border_style="painel_borda"
    ))
