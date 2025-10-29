# app/ui/menu_recursos.py
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from app.core.theme import console

# Importar modelos e views relevantes
from app.models import bible, symbols, psaltery
from app.ui import bible_view, symbols_view, psaltery_view

def _iniciar_leitura_biblia(session_state: dict):
    console.print(Panel("Consulta à Bíblia", style="titulo", border_style="painel_borda"))
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

def iniciar_menu_recursos(session_state: dict):
    """Loop do menu para o módulo de Recursos e Consultas."""
    menu_map = {
        "1": ("Bíblia", lambda: _iniciar_leitura_biblia(session_state)),
        "2": ("Símbolos de Fé", _iniciar_menu_simbolos),
        "3": ("Saltério", _iniciar_menu_salterio),
    }
    while True:
        console.clear()
        menu = Table(title="Recursos & Consultas", box=None)
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
