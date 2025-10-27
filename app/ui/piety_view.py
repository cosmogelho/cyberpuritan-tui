# app/ui/piety_view.py
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich.console import Group
from app.core.theme import console

def prompt_registro_diario() -> dict:
    """Coleta os dados do diário de piedade do usuário."""
    console.print(Panel("Registro Diário de Piedade", style="titulo"))
    
    consistencia = {
        "leitura_biblica": Confirm.ask("[prompt]Houve leitura bíblica hoje?[/prompt]"),
        "oracao": Confirm.ask("[prompt]Houve tempo de oração hoje?[/prompt]"),
        "catecismo": Confirm.ask("[prompt]Houve estudo dos símbolos de fé?[/prompt]")
    }
    
    qualitativo = {
        "oracao_qualidade": Prompt.ask(
            "[prompt]Como foi a qualidade da sua oração?[/prompt]",
            choices=["Distraída", "Normal", "Concentrada", "Vigorosa"],
            default="Normal"
        ),
        "pecado_atitude": Prompt.ask(
            "[prompt]Qual foi sua atitude perante o pecado?[/prompt]",
            choices=["Indiferente", "Luta Fraca", "Arrependido", "Vigilante"],
            default="Arrependido"
        )
    }
    
    return {"consistencia": consistencia, "qualitativo": qualitativo}

def exibir_registro_dia(data_str: str, dados: dict | None):
    """Mostra os detalhes de um registro de piedade."""
    if dados is None:
        console.print(f"[info]Nenhum registro encontrado para o dia {data_str}.[/info]")
        return
    
    consistencia = dados.get('consistencia', {})
    qualitativo = dados.get('qualitativo', {})

    t_cons = Table(title="Consistência", box=None, show_header=False)
    t_cons.add_column(width=25); t_cons.add_column()
    t_cons.add_row("Leitura Bíblica:", "✅" if consistencia.get('leitura_biblica') else "❌")
    t_cons.add_row("Oração:", "✅" if consistencia.get('oracao') else "❌")
    t_cons.add_row("Estudo dos Símbolos:", "✅" if consistencia.get('catecismo') else "❌")
    
    t_qual = Table(title="Análise Qualitativa", box=None, show_header=False)
    t_qual.add_column(width=25); t_qual.add_column()
    t_qual.add_row("Qualidade da Oração:", qualitativo.get('oracao_qualidade', 'N/A'))
    t_qual.add_row("Atitude Perante o Pecado:", qualitativo.get('pecado_atitude', 'N/A'))

    console.print(Panel(
        Group(Align.center(t_cons), Align.center(t_qual)),
        title=f"Diário de Piedade - {data_str}",
        border_style="painel_borda"
    ))

def exibir_analise(analise: dict | None):
    """Mostra um painel com a análise do período."""
    if analise is None:
        console.print("[info]Não há dados suficientes para gerar uma análise.[/info]")
        return

    total = analise['total_dias_registrados']
    t_cons = Table(title=f"Análise de Consistência (baseado em {total} dias)")
    t_cons.add_column("Métrica"); t_cons.add_column("Dias"); t_cons.add_column("Taxa")
    for metrica, contagem in analise['consistencia'].items():
        taxa = f"{(contagem/total)*100:.1f}%"
        t_cons.add_row(metrica.replace("_", " ").title(), str(contagem), taxa)

    console.print(Panel(Align.center(t_cons), title=f"Análise - Últimos {analise['periodo_dias']} dias", border_style="painel_borda"))
