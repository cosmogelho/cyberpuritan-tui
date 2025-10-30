# app/ui/actions.py
import os
import re
import subprocess
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.markup import escape  # <- ADIÇÃO CRÍTICA PARA A CORREÇÃO
from app.core.theme import console
from app.reports import metrics
from app.models import journal_model, action_item_model, notes_model, bible, symbols, psaltery

SESSION_STATE = {'versao_biblia': 'NAA'}

def _clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def _parse_reference(ref_string: str):
    """Analisa uma string de referência bíblica e retorna as partes."""
    pattern = re.compile(r'^\s*([1-3]?\s*\w+)\s*(\d+):(\d+)(?:-(\d+))?\s*$')
    match = pattern.match(ref_string)
    if not match: return None
    groups = match.groups()
    return groups[0].strip(), int(groups[1]), int(groups[2]), int(groups[3]) if groups[3] else None

# --- HANDLERS DE COMANDO ---

def _handle_help(args):
    """Exibe a ajuda com os comandos e aliases."""
    table = Table(title="Ajuda - Comandos Cyber-Puritano", style="titulo")
    table.add_column("Comando", style="info", no_wrap=True)
    table.add_column("Alias", style="yellow")
    table.add_column("Descrição", style="white")
    
    table.add_row("journal", "j", "Diário. Subcomandos: add, view, find <tag>.")
    table.add_row("actions", "a", "Ações. Subcomandos: add, view, update. Tipos: res, ora.")
    table.add_row("notes", "n", "Notas de Estudo. Subcomandos: add, view, read <id>.")
    table.add_row("bible", "b", "Busca passagens bíblicas. Ex: 'b jo 3:16-18'.")
    table.add_row("symbols", "s", "Consulta Símbolos de Fé. Ex: 's cfw 1.1', 's cmw 10'.")
    table.add_row("psaltery", "p", "Saltério. Ex: 'p 15A [view|meta|letra|play|all]', 'p list'.")
    table.add_row("reports", "rep", "Exibe um relatório de métricas da última semana.")
    table.add_row("clear", "cls", "Limpa a tela.")
    table.add_row("exit", "q", "Sai da aplicação.")
    console.print(table)

def _handle_journal(args):
    """Lida com os subcomandos do diário."""
    if not args or args[0] not in ['add', 'view', 'find']:
        console.print("[erro]Uso: journal [add|view|find <tag>]")
        return
    
    sub_cmd = args[0]
    if sub_cmd == 'add':
        console.print("[info]Escreva sua entrada no diário. Pressione Ctrl+D (Linux/Mac) ou Ctrl+Z+Enter (Windows) quando terminar.")
        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass
        content = "\n".join(content_lines)
        if not content.strip():
            console.print("[warning]Entrada vazia. Nada foi salvo.")
            return
        tags = console.input("Tags (separadas por vírgula): ")
        journal_model.add_entry(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), content, tags)
        console.print("[info]Entrada salva com sucesso!")

    elif sub_cmd == 'view':
        entries = journal_model.get_all_entries()
        for entry in entries:
            console.print(Panel(
                entry['content'], 
                title=f"[titulo]{entry['entry_date']}[/titulo] | Tags: [yellow]{entry['tags']}[/yellow]",
                border_style="cyan"
            ))
    elif sub_cmd == 'find':
        if len(args) < 2:
            console.print("[erro]Uso: journal find <tag>")
            return
        tag = args[1]
        entries = journal_model.get_entries_by_tag(tag)
        for entry in entries:
            console.print(Panel(
                entry['content'], 
                title=f"[titulo]{entry['entry_date']}[/titulo] | Tags: [yellow]{entry['tags']}[/yellow]",
                border_style="cyan"
            ))

def _handle_actions(args):
    """Lida com resoluções e pedidos de oração."""
    if len(args) < 2 or args[0] not in ['add', 'view', 'update'] or args[1] not in ['res', 'ora']:
        console.print("[erro]Uso: actions [add|view|update] [res|ora] [argumentos...]")
        return
    
    sub_cmd, item_type_arg = args[0], args[1]
    item_type = 'Resolução' if item_type_arg == 'res' else 'Pedido de Oração'

    if sub_cmd == 'add':
        text = " ".join(args[2:])
        if not text:
            text = console.input(f"Texto para nova {item_type}: ")
        if not text.strip():
            console.print("[warning]Texto vazio. Nada foi salvo.")
            return
        action_item_model.add_item(item_type, text, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        console.print(f"[info]{item_type} adicionada com sucesso!")

    elif sub_cmd == 'view':
        items = action_item_model.get_items(item_type)
        table = Table(title=f"Lista de {item_type}s")
        table.add_column("ID", style="cyan")
        table.add_column("Texto", style="white")
        table.add_column("Status", style="yellow")
        for item in items:
            table.add_row(str(item['id']), item['text'], item['status'])
        console.print(table)

    elif sub_cmd == 'update':
        try:
            item_id = int(args[2])
            new_status = args[3]
            action_item_model.update_item_status(item_id, new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            console.print(f"[info]Status do item {item_id} atualizado para '{new_status}'.")
        except (IndexError, ValueError):
            console.print("[erro]Uso: actions update [res|ora] <id> <novo_status>")

def _handle_notes(args):
    """Lida com o Commonplace Book (Notas)."""
    if not args or args[0] not in ['add', 'view', 'read']:
        console.print("[erro]Uso: notes [add|view|read <id>]")
        return

    sub_cmd = args[0]
    if sub_cmd == 'add':
        title = console.input("Título da nota: ")
        if not title.strip():
            console.print("[warning]Título vazio. Operação cancelada.")
            return
        console.print("[info]Conteúdo da nota (Ctrl+D/Ctrl+Z+Enter para terminar):")
        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass
        content = "\n".join(content_lines)
        if not content.strip():
            console.print("[warning]Conteúdo vazio. Nada foi salvo.")
            return
        tags = console.input("Tags (separadas por vírgula): ")
        notes_model.add_note(title, content, tags, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        console.print("[info]Nota salva com sucesso!")
    
    elif sub_cmd == 'view':
        notes = notes_model.get_all_notes()
        table = Table(title="Notas de Estudo (Commonplace Book)")
        table.add_column("ID", style="cyan")
        table.add_column("Título", style="white")
        table.add_column("Tags", style="yellow")
        for note in notes:
            table.add_row(str(note['id']), note['title'], note['tags'])
        console.print(table)

    elif sub_cmd == 'read':
        try:
            note_id = int(args[1])
            note = notes_model.get_note_by_id(note_id)
            if note:
                console.print(Panel(
                    note['content'],
                    title=f"[titulo]{note['title']}[/titulo] | Tags: [yellow]{note['tags']}[/yellow]",
                    border_style="cyan"
                ))
            else:
                console.print("[erro]Nota não encontrada.")
        except (IndexError, ValueError):
            console.print("[erro]Uso: notes read <id>")

def _handle_bible(args):
    """Busca e exibe passagens da Bíblia."""
    ref_string = " ".join(args)
    parsed_ref = _parse_reference(ref_string)
    if not parsed_ref:
        console.print("[erro]Formato de referência inválido. Ex: 'jo 3:16-18'")
        return
    
    book, chapter, start_verse, end_verse = parsed_ref
    verses = bible.get_verses(book, chapter, start_verse, end_verse)
    if not verses:
        console.print("[erro]Referência não encontrada.")
        return
        
    full_book_name = verses[0]['book_name']
    console.print(f"\n[titulo]--- {full_book_name} {chapter} ---[/titulo]")
    for verse in verses:
        console.print(f"[yellow][{verse['verse']}][/yellow] {verse['text']}")

def _handle_symbols(args):
    """Busca nos Símbolos de Fé."""
    if not args:
        console.print("[erro]Uso: symbols [cfw|cmw|bcw] [referência]")
        return
    
    doc = args[0].lower()
    ref = " ".join(args[1:])
    
    if doc == 'cfw':
        try:
            chap, sec = map(int, ref.split('.'))
            article = symbols.get_cfw_article(chap, sec)
            if article:
                console.print(Panel(article['text'], title=f"[titulo]CFW {chap}.{sec}: {article['title']}[/titulo]"))
            else: console.print("[erro]Artigo não encontrado.")
        except ValueError: console.print("[erro]Formato para CFW é 'capitulo.secao'.")
    
    elif doc in ['cmw', 'bcw']:
        try:
            qid = int(ref)
            q_func = symbols.get_cmw_question if doc == 'cmw' else symbols.get_bcw_question
            q = q_func(qid)
            if q:
                console.print(Panel(f"[info]P:[/info] {q['question']}\n\n[info]R:[/info] {q['answer']}", title=f"[titulo]{doc.upper()} Pergunta {qid}[/titulo]"))
            else: console.print("[erro]Pergunta não encontrada.")
        except ValueError: console.print("[erro]Referência para catecismos deve ser um número.")
    else:
        console.print("[erro]Documento inválido. Use 'cfw', 'cmw', ou 'bcw'.")

def _handle_psaltery(args):
    """
    Busca no Saltério, com controle granular, exibição fiel e player MPV.
    """
    if not args or args[0] == 'list':
        refs = psaltery.get_all_psalms_references()
        table = Table(title="Saltério - Todos os Salmos")
        table.add_column("Referência", style="cyan", no_wrap=True)
        table.add_column("Métrica/Melodia", style="yellow")
        for ref in refs:
            table.add_row(ref['referencia'], f"{ref['metrica']} - {ref['melodia']}")
        console.print(table)
        return

    referencia = args[0].upper()
    sub_cmd = args[1].lower() if len(args) > 1 else 'view'

    psalm = psaltery.get_psalm_by_reference(referencia)
    if not psalm:
        console.print(f"[erro]Salmo com referência '{referencia}' não encontrado.")
        return

    def show_meta():
        table = Table(title=f"Metadados do Salmo {psalm['referencia']}", box=None, show_header=False)
        table.add_column(style="info")
        table.add_column(style="white")
        table.add_row("Referência:", psalm['referencia'])
        table.add_row("Tipo:", psalm['tipo'])
        table.add_row("Métrica:", psalm['metrica'])
        table.add_row("Melodia:", psalm['melodia'])
        table.add_row("Compositor:", psalm['compositor'])
        table.add_row("Harmonização:", psalm['harmonizacao'])
        console.print(table)

    def show_letra():
        console.print(f"\n[titulo]--- Salmo {psalm['referencia']} - Letra ---[/titulo]")
        # ============================================================================
        # CORREÇÃO DEFINITIVA: Usando escape() para imprimir o texto literalmente.
        # ============================================================================
        console.print(escape(psalm['letra']))

    def play_music():
        url = psalm['video_url']
        if not url:
            console.print(f"[warning]O Salmo {referencia} não possui um link de áudio/vídeo cadastrado.[/warning]")
            return
        
        try:
            console.print(f"[info]Iniciando mpv para tocar a melodia do Salmo {referencia}...[/info]")
            subprocess.run(['mpv', '--no-video', url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            console.print("[erro]Comando 'mpv' não encontrado. Por favor, instale o mpv para usar esta função.[/erro]")
        except subprocess.CalledProcessError as e:
            console.print(f"[erro]O mpv encontrou um erro: {e}[/erro]")
        except Exception as e:
            console.print(f"[erro]Ocorreu um erro inesperado ao tentar tocar: {e}[/erro]")

    if sub_cmd == 'view':
        show_meta()
        show_letra()
    elif sub_cmd == 'meta':
        show_meta()
    elif sub_cmd == 'letra':
        show_letra()
    elif sub_cmd == 'play':
        play_music()
    elif sub_cmd == 'all':
        show_meta()
        show_letra()
        if psalm['video_url']:
            console.input("\n[prompt]Pressione Enter para tocar a melodia...[/prompt]")
            play_music()
    else:
        console.print(f"[erro]Subcomando '{sub_cmd}' inválido. Use [view|meta|letra|play|all].")

# --- MAPA DE COMANDOS ---
COMMAND_MAP = {
    "help": _handle_help,
    "journal": _handle_journal,
    "actions": _handle_actions,
    "notes": _handle_notes,
    "bible": _handle_bible,
    "symbols": _handle_symbols,
    "psaltery": _handle_psaltery,
    "reports": lambda args: metrics.generate_weekly_report(),
    "clear": lambda args: _clear_screen()
}
