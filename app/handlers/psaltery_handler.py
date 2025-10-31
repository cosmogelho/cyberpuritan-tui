# app/handlers/psaltery_handler.py
import os
import re
import subprocess
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.markup import escape
from app.models import psaltery
from app.core.config import DATA_DIR

def handle_psaltery_command(args: list[str]):
    if not args or args[0].lower() == 'list':
        all_psalms = psaltery.get_all_psalms_references()
        table = Table(title="Saltério - Lista de Salmos")
        table.add_column("Referência", style="cyan")
        table.add_column("Música (I/C/A)", style="yellow", justify="center")

        def sort_key(p):
            match = re.match(r'(\d+)([A-Z]*)', p['referencia'])
            return (int(match.groups()[0]), match.groups()[1]) if match else (999, p['referencia'])

        for psalm in sorted(all_psalms, key=sort_key):
            music = ""
            # --- CORREÇÃO AQUI: Usando .keys() para verificação segura ---
            has_i = 'instrumental' in psalm.keys() and psalm['instrumental']
            has_c = 'à_capela' in psalm.keys() and psalm['à_capela']
            if has_i and has_c: music = "A"
            elif has_i: music = "I"
            elif has_c: music = "C"
            table.add_row(psalm['referencia'], music)
        return table

    referencia = args[0].upper()
    sub_cmd = args[1].lower() if len(args) > 1 else 'view'
    psalm = psaltery.get_psalm_by_reference(referencia)

    if not psalm:
        return Panel(f"[red]Salmo '{referencia}' não encontrado.[/red]", border_style="red")

    if sub_cmd == 'play':
        version = args[2].lower() if len(args) > 2 else None
        
        audio_path = None
        # --- CORREÇÃO AQUI: Usando .keys() para verificação segura ---
        if version in ['i', 'instrumental'] and 'instrumental' in psalm.keys() and psalm['instrumental']:
            audio_path = psalm['instrumental']
        elif version in ['c', 'capela', 'à_capela'] and 'à_capela' in psalm.keys() and psalm['à_capela']:
            audio_path = psalm['à_capela']
        elif not version:
            # Pega a primeira versão disponível
            if 'instrumental' in psalm.keys() and psalm['instrumental']:
                audio_path = psalm['instrumental']
            elif 'à_capela' in psalm.keys() and psalm['à_capela']:
                 audio_path = psalm['à_capela']

        if audio_path:
            path = os.path.join(DATA_DIR, audio_path)
            if os.path.exists(path):
                try:
                    subprocess.run(['mpv', path])
                    return Panel(f"[green]Reprodução finalizada.[/green]", border_style="green")
                except FileNotFoundError:
                    return Panel("[red]Comando 'mpv' não encontrado.[/red] Instale-o para usar esta função.", border_style="red")
            return Panel(f"[red]Arquivo de áudio não encontrado:[/red] {path}", border_style="red")
        
        return Panel(f"[yellow]Versão de áudio solicitada não disponível para o Salmo {referencia}.[/yellow]", border_style="yellow")
    
    meta = Table(box=None, show_header=False)
    meta.add_column(style="yellow"); meta.add_column()
    # --- CORREÇÃO AQUI: Usando .keys() para verificação segura ---
    if 'tema' in psalm.keys() and psalm['tema']:
        meta.add_row("Tema(s):", f"[italic]{psalm['tema']}[/italic]")
    meta.add_row("Tipo:", psalm['tipo']); meta.add_row("Métrica:", psalm['metrica'])
    meta.add_row("Melodia:", psalm['melodia']); meta.add_row("Compositor:", psalm['compositor'])

    letra = escape(psalm['letra'])
    
    return Panel(Group(meta, "\n", letra), title=f"Salmo {referencia}", border_style="#fabd2f")
