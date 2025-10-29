# app/ui/resolution_view.py
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.console import Group
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

# --- FUNÇÃO FALTANTE ADICIONADA AQUI ---
def exibir_resolucao_para_revisao(res_id: str, dados: dict, titulo: str):
    """Exibe um painel destacado com uma única resolução para meditação."""
    
    info_basica = Text()
    info_basica.append("Categoria: ", style="prompt").append(dados.get('category', 'N/D') + "\n")
    info_basica.append("Revisões: ", style="prompt").append(str(dados.get('review_count', 0)))

    texto_resolucao = Text(dados.get('text', ''), justify="center", style="bold")
    
    render_group = Group(
        info_basica,
        Panel(texto_resolucao, border_style="dim white", padding=(1, 2))
    )

    painel_geral = Panel(
        render_group,
        title=f"{titulo} - Resolução #{res_id}",
        border_style="painel_borda"
    )
    console.print(painel_geral)
