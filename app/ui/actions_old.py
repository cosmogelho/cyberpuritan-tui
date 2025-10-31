# app/ui/actions.py
import os
import re
import subprocess
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.markup import escape
from app.core.theme import console
from app.models import journal_model, action_item_model, notes_model, bible, symbols, psaltery
from app.core.config import DATA_DIR
from app.reports import metrics

SESSION_STATE = {'versao_biblia': 'NAA'}

BIBLE_ABBREVIATIONS = {
    'gn': 'Gênesis', 'ex': 'Êxodo', 'lv': 'Levítico', 'nm': 'Números', 'dt': 'Deuteronômio',
    'js': 'Josué', 'jz': 'Juízes', 'rt': 'Rute', '1sm': '1 Samuel', '2sm': '2 Samuel',
    '1rs': '1 Reis', '2rs': '2 Reis', '1cr': '1 Crônicas', '2cr': '2 Crônicas', 'ed': 'Esdras',
    'ne': 'Neemias', 'et': 'Ester', 'jó': 'Jó', 'sl': 'Salmos', 'pv': 'Provérbios',
    'ec': 'Eclesiastes', 'ct': 'Cantares', 'is': 'Isaías', 'jr': 'Jeremias', 'lm': 'Lamentações',
    'ez': 'Ezequiel', 'dn': 'Daniel', 'os': 'Oséias', 'jl': 'Joel', 'am': 'Amós', 'ob': 'Obadias',
    'jn': 'Jonas', 'mq': 'Miquéias', 'na': 'Naum', 'hc': 'Habacuque', 'sf': 'Sofonias', 'ag': 'Ageu',
    'zc': 'Zacarias', 'ml': 'Malaquias', 'mt': 'Mateus', 'mc': 'Marcos', 'lc': 'Lucas',
    'jo': 'João', 'at': 'Atos', 'rm': 'Romanos', '1co': '1 Coríntios', '2co': '2 Coríntios',
    'gl': 'Gálatas', 'ef': 'Efésios', 'fp': 'Filipenses', 'cl': 'Colossenses',
    '1ts': '1 Tessalonicenses', '2ts': '2 Tessalonicenses', '1tm': '1 Timóteo',
    '2tm': '2 Timóteo', 'tt': 'Tito', 'fm': 'Filemom', 'hb': 'Hebreus', 'tg': 'Tiago',
    '1pe': '1 Pedro', '2pe': '2 Pedro', '1jo': '1 João', '2jo': '2 João', '3jo': '3 João',
    'jd': 'Judas', 'ap': 'Apocalipse'
}

def _clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def _parse_reference(ref_string: str):
    pattern_ch_vs = re.compile(r'^\s*([1-3]?\s*.*?)\s*(\d+):(\d+)(?:-(\d+))?\s*$')
    match = pattern_ch_vs.match(ref_string)
    if match:
        groups = match.groups()
        return groups[0].strip(), int(groups[1]), int(groups[2]), int(groups[3]) if groups[3] else None
    pattern_vs_only = re.compile(r'^\s*([1-3]?\s*.*?)\s*(\d+)(?:-(\d+))?\s*$')
    match = pattern_vs_only.match(ref_string)
    if match:
        groups = match.groups()
        return groups[0].strip(), 1, int(groups[1]), int(groups[2]) if groups[2] else None
    return None

def _handle_help(args):
    table = Table(title="Ajuda - Comandos Cyber-Puritano", style="titulo")
    table.add_column("Comando", style="info", no_wrap=True); table.add_column("Alias", style="yellow"); table.add_column("Descrição", style="white")
    table.add_row("journal", "j", "Diário. Subcomandos: add, view, find <tag>.")
    table.add_row("actions", "a", "Ações. Subcomandos: add, view, update. Tipos: res, ora.")
    table.add_row("notes", "n", "Notas de Estudo. Subcomandos: add, view, read <id>.")
    table.add_row("bible", "b", "Bíblia. Ex: 'b jo 3:16-18', 'b Judas 3', 'b list'.")
    table.add_row("symbols", "s", "Símbolos de Fé. Ex: 's cfw 1.1', 's cmw 10'.")
    table.add_row("psaltery", "p", "Saltério. Ex: 'p 15A [view|meta|letra|play [i|c]]', 'p list'.")
    table.add_row("reports", "rep", "Exibe um relatório de métricas da última semana.")
    table.add_row("clear", "cls", "Limpa a tela.")
    table.add_row("exit", "q", "Sai da aplicação.")
    console.print(table)

def _handle_journal(args):
    if not args or args[0] not in ['add', 'view', 'find']: console.print("[erro]Uso: journal [add|view|find <tag>]"); return
    sub_cmd = args[0]
    if sub_cmd == 'add':
        console.print("[info]Escreva sua entrada no diário. Pressione Ctrl+D (Linux/Mac) ou Ctrl+Z+Enter (Windows) quando terminar.")
        content = "\n".join(iter(lambda: input(), ''));
        if not content.strip(): console.print("[warning]Entrada vazia. Nada foi salvo."); return
        tags = console.input("Tags (separadas por vírgula): ")
        journal_model.add_entry(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), content, tags)
        console.print("[info]Entrada salva com sucesso!")
    elif sub_cmd == 'view':
        entries = journal_model.get_all_entries()
        for entry in entries: console.print(Panel(escape(entry['content']), title=f"[titulo]{entry['entry_date']}[/titulo] | Tags: [yellow]{entry['tags']}[/yellow]", border_style="cyan"))
    elif sub_cmd == 'find':
        if len(args) < 2: console.print("[erro]Uso: journal find <tag>"); return
        tag = args[1]
        entries = journal_model.get_entries_by_tag(tag)
        for entry in entries: console.print(Panel(escape(entry['content']), title=f"[titulo]{entry['entry_date']}[/titulo] | Tags: [yellow]{entry['tags']}[/yellow]", border_style="cyan"))

def _handle_actions(args):
    if len(args) < 2 or args[0] not in ['add', 'view', 'update'] or args[1] not in ['res', 'ora']: console.print("[erro]Uso: actions [add|view|update] [res|ora] [argumentos...]"); return
    sub_cmd, item_type_arg = args[0], args[1]
    item_type = 'Resolução' if item_type_arg == 'res' else 'Pedido de Oração'
    if sub_cmd == 'add':
        text = " ".join(args[2:]);
        if not text: text = console.input(f"Texto para nova {item_type}: ")
        if not text.strip(): console.print("[warning]Texto vazio. Nada foi salvo."); return
        action_item_model.add_item(item_type, text, datetime.now().strftime('%Y-%m-%d %H:%M:%S')); console.print(f"[info]{item_type} adicionada com sucesso!")
    elif sub_cmd == 'view':
        items = action_item_model.get_items(item_type); table = Table(title=f"Lista de {item_type}s")
        table.add_column("ID", style="cyan"); table.add_column("Texto", style="white"); table.add_column("Status", style="yellow")
        for item in items: table.add_row(str(item['id']), item['text'], item['status'])
        console.print(table)
    elif sub_cmd == 'update':
        try:
            item_id = int(args[2]); new_status = args[3]
            action_item_model.update_item_status(item_id, new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S')); console.print(f"[info]Status do item {item_id} atualizado para '{new_status}'.")
        except (IndexError, ValueError): console.print("[erro]Uso: actions update [res|ora] <id> <novo_status>")

def _handle_notes(args):
    if not args or args[0] not in ['add', 'view', 'read']: console.print("[erro]Uso: notes [add|view|read <id>]"); return
    sub_cmd = args[0]
    if sub_cmd == 'add':
        title = console.input("Título da nota: ")
        if not title.strip(): console.print("[warning]Título vazio. Operação cancelada."); return
        console.print("[info]Conteúdo da nota (Ctrl+D/Ctrl+Z+Enter para terminar):")
        content = "\n".join(iter(lambda: input(), ''))
        if not content.strip(): console.print("[warning]Conteúdo vazio. Nada foi salvo."); return
        tags = console.input("Tags (separadas por vírgula): ")
        notes_model.add_note(title, content, tags, datetime.now().strftime('%Y-%m-%d %H:%M:%S')); console.print("[info]Nota salva com sucesso!")
    elif sub_cmd == 'view':
        notes = notes_model.get_all_notes(); table = Table(title="Notas de Estudo (Commonplace Book)")
        table.add_column("ID", style="cyan"); table.add_column("Título", style="white"); table.add_column("Tags", style="yellow")
        for note in notes: table.add_row(str(note['id']), note['title'], note['tags'])
        console.print(table)
    elif sub_cmd == 'read':
        try:
            note_id = int(args[1]); note = notes_model.get_note_by_id(note_id)
            if note: console.print(Panel(escape(note['content']), title=f"[titulo]{note['title']}[/titulo] | Tags: [yellow]{note['tags']}[/yellow]", border_style="cyan"))
            else: console.print("[erro]Nota não encontrada.")
        except (IndexError, ValueError): console.print("[erro]Uso: notes read <id>")

def _handle_bible(args):
    if not args: console.print("[erro]Uso: 'b <referência>' ou 'b list'."); return
    if args[0].lower() == 'list':
        books = bible.get_all_book_names()
        table = Table(title="Livros da Bíblia e Abreviações Comuns")
        table.add_column("Livro", style="white"); table.add_column("Abrev.", style="yellow")
        abbrev_map = {v: k for k, v in BIBLE_ABBREVIATIONS.items()}
        # Ajustado para layout de duas colunas
        num_books = len(books)
        mid_point = (num_books + 1) // 2
        for i in range(mid_point):
            book1_name = books[i]['name']
            abbrev1 = abbrev_map.get(book1_name, "-")
            col1 = f"{book1_name} ({abbrev1})"
            
            col2 = ""
            if i + mid_point < num_books:
                book2_name = books[i + mid_point]['name']
                abbrev2 = abbrev_map.get(book2_name, "-")
                col2 = f"{book2_name} ({abbrev2})"
            table.add_row(col1, col2)
        console.print(table)
        return
    ref_string = " ".join(args)
    parsed_ref = _parse_reference(ref_string)
    if not parsed_ref: console.print("[erro]Formato de referência inválido. Use 'Livro Cap:Ver' ou 'Livro Ver'."); return
    book_input, chapter, start_verse, end_verse = parsed_ref
    book_full_name = BIBLE_ABBREVIATIONS.get(book_input.lower().replace(" ", ""))
    if not book_full_name:
        if book_input.title() in BIBLE_ABBREVIATIONS.values():
            book_full_name = book_input.title()
        else:
            console.print(f"[erro]Livro '{book_input}' não reconhecido. Use 'b list' para ver as opções.[/erro]"); return
    verses = bible.get_verses(book_full_name, chapter, start_verse, end_verse)
    if not verses: console.print("[erro]Referência não encontrada. Verifique o capítulo e os versículos."); return
    console.print(f"\n[titulo]--- {book_full_name} {chapter} ---[/titulo]")
    for verse in verses: console.print(f"[yellow][{verse['verse']}][/yellow] {escape(verse['text'])}")

def _handle_symbols(args):
    if not args: console.print("[erro]Uso: symbols [cfw|cmw|bcw] [referência]"); return
    doc = args[0].lower(); ref = " ".join(args[1:])
    if doc == 'cfw':
        try:
            chap, sec = map(int, ref.split('.')); article = symbols.get_cfw_article(chap, sec)
            if article: console.print(Panel(escape(article['text']), title=f"[titulo]CFW {chap}.{sec}: {article['title']}[/titulo]"))
            else: console.print("[erro]Artigo não encontrado.")
        except ValueError: console.print("[erro]Formato para CFW é 'capitulo.secao'.")
    elif doc in ['cmw', 'bcw']:
        try:
            qid = int(ref); q_func = symbols.get_cmw_question if doc == 'cmw' else symbols.get_bcw_question
            q = q_func(qid)
            if q: console.print(Panel(f"[info]P:[/info] {escape(q['question'])}\n\n[info]R:[/info] {escape(q['answer'])}", title=f"[titulo]{doc.upper()} Pergunta {qid}[/titulo]"))
            else: console.print("[erro]Pergunta não encontrada.")
        except ValueError: console.print("[erro]Referência para catecismos deve ser um número.")
    else: console.print("[erro]Documento inválido. Use 'cfw', 'cmw', ou 'bcw'.")

# ============================================================================
# (CORRIGIDO) HANDLER DO SALTÉRIO COM ACESSO CORRETO A DADOS E QUERY CORRIGIDA
# ============================================================================
def _handle_psaltery(args):
    if not args or args[0].lower() == 'list':
        all_psalms = psaltery.get_all_psalms_references()
        
        table = Table(title="Saltério - Lista de Salmos")
        table.add_column("Referência", style="cyan", no_wrap=True)
        table.add_column("Música", style="yellow", justify="center")
        
        if not all_psalms:
            console.print("[warning]Nenhum salmo encontrado na base de dados.[/warning]")
            return

        def sort_key(p):
            match = re.match(r'(\d+)([A-Z]*)', p['referencia'])
            if match:
                num, letter = match.groups()
                return int(num), letter
            return 999, p['referencia'] 

        sorted_psalms = sorted(all_psalms, key=sort_key)
        
        last_psalm_num = -1
        for psalm in sorted_psalms:
            current_psalm_num = sort_key(psalm)[0]
            if last_psalm_num != -1 and current_psalm_num != last_psalm_num:
                table.add_row("──────────", "──", style="dim")
            last_psalm_num = current_psalm_num
            
            # (CORRIGIDO) Acesso aos dados usando colchetes e verificação de existência da chave
            music_indicator = ""
            has_instrumental = 'instrumental' in psalm.keys() and psalm['instrumental']
            has_capela = 'à_capela' in psalm.keys() and psalm['à_capela']
            
            if has_instrumental and has_capela:
                music_indicator = "A"
            elif has_instrumental:
                music_indicator = "I"
            elif has_capela:
                music_indicator = "C"

            table.add_row(psalm['referencia'], music_indicator)
            
        console.print(table)
        console.print("\n[info]I: Instrumental | C: À Capela | A: Ambos[/info]")
        return

    referencia = args[0].upper()
    sub_cmd = args[1].lower() if len(args) > 1 else 'view'
    psalm = psaltery.get_psalm_by_reference(referencia)

    if not psalm:
        console.print(f"[erro]Salmo com referência '{referencia}' não encontrado.")
        return

    def show_meta():
        table = Table(title=f"Metadados do Salmo {psalm['referencia']}", box=None, show_header=False)
        table.add_column(style="info"); table.add_column(style="white")
        table.add_row("Referência:", psalm['referencia']); table.add_row("Tipo:", psalm['tipo']); table.add_row("Métrica:", psalm['metrica']); table.add_row("Melodia:", psalm['melodia'])
        table.add_row("Compositor:", psalm['compositor']); table.add_row("Harmonização:", psalm['harmonizacao']); console.print(table)

    def show_letra():
        console.print(f"\n[titulo]--- Salmo {psalm['referencia']} - Letra ---[/titulo]")
        console.print(escape(psalm['letra']))

    def play_music(psalm_data, requested_version=None):
        options = []
        if psalm_data['instrumental']: options.append(("Instrumental", psalm_data['instrumental']))
        if psalm_data['à_capela']: options.append(("À Capela", psalm_data['à_capela']))

        if not options:
            console.print(f"[warning]O Salmo {referencia} não possui áudio cadastrado.[/warning]")
            return

        chosen_path = ""
        if requested_version:
            if requested_version in ["instrumental", "i"]:
                path = next((p for name, p in options if name == "Instrumental"), None)
                if path: chosen_path = path
                else: console.print("[erro]Versão instrumental não disponível para este salmo.[/erro]"); return
            elif requested_version in ["capela", "c"]:
                path = next((p for name, p in options if name == "À Capela"), None)
                if path: chosen_path = path
                else: console.print("[erro]Versão à capela não disponível para este salmo.[/erro]"); return
        
        if not chosen_path:
            if len(options) == 1:
                chosen_path = options[0][1]
                console.print(f"[info]Tocando a única versão disponível: {options[0][0]}[/info]")
            else:
                console.print("[prompt]Qual versão deseja ouvir?[/prompt]")
                for i, (name, _) in enumerate(options): console.print(f"  [cyan]({i+1})[/cyan] {name}")
                while True:
                    choice_str = console.input("[prompt]Sua escolha (ou 'q' para sair): [/prompt]")
                    if choice_str.lower() in ['q', 'sair']: return
                    try:
                        choice_idx = int(choice_str)
                        if 1 <= choice_idx <= len(options):
                            chosen_path = options[choice_idx - 1][1]
                            break
                        else: console.print("[erro]Escolha inválida.[/erro]")
                    except ValueError: console.print("[erro]Por favor, insira um número.[/erro]")
        
        full_path = os.path.join(DATA_DIR, chosen_path)

        if not os.path.exists(full_path):
            console.print(f"[erro]Arquivo de áudio não encontrado em: {full_path}[/erro]")
            return
            
        process = None
        try:
            console.print(f"[info]Iniciando mpv...[/info]")
            process = subprocess.Popen(['mpv', full_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            console.input("[prompt]Tocando... Pressione Enter para parar.[/prompt]")
        except FileNotFoundError:
            console.print("[erro]Comando 'mpv' não encontrado. Instale o mpv para usar esta função.[/erro]")
        except Exception as e:
            console.print(f"[erro]Ocorreu um erro inesperado ao tentar tocar: {e}[/erro]")
        finally:
            if process and process.poll() is None:
                console.print("[info]Parando a reprodução.[/info]")
                process.terminate()

    if sub_cmd == 'view': show_meta(); show_letra()
    elif sub_cmd == 'meta': show_meta()
    elif sub_cmd == 'letra': show_letra()
    elif sub_cmd == 'play':
        requested_version_arg = args[2].lower() if len(args) > 2 else None
        play_music(psalm, requested_version=requested_version_arg)
    elif sub_cmd == 'all':
        show_meta(); show_letra()
        if psalm['instrumental'] or psalm['à_capela']:
            console.input("\n[prompt]Pressione Enter para ver as opções de áudio...[/prompt]")
            play_music(psalm)
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
