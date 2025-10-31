from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical
from textual.widgets import TextArea
from textual.binding import Binding
from datetime import datetime
from app.models import journal_model

class AddJournalScreen(ModalScreen[bool]):
    """Uma tela modal para adicionar uma nova entrada no diário."""

    BINDINGS = [Binding("ctrl+s", "save", "Salvar")]

    def compose(self):
        with Vertical(classes="modal_container"):
            yield Label("Nova Entrada no Diário", id="modal_title")
            yield Label("Conteúdo (Ctrl+S para Salvar, Esc para Cancelar):")
            yield TextArea(language="markdown", id="journal_content", theme="gruvbox-dark")
            yield Input(placeholder="Tags (separadas por vírgula)", id="journal_tags")
            yield Button("Salvar", variant="primary", id="save_button")
            yield Button("Cancelar", id="cancel_button")

    def on_mount(self):
        self.query_one(TextArea).focus()

    def action_save(self):
        """Salva a nova entrada."""
        content = self.query_one("#journal_content").text
        tags = self.query_one("#journal_tags").value
        if content.strip():
            journal_model.add_entry(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), content, tags)
            self.dismiss(True) # Retorna True, indicando que foi salvo
        else:
            self.app.notify("Erro: Conteúdo não pode ser vazio.", severity="error")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save_button":
            self.action_save()
        else:
            self.dismiss(False) # Retorna False, indicando que foi cancelado
