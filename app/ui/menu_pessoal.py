# app/ui/menu_pessoal.py
from datetime import date
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from app.core.theme import console

# Importar modelos e views relevantes
from app.models.piety import PiedadeManager
from app.models.resolution import ResolutionManager
from app.ui import piety_view, resolution_view

# Instanciar os managers necessários para este menu
piedade_manager = PiedadeManager()
resolution_manager = ResolutionManager()

def _iniciar_menu_piedade():
    while True:
        console.clear()
        menu_piedade = Table(title="Diário de Piedade", box=None)
        menu_piedade.add_column(style="yellow"); menu_piedade.add_column()
        menu_piedade.add_row("1.", "Registrar / Ver hoje")
        menu_piedade.add_row("2.", "Análise dos últimos 30 dias")
        menu_piedade.add_row("0.", "Voltar")
        console.print(Panel(menu_piedade, border_style="painel_borda"))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=["1", "2", "0"], show_choices=False)
        
        if escolha == '1':
            hoje_str = date.today().isoformat()
            registro_hoje = piedade_manager.get_registro_dia(hoje_str)
            console.clear()
            if registro_hoje:
                piety_view.exibir_registro_dia(hoje_str, registro_hoje)
                if not Confirm.ask("\n[prompt]Já existe um registro para hoje. Deseja sobrescrevê-lo?[/prompt]"):
                    continue
            novos_dados = piety_view.prompt_registro_diario()
            piedade_manager.registrar_dia(hoje_str, novos_dados)
            console.print("\n[sucesso]Registro salvo com sucesso![/sucesso]")
            Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
        elif escolha == '2':
            console.clear()
            analise = piedade_manager.gerar_analise()
            piety_view.exibir_analise(analise)
            Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
        elif escolha == '0': break

def _iniciar_menu_resolucoes():
    while True:
        console.clear()
        menu_resolutions = Table(title="Minhas Resoluções", box=None)
        menu_resolutions.add_column(style="yellow"); menu_resolutions.add_column()
        menu_resolutions.add_row("1.", "Revisão do dia (aleatória)")
        menu_resolutions.add_row("2.", "Revisão focada (menos vista)")
        menu_resolutions.add_row("3.", "Listar todas")
        menu_resolutions.add_row("4.", "Adicionar nova")
        menu_resolutions.add_row("0.", "Voltar")
        console.print(Panel(menu_resolutions, border_style="painel_borda"))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=["1", "2", "3", "4", "0"], show_choices=False)

        if escolha in ('1', '2'):
            resultado = resolution_manager.get_random_resolution() if escolha == '1' else resolution_manager.get_least_reviewed_resolution()
            titulo = "Revisão do Dia" if escolha == '1' else "Revisão Focada"
            if resultado:
                res_id, dados = resultado
                resolution_view.exibir_resolucao_para_revisao(res_id, dados, titulo)
                resolution_manager.update_review_stats(res_id)
                Prompt.ask("\n[info]Medite sobre este propósito. Pressione Enter para continuar...[/info]")
            else:
                console.print("[info]Nenhuma resolução registrada para revisar.[/info]")
                Prompt.ask("\n[info]Pressione Enter para voltar...[/info]")
        elif escolha == '3':
            console.clear()
            resolution_view.exibir_lista_resolucoes(resolution_manager.get_all_resolutions())
            Prompt.ask("\n[info]Pressione Enter para voltar...[/info]")
        elif escolha == '4':
            dados_novos = resolution_view.prompt_nova_resolucao()
            novo_id = resolution_manager.add_resolution(**dados_novos)
            console.print(f"\n[sucesso]Resolução #{novo_id} registrada com sucesso![/sucesso]")
            Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
        elif escolha == '0': break

def iniciar_menu_pessoal():
    """Loop do menu para o módulo de Devoção Pessoal."""
    menu_map = {
        "1": ("Diário de Piedade", _iniciar_menu_piedade),
        "2": ("Minhas Resoluções", _iniciar_menu_resolucoes),
    }
    while True:
        console.clear()
        menu = Table(title="Devoção Pessoal", box=None)
        menu.add_column(style="yellow"); menu.add_column()
        for key, (label, _) in menu_map.items():
            menu.add_row(f"{key}.", label)
        menu.add_row("0.", "Voltar ao menu principal")
        console.print(Panel(menu, border_style="painel_borda"))
        
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=list(menu_map.keys()) + ["0"], show_choices=False)
        if escolha == '0':
            break
        
        console.clear()
        _, func = menu_map[escolha]
        func()
