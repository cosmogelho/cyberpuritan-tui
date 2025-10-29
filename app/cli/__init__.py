# app/cli/__init__.py
import click
from rich.prompt import Prompt
from app.core.theme import console
from app.ui.status_panel import render_status_panel
# A linha abaixo foi ajustada para um import relativo (note o ".")
from .command_parser import parse 
from app.ui.actions import COMMAND_MAP, SESSION_STATE

def run_interactive_mode():
    """Inicia o loop principal da aplicação no modo interativo."""
    console.clear()
    console.print("[bold cyan]Cyber-Puritano[/bold cyan] | Soli Deo Gloria!")
    console.print("Digite '[yellow]help[/yellow]' para ver os comandos ou '[yellow]q[/yellow]' para sair.")

    while True:
        try:
            console.print(render_status_panel())
            versao_biblia = SESSION_STATE.get('versao_biblia', 'NAA')
            raw_input = Prompt.ask(f"[cyan]({versao_biblia})[/cyan] [bold green]>[/bold green]")
            
            parsed = parse(raw_input)
            if not parsed: continue

            cmd, args = parsed["cmd"], parsed["args"]
            if cmd in ("exit", "q"): break
            
            if action := COMMAND_MAP.get(cmd):
                action(args)
            else:
                console.print(f"[erro]Comando '{cmd}' não encontrado. Digite 'help'.[/erro]")

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print(f"[bold red]Ocorreu um erro inesperado:[/bold red] {e}")
            console.print("[info]Por favor, reporte este erro se ele persistir.[/info]")

    console.print("\n[bold]Soli Deo Gloria![/bold]")

@click.command()
def cli():
    """Ferramenta devocional Cyber-Puritano."""
    run_interactive_mode()
