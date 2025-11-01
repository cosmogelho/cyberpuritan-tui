# app/ui/telas.py (VERSÃO CORRETA)
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from pyfiglet import Figlet
from rich.text import Text

# Inicializa o console do Rich
console = Console()

def criar_banner(texto: str) -> Panel:
    """Cria um banner de título com arte ASCII."""
    f = Figlet(font='slant')
    arte_ascii = f.renderText(texto)
    return Panel(Align.center(arte_ascii, vertical="middle"), style="bold cyan", border_style="cyan")

# --- Banners Pré-renderizados ---
BANNER_PRINCIPAL = criar_banner("Cyber Puritano")
BANNER_DIARIO = criar_banner("Diario")
BANNER_ACOES = criar_banner("Acoes")
BANNER_NOTAS = criar_banner("Notas")
BANNER_BIBLIA = criar_banner("Biblia")
BANNER_SIMBOLOS = criar_banner("Simbolos")
BANNER_SALTERIO = criar_banner("Salterio")
BANNER_RELATORIOS = criar_banner("Relatorios")

def desenhar_layout_geral(banner: Panel, ajuda: Panel, conteudo: any, prompt: str, mensagem: str = ""):
    """Função base para desenhar todas as telas da TUI."""
    layout = Layout()
    layout.split(
        Layout(name="header", size=8),
        Layout(ratio=1, name="main"),
        Layout(size=3, name="footer"),
    )
    layout["main"].split_row(Layout(name="side", size=40), Layout(name="body", ratio=2))
    
    layout["header"].update(banner)
    layout["side"].update(ajuda)
    layout["body"].update(Panel(conteudo if conteudo is not None else "", border_style="dim", title="[bold]Conteúdo Principal[/bold]"))
    
    rodape_painel = Panel(
        Text.from_markup(f"[bold green]{prompt}[/bold green] [yellow]{mensagem}[/yellow]"),
        border_style="dim"
    )
    layout["footer"].update(rodape_painel)
    console.print(layout)

# ===== A FUNÇÃO QUE FALTAVA ESTÁ AQUI AGORA =====
def desenhar_menu_principal():
    """Prepara os componentes visuais para a tela do menu principal."""
    menu_texto = (
        "[bold cyan]NAVEGAÇÃO PRINCIPAL[/bold cyan]\n"
        "─────────────────────\n"
        "[yellow]1[/yellow]. Diário\n"
        "[yellow]2[/yellow]. Ações (Resoluções e Orações)\n"
        "[yellow]3[/yellow]. Notas de Estudo\n"
        "[yellow]4[/yellow]. Bíblia\n"
        "[yellow]5[/yellow]. Símbolos de Fé\n"
        "[yellow]6[/yellow]. Saltério\n"
        "[yellow]7[/yellow]. Relatórios"
    )
    conteudo_central = Panel(
        Align.center(menu_texto, vertical="middle"),
        title="Módulos Devocionais",
        border_style="green",
    )
    
    ajuda = Panel(
        "Digite um [yellow]número[/yellow] para entrar em um módulo, [yellow]h[/yellow] para ajuda ou [yellow]q[/yellow] para sair.",
        title="[bold]Info[/bold]",
        border_style="green"
    )
    return BANNER_PRINCIPAL, ajuda, Align.center(conteudo_central), "Escolha uma opção >"

def desenhar_tela_salterio(conteudo: any, mensagem: str):
    """Desenha a tela específica do módulo Saltério."""
    comandos = (
        "[bold cyan]COMANDOS[/bold cyan]\n"
        "──────────\n"
        "[yellow]listar, l[/yellow]      - Lista os salmos\n"
        "[yellow]proximo, p[/yellow]     - Próxima página\n"
        "[yellow]anterior, a[/yellow]    - Página anterior\n\n"
        "[yellow]ver <num>[/yellow]       - Mostra detalhes\n"
        "[yellow]tocar <num>[/yellow]     - Toca o áudio\n\n"
        "[yellow]voltar[/yellow]         - Retorna ao Menu"
    )
    ajuda = Panel(comandos, title="[bold]Ajuda do Módulo[/bold]", border_style="green")
    desenhar_layout_geral(BANNER_SALTERIO, ajuda, conteudo, "(Saltério) >", mensagem)

def desenhar_tela_diario(conteudo: any, mensagem: str):
    """Desenha a tela específica do módulo Diário."""
    comandos = (
        "[bold cyan]COMANDOS[/bold cyan]\n"
        "──────────\n"
        "[yellow]add[/yellow]           - Adicionar nova entrada\n"
        "[yellow]ver[/yellow]           - Ver todas as entradas\n"
        "[yellow]buscar <tag>[/yellow] - Buscar por tag\n\n"
        "[yellow]voltar[/yellow]        - Retorna ao Menu"
    )
    ajuda = Panel(comandos, title="[bold]Ajuda do Módulo[/bold]", border_style="green")
    desenhar_layout_geral(BANNER_DIARIO, ajuda, conteudo, "(Diário) >", mensagem)
