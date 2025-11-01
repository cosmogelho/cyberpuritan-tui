# app/ui/actions.py (VERSÃO FINAL COM PAGER)
import os
import re
import math
import subprocess
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text
from app.core.theme import console
from app.models import journal_model, psaltery
from app.core.config import DATA_DIR

# --- MÓDULO DIÁRIO ---
def adicionar_entrada_diario():
    console.print("[info]Escreva sua entrada. Pressione Ctrl+D (Linux/Mac) ou Ctrl+Z+Enter (Windows) para salvar.[/info]")
    content = "\n".join(iter(lambda: input(), ''))
    if not content.strip():
        return None, "[warning]Entrada vazia. Nada foi salvo.[/warning]"
    tags = Prompt.ask("Tags (separadas por vírgula)")
    journal_model.add_entry(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), content, tags)
    return None, "[info]Entrada salva com sucesso![/info]"

def ver_diario():
    entries = journal_model.get_all_entries()
    if not entries:
        return Panel(Align.center("[italic]Nenhuma entrada no diário ainda.[/italic]", vertical="middle"))
    
    paineis_conteudo = []
    for entry in entries:
        paineis_conteudo.append(Panel(Text(entry['content']), title=f"[bold cyan]{entry['date']}[/bold cyan] | Tags: [yellow]{entry['tags']}[/yellow]", border_style="cyan"))
    
    return Panel(Group(*paineis_conteudo), title="[bold]Todas as Entradas[/bold]", border_style="dim")

def processar_comandos_diario(comando, args):
    if comando == 'ver':
        return ver_diario()
    elif comando == 'buscar':
        return Panel(Align.center("[warning]Busca ainda não implementada.[/warning]", vertical="middle"))
    else:
        return f"[erro]Comando '{comando}' desconhecido para o Diário.[/erro]"

# --- MÓDULO SALTÉRIO ---
def listar_salmos(pagina_atual=1, itens_por_pagina=10):
    all_psalms = psaltery.get_all_psalms_references()
    geneva_psalms = [p for p in all_psalms if p['referencia'].endswith('A')]

    if not geneva_psalms:
        return Panel(Align.center("[italic]Nenhum salmo encontrado.[/italic]", vertical="middle")), 1

    def sort_key(p):
        match = re.match(r'(\d+)', p['referencia'])
        return int(match.group(1)) if match else 999
    
    sorted_psalms = sorted(geneva_psalms, key=sort_key)
    
    total_paginas = math.ceil(len(sorted_psalms) / itens_por_pagina)
    pagina_atual = max(1, min(pagina_atual, total_paginas))
    
    inicio = (pagina_atual - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    salmos_da_pagina = sorted_psalms[inicio:fim]

    tabela = Table(title=f"Saltério de Genebra (Página {pagina_atual} de {total_paginas})")
    tabela.add_column("Salmo", style="cyan", no_wrap=True, width=10)
    tabela.add_column("Música", style="yellow", justify="center", width=8)
    tabela.add_column("Tema(s)", style="white")

    for psalm in salmos_da_pagina:
        has_instrumental = psalm['instrumental']
        has_capela = psalm['à_capela']
        music_indicator = "A" if has_instrumental and has_capela else "I" if has_instrumental else "C" if has_capela else ""
        tema = psalm['tema'] if psalm['tema'] else ""
        ref_display = psalm['referencia'].rstrip('A')
        tabela.add_row(ref_display, music_indicator, tema)
        
    return tabela, total_paginas

def ver_salmo(numero_salmo):
    """Prepara o conteúdo e o título para serem exibidos em um Pager."""
    referencia = f"{numero_salmo}A"
    psalm = psaltery.get_psalm_by_reference(referencia)
    if not psalm:
        return f"[erro]Salmo '{numero_salmo}' não encontrado.", None
    
    meta_tabela = Table(box=None, show_header=False, show_edge=False)
    meta_tabela.add_column()
    meta_tabela.add_column()
    if psalm['tema']: meta_tabela.add_row("[info]Tema(s):[/info]", f"[italic]{psalm['tema']}[/italic]")
    meta_tabela.add_row("[info]Métrica:[/info]", psalm['metrica'])
    meta_tabela.add_row("[info]Melodia:[/info]", psalm['melodia'])

    letra = Text(psalm['letra'], justify="left")
    letra_panel = Panel(letra, title="[bold]Letra[/bold]", border_style="dim")
    
    conteudo_agrupado = Group(meta_tabela, letra_panel)
    titulo = f"Detalhes do Salmo {psalm['referencia']}"
    
    return conteudo_agrupado, titulo

def tocar_salmo(numero_salmo):
    referencia = f"{numero_salmo}A"
    psalm = psaltery.get_psalm_by_reference(referencia)
    if not psalm:
        return f"[erro]Salmo '{numero_salmo}' não encontrado."
    
    path = psalm.get('instrumental') or psalm.get('à_capela')
    if not path:
        return f"[warning]O Salmo {referencia} não possui áudio."
    
    full_path = os.path.join(DATA_DIR, path)
    if not os.path.exists(full_path):
        return f"[erro]Arquivo de áudio não encontrado em: {full_path}"

    try:
        subprocess.Popen(['mpv', full_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"[info]Iniciando a reprodução do Salmo {numero_salmo}..."
    except FileNotFoundError:
        return "[erro]'mpv' não encontrado. Instale-o para tocar áudios."
    except Exception as e:
        return f"[erro]Erro ao tocar áudio: {e}"
