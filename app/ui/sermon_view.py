# app/ui/sermon_view.py
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.console import Group
from app.core.theme import console

def exibir_lista_sermoes(sermoes: list[tuple[str, dict]]) -> str | None:
    """Mostra uma tabela com sermões e pergunta qual deles detalhar."""
    if not sermoes:
        console.print("[info]Nenhum sermão registrado ainda.[/info]")
        return None

    tabela = Table(title="Sermões Registrados")
    tabela.add_column("ID", style="destaque", justify="center")
    tabela.add_column("Data")
    tabela.add_column("Título")
    tabela.add_column("Pregador")
    tabela.add_column("Passagem Principal")

    opcoes_validas = []
    for sermon_id, dados in sermoes:
        opcoes_validas.append(sermon_id)
        tabela.add_row(
            sermon_id,
            dados.get('data', 'N/D'),
            dados.get('titulo', 'N/D'),
            dados.get('pregador', 'N/D'),
            dados.get('passagem_principal', 'N/D')
        )
    
    console.print(tabela)
    
    escolha = Prompt.ask(
        "\n[prompt]Digite o ID do sermão para ver detalhes (ou Enter para voltar)[/prompt]",
        choices=opcoes_validas,
        show_choices=False,
        default=""
    )
    return escolha if escolha else None

def exibir_detalhes_sermon(sermon_id: str, dados: dict):
    """Exibe um painel com todos os detalhes de um sermão específico."""
    console.clear()

    info_basica = Text()
    info_basica.append(f"Pregador: ", style="prompt").append(dados.get('pregador', 'N/D') + "\n")
    info_basica.append(f"Data: ", style="prompt").append(dados.get('data', 'N/D') + "\n")
    info_basica.append(f"Passagem Principal: ", style="prompt").append(dados.get('passagem_principal', 'N/D') + "\n")
    if outras := dados.get('outras_passagens'):
        info_basica.append(f"Outras Passagens: ", style="prompt").append(outras + "\n")
    if tema := dados.get('tema'):
        info_basica.append(f"Tema: ", style="prompt").append(tema)

    p_anotacoes = Panel(Text(dados.get('anotacoes', ''), justify="left"), title="Anotações")
    p_aplicacoes = Panel(Text(dados.get('aplicacoes', ''), justify="left"), title="Aplicações Pessoais")

    render_group = Group(info_basica, p_anotacoes, p_aplicacoes)
    painel_geral = Panel(
        render_group,
        title=f"Sermão #{sermon_id} - {dados.get('titulo', 'Sem Título')}",
        border_style="painel_borda"
    )
    console.print(painel_geral)

def prompt_novo_sermon() -> dict:
    """Coleta os dados de um novo sermão através de prompts."""
    console.clear()
    console.print(Panel("Registrar Novo Sermão", style="titulo"))
    
    dados = {}
    dados['titulo'] = Prompt.ask("[prompt]Título do sermão[/prompt]")
    dados['pregador'] = Prompt.ask("[prompt]Nome do pregador[/prompt]")
    dados['data'] = Prompt.ask("[prompt]Data (AAAA-MM-DD)[/prompt]", default=datetime.now().strftime('%Y-%m-%d'))
    dados['passagem_principal'] = Prompt.ask("[prompt]Passagem principal[/prompt]")
    dados['outras_passagens'] = Prompt.ask("[prompt]Outras passagens (opcional)[/prompt]", default="")
    dados['tema'] = Prompt.ask("[prompt]Tema central (opcional)[/prompt]", default="")
    
    console.print("\n[prompt]Digite suas anotações. Pressione Esc -> Enter para finalizar.[/prompt]")
    dados['anotacoes'] = Prompt.get_input(console, multiline=True)
    
    console.print("\n[prompt]Digite as aplicações pessoais. Pressione Esc -> Enter para finalizar.[/prompt]")
    dados['aplicacoes'] = Prompt.get_input(console, multiline=True)
    
    return dados
