from textual.app import App
from textual.widgets import Header, Footer, ListView, ListItem
from textual.containers import Container
from textual.widgets import Label

class HomeScreen(Container):
    """A tela principal com o menu de seleção de módulos."""

    def compose(self):
        yield Label("[bold #fabd2f]Selecione um módulo:[/]", classes="menu-title")
        yield ListView(
            ListItem(Label("📖 Diário (Journal)"), id="journal"),
            ListItem(Label("📝 Notas (Commonplace)"), id="notes"),
            ListItem(Label("🙏 Ações (Resoluções/Orações)"), id="actions"),
            ListItem(Label("✝️ Símbolos da Fé"), id="symbols"),
            ListItem(Label("🎵 Saltério"), id="psaltery"),
            ListItem(Label("📜 Bíblia (via comando)"), id="bible_info"),
            ListItem(Label("📊 Relatórios"), id="reports"),
            id="main_menu"
        )

    def on_mount(self):
        """Foca na lista quando a tela é montada."""
        self.query_one(ListView).focus()
