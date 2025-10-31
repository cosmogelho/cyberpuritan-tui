from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable
from textual.binding import Binding
from app.models import journal_model
from rich.text import Text

# Importaremos esta tela de popup em breve
from .add_journal_screen import AddJournalScreen

class JournalScreen(Screen):
    """Tela para visualizar e navegar pelas entradas do diário."""

    BINDINGS = [
        Binding("q", "app.pop_screen", "Voltar"),
        Binding("j", "cursor_down", "Mover para baixo", show=False),
        Binding("k", "cursor_up", "Mover para cima", show=False),
        Binding("a", "add_entry", "Adicionar Entrada"),
        Binding("enter", "select_entry", "Ver Detalhes"),
    ]

    def compose(self):
        yield Header()
        yield DataTable(id="journal_table")
        yield Footer()

    def on_mount(self):
        """Carrega os dados na tabela quando a tela é montada."""
        self.update_table()

    def update_table(self):
        """Busca as entradas do diário e preenche a tabela."""
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("Data", "Tags", "Conteúdo (início)")
        
        entries = journal_model.get_all_entries()
        for entry in entries:
            # Pega apenas a primeira linha do conteúdo para a prévia
            preview = entry['content'].split('\n', 1)[0]
            
            # Adiciona a linha com metadados para podermos buscar o ID depois
            table.add_row(
                Text(entry['entry_date'], style="#fabd2f"),
                Text(entry['tags'], style="#8ec07c"),
                Text(preview, style="dim"),
                key=str(entry['id'])
            )

    def action_add_entry(self):
        """Abre a tela de adição de nova entrada."""
        def check_if_saved(saved: bool):
            if saved:
                self.update_table()

        self.app.push_screen(AddJournalScreen(), check_if_saved)

    def action_select_entry(self):
        """Exibe o conteúdo completo da entrada selecionada."""
        table = self.query_one(DataTable)
        entry_id = table.get_row_key(table.cursor_row)
        # Por enquanto, vamos apenas mostrar um popup simples
        # Idealmente, isso abriria uma nova tela de detalhes
        entry = next((e for e in journal_model.get_all_entries() if str(e['id']) == entry_id), None)
        if entry:
            self.app.notify("Detalhes da Entrada", entry['content'], timeout=10)
