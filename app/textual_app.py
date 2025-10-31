# app/textual_app.py
# VERSÃO FINAL, ROBUSTA E FUNCIONAL

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, Input
from rich.panel import Panel
from rich.align import Align
from rich.console import Group
from rich.text import Text

from app.ui.icons import *
# Importa todos os handlers para reconectar a funcionalidade
from app.handlers import help_handler, bible_handler, psaltery_handler, symbols_handler

# Mapeia os comandos que já temos para seus handlers
COMMAND_MAP = {
    "help": help_handler.handle_help_command,
    "bible": bible_handler.handle_bible_command,
    "psaltery": psaltery_handler.handle_psaltery_command,
    "symbols": symbols_handler.handle_symbols_command,
    # Adicionaremos os outros aqui conforme recriamos suas telas
}

class WelcomeWidget(Static):
    """O widget da tela de boas-vindas. Agora sem o bug de expansão."""
    def compose(self) -> ComposeResult:
        title = Text("Cyber-Puritano", justify="center", style="#fabd2f")
        quote = Text.assemble(
            ("\nA tua palavra é lâmpada que ilumina os meus passos...", "italic"),
            ("\nSalmo 119:105", "bold #a89984")
        )
        help_text = Text.assemble(("\n\nDigite '", "#ebdbb2"), ("help", "bold #8ec07c"), ("' para iniciar.", "#ebdbb2"))

        # O painel agora está contido dentro de um Align, sem expandir
        welcome_panel = Panel(
            Align.center(Group(title, Align.center(quote), Align.center(help_text)), vertical="middle"),
            title=f"[bold] {SCROLL} Bem-vindo [/]",
            border_style="#665c54",
            height=20 # Altura fixa para evitar que ele "cresça" demais
        )
        yield Static(welcome_panel)

class PuritanApp(App):
    """Sua Mesa de Estudos Digital."""
    CSS_PATH = "ui/styles.tcss"
    BINDINGS = [("escape", "quit", "Sair")]

    def compose(self) -> ComposeResult:
        """Cria o layout principal da aplicação."""
        yield Header()
        yield Container(
            Static("Sidebar Estática", id="sidebar"),
            Container(WelcomeWidget(), id="content_area")
        , id="main_container")
        yield Input(placeholder=f"{PROMPT} Digite um comando...", id="command_input")
        yield Footer()

    def on_mount(self) -> None:
        """Configura os elementos estáticos da UI."""
        self.query_one(Header).text = f" {CROSS} Cyber-Puritano"
        self.query_one(Footer).text = "Post Tenebras Lux"
        self.query_one(Input).focus()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Lida com os comandos enviados pelo usuário."""
        command_text = message.value.strip()
        message.input.clear()

        if not command_text:
            return

        # Lógica de parse do comando (reaproveitada)
        from app.cli.command_parser import parse
        parsed = parse(command_text)
        if not parsed:
            result_widget = Static(Panel(f"[red]Comando inválido: {command_text}[/red]", border_style="red"))
        else:
            cmd, args = parsed["cmd"], parsed["args"]
            
            # Limpa a tela ou sai
            if cmd in ["exit", "q"]:
                self.exit()
            elif cmd in ["clear", "cls"]:
                 # Limpa o conteúdo
                content_area = self.query_one("#content_area")
                content_area.query("*").remove()
                return

            # Executa o comando do mapa
            if handler := COMMAND_MAP.get(cmd):
                # O resultado de um handler (um Panel, Table, etc. do Rich)
                rich_renderable = handler(args)
                # "Embrulhamos" em um Static para o Textual poder exibir
                result_widget = Static(rich_renderable)
            else:
                result_widget = Static(Panel(f"[yellow]Comando '{cmd}' não implementado.[/yellow]", border_style="yellow"))

        # Atualiza a área de conteúdo
        content_area = self.query_one("#content_area")
        content_area.query("*").remove() # Limpa o conteúdo anterior
        content_area.mount(result_widget) # Monta o novo resultado
