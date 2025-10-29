# app/ui/actions.py
# Versão FINAL E CORRIGIDA - Ajuste no import de resolution_view.

from datetime import date
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.box import ROUNDED

# --- Importações de Models (Lógica de Dados) ---
from app.models import bible, psaltery, symbols
from app.models.record import RecordManager
from app.models.resolution import ResolutionManager
from app.models.piety import PiedadeManager
from app.models.sunday import SundayManager
from app.models.fasting import FastingManager

# --- Importações de Views (Lógica de Apresentação) ---
from app.ui.bible_view import exibir_passagem, mostrar_tabela_livros
from app.ui.record_view import prompt_novo_registro, exibir_lista_registros, exibir_detalhes_registro
# A LINHA ABAIXO FOI CORRIGIDA:
from app.ui.resolution_view import prompt_nova_resolucao, exibir_lista_resolucoes, exibir_resolucao_para_revisao
from app.ui.symbols_view import exibir_simbolos
from app.ui.psaltery_view import exibir_lista_de_salmos, exibir_detalhes_do_salmo
from app.ui.piety_view import prompt_registro_diario
from app.reports import metrics
from app.ui.reports_view import display_piety_report, display_resolutions_report

# --- Importações do Core (Núcleo) ---
from app.core.theme import console
from app.core.config import VERSOES_BIBLIA_DISPONIVEIS

# --- Estado da Sessão ---
SESSION_STATE = {"versao_biblia": "NAA"}

# --- Funções de Ação (Uma para cada comando) ---

def do_help(args):
    """Mostra uma ajuda detalhada e organizada sobre os comandos usando tabelas."""
    console.print("\n[bold cyan]GUIA DE COMANDOS DO CYBER-PURITANO[/bold cyan]")
    console.print("Use um comando seguido de seus argumentos. Atalhos estão em [bold cyan]parênteses[/bold cyan].\n")

    # Tabela 1: Devoção e Disciplinas
    t_devocao = Table(
        title="[bold green]Devoção e Disciplinas[/bold green]",
        box=ROUNDED,
        title_justify="center",
        show_header=False
    )
    t_devocao.add_column(style="yellow", no_wrap=True)
    t_devocao.add_column()
    t_devocao.add_row("diario", "Inicia o formulário para o registro diário de piedade.")
    t_devocao.add_row("domingo [bold cyan](dom)[/bold cyan]", "Registra a sua preparação para o Dia do Senhor.")
    t_devocao.add_row("fast [bold cyan](f)[/bold cyan]", "Gerencia os períodos de jejum (`start`, `stop`, `status`).")
    t_devocao.add_row("resolucoes [bold cyan](res)[/bold cyan]", "Gerencia suas resoluções (`add`, `list`, `review`).")
    console.print(t_devocao)

    # Tabela 2: Recursos e Consultas
    t_recursos = Table(
        title="[bold green]Recursos e Consultas[/bold green]",
        box=ROUNDED,
        title_justify="center",
        show_header=False
    )
    t_recursos.add_column(style="yellow", no_wrap=True)
    t_recursos.add_column()
    t_recursos.add_row("biblia [bold cyan](b)[/bold cyan]", "Consulta uma passagem da Bíblia.\n[dim]Ex: b 1jo 3:16[/dim]")
    t_recursos.add_row("simbolos [bold cyan](s)[/bold cyan]", "Consulta Símbolos de Fé (`cfw`, `cmw`, `bcw`).\n[dim]Ex: s cfw 1[/dim]")
    t_recursos.add_row("salterio", "Busca versões cantadas de um Salmo.\n[dim]Ex: salterio 23[/dim]")
    console.print(t_recursos)

    # Tabela 3: Registros e Análises
    t_registros = Table(
        title="[bold green]Registros e Análises[/bold green]",
        box=ROUNDED,
        title_justify="center",
        show_header=False
    )
    t_registros.add_column(style="yellow", no_wrap=True)
    t_registros.add_column()
    t_registros.add_row("registros [bold cyan](r)[/bold cyan]", "Gerencia anotações de sermões e estudos (`add`, `list`).")
    t_registros.add_row("relatorios [bold cyan](rel)[/bold cyan]", "Mostra as métricas de consistência e resoluções.")
    console.print(t_registros)

    # Tabela 4: Sistema
    t_sistema = Table(
        title="[bold green]Sistema[/bold green]",
        box=ROUNDED,
        title_justify="center",
        show_header=False
    )
    t_sistema.add_column(style="yellow", no_wrap=True)
    t_sistema.add_column()
    t_sistema.add_row("config", f"Altera a versão da Bíblia. Disponíveis: {', '.join(VERSOES_BIBLIA_DISPONIVEIS)}.")
    t_sistema.add_row("help [bold cyan](h)[/bold cyan]", "Mostra esta ajuda.")
    t_sistema.add_row("exit [bold cyan](q)[/bold cyan]", "Sai do programa.")
    console.print(t_sistema)

def do_biblia(args):
    """Exibe um texto da Bíblia."""
    if not args:
        mostrar_tabela_livros()
        console.print("\n[info]Uso: biblia <livro> <capítulo>[:<versículo>][/info]")
        return
    livro, cap_vers = args[0], args[1] if len(args) > 1 else "1"
    try:
        if ":" in cap_vers:
            cap_str, ver_str = cap_vers.split(":")
            cap, ver = int(cap_str), int(ver_str)
        else:
            cap, ver = int(cap_vers), None
        resultado = bible.obter_passagem(SESSION_STATE["versao_biblia"], livro, cap, ver)
        exibir_passagem(resultado)
    except (ValueError, IndexError):
        console.print("[erro]Argumentos inválidos. Exemplo: biblia gn 1:1[/erro]")

def do_simbolos(args):
    """Consulta os Símbolos de Fé."""
    if len(args) < 2:
        console.print("[erro]Uso: simbolos <cfw|cmw|bcw> <numero>[/erro]")
        return
    doc, num_str = args[0].lower(), args[1]
    if doc not in ['cfw', 'cmw', 'bcw']:
        console.print(f"[erro]Documento '{doc}' inválido. Use cfw, cmw ou bcw.[/erro]")
        return
    try:
        num = int(num_str)
        sec = int(args[2]) if doc == 'cfw' and len(args) > 2 else None
        resultado = symbols.obter_simbolo(doc, num, sec)
        exibir_simbolos(resultado, doc)
    except ValueError:
        console.print(f"[erro]O número '{num_str}' é inválido.[/erro]")

def do_salterio(args):
    """Busca versões de um Salmo."""
    if not args:
        console.print("[erro]Uso: salterio <numero_do_salmo>[/erro]")
        return
    num_salmo = args[0]
    resultados = psaltery.buscar_versoes_salmo(num_salmo)
    if isinstance(resultados, dict) and "erro" in resultados:
        console.print(f"[erro]{resultados['erro']}[/erro]")
        return
    if not resultados:
        console.print(f"[info]Nenhuma versão encontrada para o Salmo {num_salmo}.[/info]")
        return
    while True:
        idx = exibir_lista_de_salmos(resultados)
        if idx is not None:
            exibir_detalhes_do_salmo(resultados[idx])
            if not Confirm.ask("\n[prompt]Ver outra versão?[/prompt]", default=False): break
        else: break

def do_registros(args):
    """Gerencia anotações de sermões e estudos."""
    mgr, sub_cmd = RecordManager(), args[0] if args else "list"
    if sub_cmd == "add":
        dados = prompt_novo_registro()
        novo_id = mgr.add_record(dados)
        console.print(f"\n[sucesso]Registro #{novo_id} salvo![/sucesso]")
    elif sub_cmd == "list":
        registros = mgr.get_all_records()
        record_id = exibir_lista_registros(registros)
        if record_id and (detalhes := mgr.get_record_by_id(record_id)):
            exibir_detalhes_registro(str(detalhes.id), detalhes)
    else:
        console.print(f"[erro]Sub-comando '{sub_cmd}' desconhecido. Use 'add' ou 'list'.[/erro]")

def do_resolucoes(args):
    """Gerencia resoluções pessoais."""
    mgr, sub_cmd = ResolutionManager(), args[0] if args else "review"
    if sub_cmd == "add":
        dados = prompt_nova_resolucao()
        novo_id = mgr.add_resolution(**dados)
        console.print(f"\n[sucesso]Resolução #{novo_id} registrada![/sucesso]")
    elif sub_cmd == "list":
        resolucoes = [(str(r.id), vars(r)) for r in mgr.get_all_resolutions()]
        exibir_lista_resolucoes(resolucoes)
    elif sub_cmd == "review":
        res = mgr.get_least_reviewed_resolution() or mgr.get_random_resolution()
        if res:
            exibir_resolucao_para_revisao(str(res.id), vars(res), "Revisão")
            mgr.update_review_stats(str(res.id))
        else:
            console.print("[info]Nenhuma resolução para revisar.[/info]")
    else:
        console.print(f"[erro]Sub-comando '{sub_cmd}' desconhecido. Use 'add', 'list' ou 'review'.[/erro]")

def do_diario(args):
    """Registra o diário de piedade para o dia atual."""
    pm = PiedadeManager()
    hoje_str = date.today().isoformat()
    dados = prompt_registro_diario()
    pm.registrar_dia(hoje_str, dados)
    console.print(f"\n[sucesso]Diário de {hoje_str} registrado com sucesso![/sucesso]")

def do_domingo(args):
    """Registra a preparação para o Dia do Senhor."""
    sub_cmd = args[0] if args else "preparar"
    if sub_cmd == "preparar":
        sunday_manager = SundayManager()
        console.print("[titulo]Preparação para o Dia do Senhor[/titulo]")
        checks = {
            "pastor": Confirm.ask("Orou pelo pastor?"), "leitura": Confirm.ask("Leu a passagem do sermão?"),
            "confissao": Confirm.ask("Confessou seus pecados?"), "mundo": Confirm.ask("Deixou as preocupações seculares?"),
            "congregacao": Confirm.ask("Orou pela sua congregação?")
        }
        sunday_manager.log_preparation(date.today().isoformat(), checks)
        console.print("[sucesso]Preparação registrada! Que Deus abençoe seu Dia.[/sucesso]")
    else:
        console.print(f"[erro]Sub-comando '{sub_cmd}' desconhecido. Use 'preparar'.[/erro]")

def do_fast(args):
    """Gerencia os períodos de jejum."""
    fm = FastingManager()
    sub_cmd = args[0] if args else "status"
    
    if sub_cmd == "start":
        if fm.get_active_fast():
            console.print("[erro]Já existe um jejum ativo. Conclua-o antes de iniciar outro.[/erro]")
            return
        purpose = Prompt.ask("[prompt]Qual o propósito do jejum?[/prompt]")
        scripture = Prompt.ask("[prompt]Qual a passagem bíblica de foco?[/prompt]")
        fast_id = fm.start_fast(purpose, scripture)
        console.print(f"[sucesso]Jejum #{fast_id} iniciado![/sucesso]")
    elif sub_cmd == "stop":
        active = fm.get_active_fast()
        if not active:
            console.print("[info]Nenhum jejum ativo para concluir.[/info]")
            return
        reflection = Prompt.ask(f"[prompt]Digite a reflexão sobre o jejum #{active['id']}[/prompt]")
        fm.finish_fast(active['id'], reflection)
        console.print(f"[sucesso]Jejum #{active['id']} concluído.[/sucesso]")
    elif sub_cmd == "status":
        active = fm.get_active_fast()
        if active:
            console.print(f"[info]Jejum ativo iniciado em {active['start_date']}[/info]")
            console.print(f"  └─ [bold]Propósito:[/bold] {active['purpose']}")
        else:
            console.print("[info]Nenhum jejum ativo no momento.[/info]")
    else:
        console.print(f"[erro]Sub-comando '{sub_cmd}' desconhecido. Use 'start', 'stop' ou 'status'.[/erro]")

def do_relatorios(args):
    """Exibe relatórios e métricas de consistência."""
    display_piety_report(metrics.get_piety_summary())
    display_resolutions_report(metrics.get_resolution_summary())

def do_config(args):
    """Muda a versão da Bíblia."""
    if not args or args[0].upper() not in VERSOES_BIBLIA_DISPONIVEIS:
        console.print(f"[erro]Versão inválida. Disponíveis: {', '.join(VERSOES_BIBLIA_DISPONIVEIS)}.[/erro]")
        return
    SESSION_STATE["versao_biblia"] = args[0].upper()
    console.print(f"[sucesso]Versão da Bíblia alterada para {SESSION_STATE['versao_biblia']}.[/sucesso]")


# --- Mapeamento de Comandos ---
COMMAND_MAP = {
    "help": do_help,
    "biblia": do_biblia,
    "simbolos": do_simbolos,
    "salterio": do_salterio,
    "registros": do_registros,
    "resolucoes": do_resolucoes,
    "diario": do_diario,
    "domingo": do_domingo,
    "fast": do_fast,
    "relatorios": do_relatorios,
    "config": do_config,
}
