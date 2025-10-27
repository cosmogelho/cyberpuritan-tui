# app/ui/main_menu.py
from datetime import date
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.padding import Padding
from rich.prompt import Prompt, Confirm
from app.core.theme import console
from app.core.config import VERSAO_BIBLIA_PADRAO, VERSOES_BIBLIA_DISPONIVEIS

# Importar TODOS os modelos e views necessários
from app.models import bible, symbols, psaltery
from app.models.sermon import SermonManager
from app.models.piety import PiedadeManager
from app.models.study import StudyManager
from app.models.resolution import ResolutionManager
from app.ui import bible_view, symbols_view, psaltery_view, sermon_view, piety_view, study_view, resolution_view

# Instanciar TODOS os managers
sermon_manager = SermonManager()
piedade_manager = PiedadeManager()
study_manager = StudyManager()
resolution_manager = ResolutionManager()

# Estado da sessão
session_state = {"versao_biblia": VERSAO_BIBLIA_PADRAO}

def _iniciar_leitura_biblia():
    console.print(Panel("Bíblia", style="titulo", border_style="painel_borda"))
    livro = Prompt.ask("[prompt]Livro (ou 'ajuda')[/prompt]")
    if livro.lower() == "ajuda":
        bible_view.mostrar_tabela_livros()
        livro = Prompt.ask("[prompt]Livro[/prompt]")
    cap = Prompt.ask("[prompt]Capítulo[/prompt]")
    ver = Prompt.ask("[prompt]Versículo (opcional)[/prompt]", default="")
    try:
        resultado = bible.obter_passagem(
            versao=session_state["versao_biblia"],
            livro=livro, capitulo=int(cap),
            versiculo=int(ver) if ver else None
        )
        bible_view.exibir_passagem(resultado)
    except (ValueError, TypeError):
        console.print("[erro]Capítulo e versículo devem ser números válidos.[/erro]")

def _iniciar_menu_simbolos():
    console.print(Panel("Símbolos de Fé", style="titulo", border_style="painel_borda"))
    doc = Prompt.ask("Qual documento? [1] Confissão de Fé [2] Catecismo Maior [3] Breve Catecismo", choices=["1", "2", "3"], show_choices=False)
    try:
        if doc == "1":
            cap = int(Prompt.ask("[prompt]Capítulo[/prompt]"))
            sec_str = Prompt.ask("[prompt]Seção (opcional)[/prompt]", default="")
            sec = int(sec_str) if sec_str else None
            resultado = symbols.obter_simbolo('cfw', cap, sec)
            symbols_view.exibir_simbolos(resultado, 'cfw')
        else:
            tipo = 'cmw' if doc == "2" else 'bcw'
            num = int(Prompt.ask("[prompt]Número da pergunta[/prompt]"))
            resultado = symbols.obter_simbolo(tipo, num)
            symbols_view.exibir_simbolos(resultado, tipo)
    except (ValueError, TypeError):
        console.print("[erro]Entrada inválida. Por favor, insira um número.[/erro]")

def _iniciar_menu_salterio():
    console.print(Panel("Saltério", style="titulo", border_style="painel_borda"))
    num_salmo = Prompt.ask("[prompt]Digite o número do Salmo[/prompt]")
    resultados = psaltery.buscar_versoes_salmo(num_salmo)
    if isinstance(resultados, dict) and "erro" in resultados:
        console.print(f"[erro]{resultados['erro']}[/erro]")
        return
    while True:
        indice_escolhido = psaltery_view.exibir_lista_de_salmos(resultados)
        if indice_escolhido is not None:
            versao_selecionada = resultados[indice_escolhido]
            psaltery_view.exibir_detalhes_do_salmo(versao_selecionada)
            if not Confirm.ask("\n[prompt]Ver outra versão desta lista?[/prompt]", default=True):
                break
        else:
            break

def _iniciar_menu_estudos():
    while True:
        console.clear()
        menu_estudos = Table(title="Estudos", box=None)
        menu_estudos.add_column(style="yellow"); menu_estudos.add_column()
        menu_estudos.add_row("1.", "Listar")
        menu_estudos.add_row("2.", "Criar")
        menu_estudos.add_row("0.", "Voltar ao menu principal")
        console.print(Panel(menu_estudos, border_style="painel_borda"))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=["1", "2", "0"], show_choices=False)
        if escolha == '1':
            while True:
                console.clear()
                todas_notas = study_manager.get_all_notes()
                id_escolhido = study_view.exibir_lista_notas(todas_notas)
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
        menu_sermoes.add_row("1.", "Listar")
        menu_sermoes.add_row("2.", "Adicionar")
        menu_sermoes.add_row("0.", "Voltar ao menu principal")
        console.print(Panel(menu_sermoes, border_style="painel_borda"))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=["1", "2", "0"], show_choices=False)
        if escolha == '1':
            while True:
                console.clear()
                todos_sermoes = sermon_manager.get_all_sermoes()
                id_escolhido = sermon_view.exibir_lista_sermoes(todos_sermoes)
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

def _iniciar_menu_piedade():
    while True:
        console.clear()
        menu_piedade = Table(title="Diário", box=None)
        menu_piedade.add_column(style="yellow"); menu_piedade.add_column()
        menu_piedade.add_row("1.", "Registrar / Ver hoje")
        menu_piedade.add_row("2.", "Últimos 30 dias")
        menu_piedade.add_row("0.", "Voltar ao menu principal")
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
    """Loop do menu para o módulo de Resoluções."""
    while True:
        console.clear()
        menu_resolutions = Table(title="Minhas Resoluções", box=None)
        menu_resolutions.add_column(style="yellow"); menu_resolutions.add_column()
        menu_resolutions.add_row("1.", "Revisão do dia (aleatória)")
        menu_resolutions.add_row("2.", "Revisão focada (menos vista)")
        menu_resolutions.add_row("3.", "Listar")
        menu_resolutions.add_row("4.", "Adicionar")
        menu_resolutions.add_row("0.", "Voltar ao menu principal")
        console.print(Panel(menu_resolutions, border_style="painel_borda"))

        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=["1", "2", "3", "4", "0"], show_choices=False)

        if escolha == '1' or escolha == '2':
            if escolha == '1':
                resultado = resolution_manager.get_random_resolution()
                titulo = "Revisão do dia"
            else: # escolha == '2'
                resultado = resolution_manager.get_least_reviewed_resolution()
                titulo = "Revisão focada"

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
            todas_resolucoes = resolution_manager.get_all_resolutions()
            resolution_view.exibir_lista_resolucoes(todas_resolucoes)
            Prompt.ask("\n[info]Pressione Enter para voltar...[/info]")
        
        elif escolha == '4':
            dados_novos = resolution_view.prompt_nova_resolucao()
            novo_id = resolution_manager.add_resolution(**dados_novos)
            console.print(f"\n[sucesso]Resolução #{novo_id} registrada com sucesso![/sucesso]")
            Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
        
        elif escolha == '0':
            break

def _mudar_versao_biblia():
    nova = Prompt.ask("Selecione a versão da Bíblia", choices=VERSOES_BIBLIA_DISPONIVEIS, default=session_state["versao_biblia"])
    session_state["versao_biblia"] = nova.upper()
    console.print(f"Versão alterada para [sucesso]{session_state['versao_biblia']}[/sucesso].")

def iniciar_menu_interativo():
    """Loop principal do modo interativo."""
    opcoes_menu = {
        "1": ("Símbolos de fé", _iniciar_menu_simbolos),
        "2": ("Bíblia", _iniciar_leitura_biblia),
        "3": ("Saltério", _iniciar_menu_salterio),
        "4": ("Estudos", _iniciar_menu_estudos),
        "5": ("Sermões", _iniciar_menu_sermoes),
        "6": ("Diário", _iniciar_menu_piedade),
        "7": ("Resoluções", _iniciar_menu_resolucoes),
        "8": ("Tradução", _mudar_versao_biblia),
        "0": ("Sair", None)
    }

    while True:
        console.clear()
        console.print(Panel(Text("Cyber-Puritano", justify="center"), border_style="painel_borda"))
        menu = Table(title=f"[Menu Principal (Versão: {session_state['versao_biblia']})]", box=None, padding=(0,1))
        menu.add_column(style="yellow", width=3); menu.add_column(width=30)
        menu.add_column(style="yellow", width=3); menu.add_column()

        menu.add_row("1.", opcoes_menu["1"][0], "5.", opcoes_menu["5"][0])
        menu.add_row("2.", opcoes_menu["2"][0], "6.", opcoes_menu["6"][0])
        menu.add_row("3.", opcoes_menu["3"][0], "7.", opcoes_menu["7"][0])
        menu.add_row("4.", opcoes_menu["4"][0], "8.", opcoes_menu["8"][0])
        menu.add_row("", "", "0.", opcoes_menu["0"][0])

        console.print(Padding(menu, (1, 2)))
        escolha = Prompt.ask("[prompt]Escolha uma opção[/prompt]", choices=opcoes_menu.keys(), show_choices=False)

        if escolha == "0":
            console.clear()
            console.print(Panel("[sucesso]Soli Deo Gloria![/sucesso]"))
            break

        console.clear()
        opcoes_menu[escolha][1]()

        Prompt.ask("\n[info]Pressione Enter para voltar ao menu...[/info]", default="")
