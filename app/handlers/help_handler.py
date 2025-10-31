# app/handlers/help_handler.py
from rich.table import Table

def handle_help_command(args: list[str]):
    """Cria e retorna a tabela de ajuda como um widget Rich."""
    table = Table(title="Ajuda - Comandos Cyber-Puritano", style="#fabd2f")
    table.add_column("Comando", style="info", no_wrap=True)
    table.add_column("Alias", style="yellow")
    table.add_column("Descrição", style="white")
    table.add_row("journal", "j", "Diário. Subcomandos: view, find <tag>.")
    table.add_row("actions", "a", "Ações. Subcomandos: view, update. Tipos: res, ora.")
    table.add_row("notes", "n", "Notas de Estudo. Subcomandos: view, read <id>.")
    table.add_row("bible", "b", "Bíblia. Ex: 'b jo 3:16-18'.")
    table.add_row("symbols", "s", "Símbolos de Fé. Ex: 's cfw 1.1'.")
    table.add_row("psaltery", "p", "Saltério. Ex: 'p 15A', 'p list', 'p 23 play'.")
    table.add_row("reports", "rep", "Exibe um relatório de métricas da última semana.")
    table.add_row("clear", "cls", "Limpa a tela de resultados.")
    table.add_row("exit", "q", "Sai da aplicação.")
    
    # Nota sobre comandos de adição
    table.add_row("\n[bold]Adicionar Entradas[/bold]", "", "[italic]Para adicionar no diário, notas ou ações, use um editor externo e gerencie o banco de dados diretamente. Uma futura versão terá telas de formulário.[/italic]")
    
    return table
