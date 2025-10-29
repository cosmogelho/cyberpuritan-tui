# app/ui/record_view.py
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.console import Group
from app.core.theme import console

def prompt_novo_registro() -> dict:
    """Coleta os dados de um novo registro de forma categórica."""
    console.clear()
    console.print(Panel("Adicionar Novo Registro", style="titulo"))
    
    dados = {}
    cat_choices = {"1": "Sermão", "2": "Estudo Bíblico/EBD", "3": "Reunião de Oração", "4": "Estudo Doutrinário"}
    cat_choice = Prompt.ask("[prompt]Qual o tipo de registro?[/prompt]", choices=cat_choices.keys(), show_choices=False)
    dados['category'] = cat_choices[cat_choice]
    
    dados['titulo'] = Prompt.ask(f"[prompt]Título ({dados['category']})[/prompt]")
    
    author_prompt = "Pregador" if dados['category'] == 'Sermão' else 'Professor/Autor'
    dados['author'] = Prompt.ask(f"[prompt]{author_prompt}[/prompt]")
    
    dados['context'] = Prompt.ask("[prompt]Contexto (Igreja, Conferência, Livro)[/prompt]", default="Igreja Local")
    dados['data'] = Prompt.ask("[prompt]Data (AAAA-MM-DD)[/prompt]", default=datetime.now().strftime('%Y-%m-%d'))
    dados['passagem_principal'] = Prompt.ask("[prompt]Passagem(ns) Principal(is)[/prompt]")
    
    console.print("\n[prompt]Digite suas anotações. Pressione Esc -> Enter para finalizar.[/prompt]")
    dados['anotacoes'] = Prompt.get_input(console, multiline=True)
    
    console.print("\n[prompt]Digite as aplicações pessoais. Pressione Esc -> Enter para finalizar.[/prompt]")
    dados['aplicacoes'] = Prompt.get_input(console, multiline=True)
    
    return dados

def exibir_lista_registros(registros: list[dict]) -> str | None:
    """Mostra uma tabela com registros e pergunta qual deles detalhar."""
    if not registros:
        console.print("[info]Nenhum registro encontrado.[/info]")
        return None

    tabela = Table(title="Registros da Igreja")
    tabela.add_column("ID", style="destaque", justify="center")
    tabela.add_column("Categoria")
    tabela.add_column("Data")
    tabela.add_column("Título")
    tabela.add_column("Autor")

    opcoes_validas = [str(r['id']) for r in registros]
    for r in registros:
        tabela.add_row(str(r['id']), r.get('category', 'N/D'), r.get('data', 'N/D'), r.get('titulo', 'N/D'), r.get('author', 'N/D'))
    
    console.print(tabela)
    
    return Prompt.ask(
        "\n[prompt]Digite o ID para ver detalhes (ou Enter para voltar)[/prompt]",
        choices=opcoes_validas, show_choices=False, default=""
    )

def exibir_detalhes_registro(record_id: str, dados: dict):
    """Exibe um painel com todos os detalhes de um registro específico."""
    console.clear()

    info_basica = Text()
    info_basica.append(f"Autor/Pregador: ", style="prompt").append(dados.get('author', 'N/D') + "\n")
    info_basica.append(f"Contexto: ", style="prompt").append(dados.get('context', 'N/D') + "\n")
    info_basica.append(f"Data: ", style="prompt").append(dados.get('data', 'N/D') + "\n")
    info_basica.append(f"Passagem Principal: ", style="prompt").append(dados.get('passagem_principal', 'N/D') + "\n")

    p_anotacoes = Panel(Text(dados.get('anotacoes', ''), justify="left"), title="Anotações")
    p_aplicacoes = Panel(Text(dados.get('aplicacoes', ''), justify="left"), title="Aplicações Pessoais")

    render_group = Group(info_basica, p_anotacoes, p_aplicacoes)
    painel_geral = Panel(
        render_group,
        title=f"{dados.get('category')} #{record_id} - {dados.get('titulo', 'Sem Título')}",
        border_style="painel_borda"
    )
    console.print(painel_geral)
