# app/ui/study_view.py
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.markdown import Markdown
from rich.console import Group
from app.core.theme import console

def exibir_lista_notas(notas: list[dict] | None) -> str | None:
    """Mostra uma tabela com as anotações e pede para selecionar uma."""
    if not notas:
        console.print("[info]Nenhuma anotação encontrada. Que tal criar a primeira?[/info]")
        return None

    tabela = Table(title="Estudos & Anotações")
    tabela.add_column("ID", style="destaque", justify="center")
    tabela.add_column("Título")
    tabela.add_column("Tags")
    tabela.add_column("Criado em")

    opcoes_validas = [str(nota['id']) for nota in notas]
    for nota in notas:
        data_criacao = nota['created_at'].split('T')[0]
        tabela.add_row(str(nota['id']), nota.get('title', 'N/D'), nota.get('tags', ''), data_criacao)
    
    console.print(tabela)
    
    return Prompt.ask(
        "\n[prompt]Digite o ID da anotação para ver os detalhes (ou Enter para voltar)[/prompt]",
        choices=opcoes_validas, show_choices=False, default=""
    )

def exibir_detalhes_nota(nota: dict):
    """Exibe um painel com todos os detalhes de uma anotação."""
    console.clear()

    info_basica = Text()
    info_basica.append(f"Tags: ", style="prompt").append(nota.get('tags', 'N/D') + "\n")
    info_basica.append(f"Criado em: ", style="prompt").append(nota.get('created_at', 'N/D'))

    # Usar Markdown permite formatação rica no conteúdo da nota
    conteudo_md = Markdown(nota.get('content', ''))
    p_conteudo = Panel(conteudo_md, title="Conteúdo", border_style="painel_borda")

    render_group = Group(info_basica, p_conteudo)
    painel_geral = Panel(
        render_group, title=f"Anotação #{nota['id']} - {nota.get('title', 'Sem Título')}",
        border_style="painel_borda"
    )
    console.print(painel_geral)

def prompt_nova_nota() -> dict:
    """Coleta os dados de uma nova anotação."""
    console.clear()
    console.print(Panel("Nova Anotação de Estudo", style="titulo"))
    
    dados = {}
    dados['title'] = Prompt.ask("[prompt]Título da anotação[/prompt]")
    dados['tags'] = Prompt.ask("[prompt]Tags (separadas por vírgula, opcional)[/prompt]", default="")
    
    console.print("\n[prompt]Digite o conteúdo da anotação. Pressione Esc -> Enter para finalizar.[/prompt]")
    dados['content'] = Prompt.get_input(console, multiline=True)
    
    return dados
