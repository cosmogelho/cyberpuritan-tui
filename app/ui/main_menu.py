# app/ui/main_menu.py
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.padding import Padding
from rich.prompt import Prompt, Confirm
from app.core.theme import console
from app.core.config import VERSAO_BIBLIA_PADRAO, VERSOES_BIBLIA_DISPONIVEIS
from datetime import date, datetime
from app.core.connections import db_manager

# --- Importações de Models ---
from app.models.resolution import ResolutionManager
from app.models.record import RecordManager
from app.models.fasting import FastingManager
from app.models.sunday import SundayManager
from app.models import bible, psaltery, symbols

# --- Importações de Views e Painéis ---
from app.ui.status_panel import render_status_panel
from app.ui.resolution_view import prompt_nova_resolucao, exibir_lista_resolucoes, exibir_resolucao_para_revisao
from app.ui.record_view import prompt_novo_registro, exibir_lista_registros, exibir_detalhes_registro
from app.ui.bible_view import mostrar_tabela_livros, exibir_passagem
from app.ui.symbols_view import exibir_simbolos
from app.ui.psaltery_view import exibir_lista_de_salmos, exibir_detalhes_do_salmo
from app.reports import metrics


# --- Instanciar todos os managers ---
resolution_manager = ResolutionManager()
record_manager = RecordManager()
fasting_manager = FastingManager()
sunday_manager = SundayManager()

# --- Funções de Ação ---

def acao_meditacao_guiada():
    console.print(Panel("Meditação Guiada", style="titulo"))
    choice = Prompt.ask("[prompt]Qual o foco? [1] Na Palavra (Autoexame) [2] Doutrinária (Contemplação)[/prompt]", choices=["1", "2"])
    # ... (lógica da meditação)
    console.print("[sucesso]Meditação registrada![/sucesso]")

def acao_jejum_iniciar():
    active = fasting_manager.get_active_fast()
    if active:
        console.print("[erro]Já existe um jejum ativo.[/erro]")
        return
    purpose = Prompt.ask("[prompt]Propósito do jejum?[/prompt]")
    scripture = Prompt.ask("[prompt]Passagem de foco?[/prompt]")
    fast_id = fasting_manager.start_fast(purpose, scripture)
    console.print(f"[sucesso]Jejum #{fast_id} iniciado![/sucesso]")

def acao_jejum_concluir():
    active = fasting_manager.get_active_fast()
    if not active:
        console.print("[info]Nenhum jejum ativo.[/info]")
        return
    reflection = Prompt.ask(f"[prompt]Reflexão sobre o jejum #{active['id']}:[/prompt]")
    fasting_manager.finish_fast(active['id'], reflection)
    console.print(f"[sucesso]Jejum #{active['id']} concluído![/sucesso]")

def acao_domingo_preparar():
    console.print(Panel("Preparação para o Dia do Senhor", style="titulo"))
    checks = { "pastor": Confirm.ask("[prompt]Orou pelo pastor?[/prompt]"), "leitura": Confirm.ask("[prompt]Leu a passagem?[/prompt]"), "confissao": Confirm.ask("[prompt]Confessou seus pecados?[/prompt]"), "mundo": Confirm.ask("[prompt]Deixou as preocupações?[/prompt]"), "congregacao": Confirm.ask("[prompt]Orou pela congregação?[/prompt]")}
    sunday_manager.log_preparation(date.today().isoformat(), checks)
    console.print("[sucesso]Preparação registrada![/sucesso]")

def acao_domingo_guardar():
    console.print(Panel("Guardando o Dia do Senhor", style="titulo"))
    console.print("[info]Use os comandos 'igreja/registros add', 'recursos/salterio', etc.[/info]")

def acao_registros_add():
    dados = prompt_novo_registro()
    novo_id = record_manager.add_record(dados)
    console.print(f"\n[sucesso]Registro #{novo_id} ({dados['category']}) salvo![/sucesso]")

def acao_registros_listar():
    registros = record_manager.get_all_records()
    record_id = exibir_lista_registros(registros)
    if record_id:
        detalhes = record_manager.get_record_by_id(record_id)
        if detalhes:
            exibir_detalhes_registro(str(detalhes.id), detalhes)

def acao_resolucoes_revisar_random():
    resultado = resolution_manager.get_random_resolution()
    if not resultado: console.print("[info]Nenhuma resolução para revisar.[/info]"); return
    exibir_resolucao_para_revisao(str(resultado.id), vars(resultado), "Revisão do Dia")
    resolution_manager.update_review_stats(str(resultado.id))

def acao_resolucoes_revisar_focada():
    resultado = resolution_manager.get_least_reviewed_resolution()
    if not resultado: console.print("[info]Nenhuma resolução para revisar.[/info]"); return
    exibir_resolucao_para_revisao(str(resultado.id), vars(resultado), "Revisão Focada")
    resolution_manager.update_review_stats(str(resultado.id))
    
def acao_resolucoes_listar():
    exibir_lista_resolucoes(resolution_manager.get_all_resolutions())

def acao_resolucoes_add():
    dados = prompt_nova_resolucao()
    novo_id = resolution_manager.add_resolution(**dados)
    console.print(f"\n[sucesso]Resolução #{novo_id} registrada![/sucesso]")

def acao_recursos_biblia(session_state):
    livro = Prompt.ask("[prompt]Livro (ou 'ajuda')[/prompt]")
    if livro.lower() == "ajuda": mostrar_tabela_livros(); livro = Prompt.ask("[prompt]Livro[/prompt]")
    cap = Prompt.ask("[prompt]Capítulo[/prompt]")
    ver = Prompt.ask("[prompt]Versículo (opcional)[/prompt]", default="")
    try:
        resultado = bible.obter_passagem(session_state["versao_biblia"], livro, int(cap), int(ver) if ver else None)
        exibir_passagem(resultado)
    except (ValueError, TypeError): console.print("[erro]Entrada inválida.[/erro]")

def acao_recursos_simbolos():
    console.print(Panel("Símbolos de Fé", style="titulo"))
    doc = Prompt.ask("Documento? [1] CFW [2] CMW [3] BCW", choices=["1", "2", "3"])
    try:
        if doc == "1":
            cap = int(Prompt.ask("Capítulo"))
            sec_str = Prompt.ask("Seção (opcional)", default="")
            sec = int(sec_str) if sec_str else None
            resultado = symbols.obter_simbolo('cfw', cap, sec)
            exibir_simbolos(resultado, 'cfw')
        else:
            tipo = 'cmw' if doc == "2" else 'bcw'
            num = int(Prompt.ask("Número da pergunta"))
            resultado = symbols.obter_simbolo(tipo, num)
            exibir_simbolos(resultado, tipo)
    except (ValueError, TypeError): console.print("[erro]Entrada inválida.[/erro]")


def acao_recursos_salterio():
    console.print(Panel("Saltério", style="titulo"))
    num_salmo = Prompt.ask("Número do Salmo")
    resultados = psaltery.buscar_versoes_salmo(num_salmo)
    if isinstance(resultados, dict) and "erro" in resultados:
        console.print(f"[erro]{resultados['erro']}[/erro]"); return
    while True:
        idx = exibir_lista_de_salmos(resultados)
        if idx is not None:
            exibir_detalhes_do_salmo(resultados[idx])
            if not Confirm.ask("Ver outra versão?", default=True): break
        else: break
    
def acao_relatorios():
    console.print(Panel(Text("Relatórios & Métricas", justify="center")))
    from app.ui.reports_view import display_piety_report, display_resolutions_report
    # display_piety_report(metrics.get_piety_summary())
    # display_resolutions_report(metrics.get_resolution_summary())
    console.print("[info]Módulo de relatórios em construção.[/info]")
    
# --- A Nova Estrutura do Menu Hierárquico ---
MENU_TREE = {
    "_title": "Menu Principal",
    "pessoal": {
        "_title": "Devoção Pessoal",
        "meditacao": acao_meditacao_guiada,
        "resolucoes": { "_title": "Minhas Resoluções", "revisar": acao_resolucoes_revisar_random, "focada": acao_resolucoes_revisar_focada, "listar": acao_resolucoes_listar, "add": acao_resolucoes_add },
        "jejum": { "_title": "Jejum", "iniciar": acao_jejum_iniciar, "concluir": acao_jejum_concluir, },
        "domingo": { "_title": "Dia do Senhor", "preparar": acao_domingo_preparar, "guardar": acao_domingo_guardar }
    },
    "igreja": {
        "_title": "Atividades da Igreja",
        "registros": { "_title": "Registros (Sermões, Estudos, etc)", "add": acao_registros_add, "listar": acao_registros_listar }
    },
    "recursos": {
        "_title": "Recursos & Consultas",
        "biblia": acao_recursos_biblia,
        "simbolos": acao_recursos_simbolos,
        "salterio": acao_recursos_salterio
    },
    "relatorios": acao_relatorios,
}

# --- O Loop Interativo Final ---

def display_current_menu(path, current_node):
    title = current_node.get("_title", "Menu")
    menu_table = Table(title=f"[Menu: {title}]", box=None, padding=(0, 2))
    menu_table.add_column("Comando", style="yellow"); menu_table.add_column("Descrição")
    for key, value in current_node.items():
        if key.startswith("_"): continue
        desc = value.get("_title") if isinstance(value, dict) else value.__name__.replace("acao_", "").replace("_", " ").title()
        menu_table.add_row(key, desc)
    console.print(Padding(menu_table, (1, 2)))

def iniciar_menu_interativo():
    session_state = {"versao_biblia": VERSAO_BIBLIA_PADRAO}
    path = []
    
    db_manager.start()

    try:
        while True:
            console.clear()
            console.print(Panel(Text("Cyber-Puritano", justify="center"), border_style="painel_borda"))
            console.print(render_status_panel())

            current_node = MENU_TREE
            for p in path: current_node = current_node.get(p, {})
            display_current_menu(path, current_node)

            prompt_path = "/".join(path)
            prompt_text = f"[prompt]{prompt_path}>[/prompt] " if path else "[prompt]>[/prompt] "
            
            user_input = Prompt.ask(prompt_text, default="").lower().strip()
            if not user_input: continue

            if user_input.upper() in VERSOES_BIBLIA_DISPONIVEIS:
                session_state["versao_biblia"] = user_input.upper()
                console.print(f"Versão da Bíblia alterada para [sucesso]{session_state['versao_biblia']}[/sucesso].")
                Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
                continue

            parts = user_input.split()
            
            if parts[0] in ("sair", "exit", "quit", "q"):
                break
            if parts[0] in ("voltar", "..", "v"):
                if path: path.pop()
                continue
            if parts[0] in ("ajuda", "menu", "help", "ls"):
                continue

            node_to_process = MENU_TREE
            for p in path: node_to_process = node_to_process.get(p, {})

            temp_path = list(path)
            found_action = False
            for i, part in enumerate(parts):
                if part in node_to_process:
                    target = node_to_process[part]
                    if isinstance(target, dict):
                        node_to_process = target
                        temp_path.append(part)
                        if i == len(parts) - 1:
                            path = temp_path
                    else:
                        console.clear()
                        if part == "biblia": target(session_state)
                        else: target()
                        Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
                        found_action = True
                        break
                else:
                    console.print(f"[erro]Comando '{part}' não encontrado em '/{"/".join(temp_path)}'.[/erro]")
                    Prompt.ask("\n[info]Pressione Enter para continuar...[/info]")
                    found_action = True
                    break
            
            if not found_action and path != temp_path:
                path = temp_path

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        console.print(Panel("[sucesso]Soli Deo Gloria![/sucesso]"))
        db_manager.close()
