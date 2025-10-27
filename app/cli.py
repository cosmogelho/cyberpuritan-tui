import click
from app.core.config import VERSAO_BIBLIA_PADRAO
from app.models import bible
from app.ui import bible_view
from app.ui.main_menu import iniciar_menu_interativo

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Ferramenta devocional Cyber-Puritano. Inicia em modo interativo se nenhum comando for usado."""
    if ctx.invoked_subcommand is None:
        iniciar_menu_interativo()

@cli.command()
@click.argument("livro")
@click.argument("capitulo", type=int)
@click.argument("versiculo", type=int, required=False)
@click.option("--versao", "-v", default=VERSAO_BIBLIA_PADRAO, help="Versão da Bíblia.")
def biblia(livro: str, capitulo: int, versiculo: int | None, versao: str):
    """Exibe um texto da Bíblia diretamente no terminal."""
    # 1. Chama o modelo para buscar os dados
    resultado = bible.obter_passagem(versao, livro, capitulo, versiculo)
    # 2. Passa os dados para a view exibir
    bible_view.exibir_passagem(resultado)

# Outros comandos podem ser adicionados aqui seguindo o mesmo padrão.
