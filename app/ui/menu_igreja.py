# app/ui/menu_igreja.py
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from app.core.theme import console

# Importar modelos e views relevantes
from app.models.sermon import SermonManager
from app.models.study import StudyManager
from app.ui import sermon_view, study_view

# Instanciar os managers necessários para este menu
sermon_manager = SermonManager()
study_manager = StudyManager()

def _iniciar_menu_estudos():
    while True:
        console.clear()
        menu_estudos = Table(title="Estudos & Anotações", box=None)
        menu_estudos.add_column(style="yellow"); menu_estudos.add_column()
        menu_estudos.add_row("1.", "Listar anotações")
        menu_estudos.add_row("2.", "Criar nova anotação")
        menu_estudos.add_row("0.", "Voltar")
        console.print(Panel(menu_estudos, border_style="painel_borda"))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=["1", "2", "0"], show_choices=False)

        if escolha == '1':
            while True:
                console.clear()
                id_escolhido = study_view.exibir_lista_notas(study_manager.get_all_notes())
                if id_escolhido:
                    nota_detalhada = study_manager.get_note_by_id(int(id_escolhido))
                    if nota_detalhada: study_view.exibir_detalhes_nota(nota_detalhada)
                    Prompt.ask("\n[info]Pressione Enter para voltar à lista...[/info]")
                else: break
        elif escolha == '2':
            dados_novos = study_view.prompt_nova_nota()
            novo_id = study_manager.add_note(**dados_novos)
            if novo_id: console.print(f"\n[sucesso]Anotação #{novo_id} criada com sucesso![/sucesso]")
            else: console.print(f"\n[erro]Falha ao criar anotação.[/erro]")
            Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
        elif escolha == '0': break

def _iniciar_menu_sermoes():
    while True:
        console.clear()
        menu_sermoes = Table(title="Registro de Sermões", box=None)
        menu_sermoes.add_column(style="yellow"); menu_sermoes.add_column()
        menu_sermoes.add_row("1.", "Listar sermões")
        menu_sermoes.add_row("2.", "Adicionar sermão")
        menu_sermoes.add_row("0.", "Voltar")
        console.print(Panel(menu_sermoes, border_style="painel_borda"))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=["1", "2", "0"], show_choices=False)

        if escolha == '1':
            while True:
                console.clear()
                id_escolhido = sermon_view.exibir_lista_sermoes(sermon_manager.get_all_sermoes())
                if id_escolhido:
                    sermon_detalhado = sermon_manager.get_sermon_by_id(id_escolhido)
                    sermon_view.exibir_detalhes_sermon(id_escolhido, sermon_detalhado)
                    Prompt.ask("\n[info]Pressione Enter para voltar à lista...[/info]")
                else: break
        elif escolha == '2':
            dados_novos = sermon_view.prompt_novo_sermon()
            novo_id = sermon_manager.add_sermon(dados_novos)
            console.print(f"\n[sucesso]Sermão #{novo_id} registrado com sucesso![/sucesso]")
            Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
        elif escolha == '0': break

def iniciar_menu_igreja():
    """Loop do menu para o módulo de Atividades da Igreja."""
    menu_map = {
        "1": ("Registro de Sermões", _iniciar_menu_sermoes),
        "2": ("Estudos & Anotações", _iniciar_menu_estudos),
    }
    while True:
        console.clear()
        menu = Table(title="Atividades da Igreja", box=None)
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
