# app/ui/resolution_view.py
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from app.core.theme import console

def prompt_nova_resolucao() -> dict:
    """Coleta os dados de uma nova resolução."""
    console.clear()
    console.print(Panel("Adicionar Nova Resolução Pessoal", style="titulo"))
    dados = {}
    dados['text'] = Prompt.ask("[prompt]Digite o texto da sua resolução[/prompt]")
    dados['category'] = Prompt.ask("[prompt]Em qual categoria de vida ela se encaixa? (Ex: Piedade, Caráter, Uso do Tempo)[/prompt]", default="Geral")
    return dados

def exibir_lista_resolucoes(resolutions: list[tuple[str, dict]]):
    """Mostra uma tabela com todas as resoluções registradas."""
    if not resolutions:
        console.print("[info]Nenhuma resolução registrada ainda. Comece adicionando a primeira![/info]")
        return

    tabela = Table(title="Minhas Resoluções Pessoais")
    tabela.add_column("ID", style="destaque", justify="center")
    tabela.add_column("Categoria")
    tabela.add_column("Texto da Resolução")
    tabela.add_column("Revisões", justify="center")

    for res_id, dados in resolutions:
        tabela.add_row(
            res_id,
            dados.get('category', 'N/D'),
            dados.get('text', 'N/D'),
            str(dados.get('review_count', 0))
        )
    
    console.print(tabela)

# (Adicionaremos a view de revisão individual no próximo passo)
