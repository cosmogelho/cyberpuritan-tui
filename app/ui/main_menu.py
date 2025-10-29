# app/ui/main_menu.py
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.padding import Padding
from rich.prompt import Prompt
from app.core.theme import console
from app.core.config import VERSAO_BIBLIA_PADRAO, VERSOES_BIBLIA_DISPONIVEIS

# Importar os novos submenus e os módulos de relatório
from .menu_pessoal import iniciar_menu_pessoal
from .menu_igreja import iniciar_menu_igreja
from .menu_recursos import iniciar_menu_recursos
from app.reports import metrics
from app.ui import reports_view

# O estado da sessão (versão da Bíblia) permanece global
session_state = {"versao_biblia": VERSAO_BIBLIA_PADRAO}

def _mudar_versao_biblia():
    """Altera a versão da Bíblia usada nas consultas."""
    nova = Prompt.ask(
        "Selecione a versão da Bíblia",
        choices=VERSOES_BIBLIA_DISPONIVEIS,
        default=session_state["versao_biblia"]
    )
    session_state["versao_biblia"] = nova.upper()
    console.print(f"Versão alterada para [sucesso]{session_state['versao_biblia']}[/sucesso].")
    Prompt.ask("\n[info]Pressione Enter para continuar...[/info]", default="")

def _iniciar_relatorios():
    """Orquestra a busca e exibição de todos os relatórios."""
    console.print(Panel(Text("Relatórios & Métricas", justify="center"), border_style="painel_borda"))
    
    # Relatório de Piedade
    piety_summary = metrics.get_piety_summary()
    reports_view.display_piety_report(piety_summary)
    
    console.print() # Adiciona um espaço

    # Relatório de Resoluções
    resolution_summary = metrics.get_resolution_summary()
    reports_view.display_resolutions_report(resolution_summary)

    Prompt.ask("\n[info]Pressione Enter para voltar ao menu...[/info]", default="")


def iniciar_menu_interativo():
    """Loop principal do modo interativo, agora como um roteador."""
    # Adicionada a nova opção de menu
    opcoes_menu = {
        "1": ("Devoção Pessoal", iniciar_menu_pessoal),
        "2": ("Atividades da Igreja", iniciar_menu_igreja),
        "3": ("Recursos & Consultas", lambda: iniciar_menu_recursos(session_state)),
        "4": ("Relatórios & Métricas", _iniciar_relatorios),
        "5": ("Mudar Versão da Bíblia", _mudar_versao_biblia),
        "0": ("Sair", None)
    }

    while True:
        console.clear()
        titulo_principal = Text("Cyber-Puritano", justify="center")
        subtitulo_menu = f"Menu Principal (Bíblia: {session_state['versao_biblia']})"
        
        console.print(Panel(titulo_principal, border_style="painel_borda"))
        
        menu = Table(title=subtitulo_menu, box=None, padding=(0, 2))
        menu.add_column(style="yellow", width=3)
        menu.add_column()

        for key, (label, _) in opcoes_menu.items():
            menu.add_row(f"{key}.", label)

        console.print(Padding(menu, (1, 2)))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=opcoes_menu.keys(), show_choices=False)

        if escolha == "0":
            console.clear()
            console.print(Panel("[sucesso]Soli Deo Gloria![/sucesso]"))
            break

        console.clear()
        _, funcao = opcoes_menu[escolha]
        funcao()
