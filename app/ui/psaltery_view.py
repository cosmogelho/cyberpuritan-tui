# app/ui/psaltery_view.py
import subprocess
import shutil
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Group
from rich.prompt import Prompt, Confirm
from app.core.theme import console

def _tocar_audio_mpv(url: str):
    """Verifica se o mpv está instalado e executa o áudio do link."""
    if not shutil.which("mpv"):
        console.print("[erro]O comando 'mpv' não foi encontrado em seu sistema.[/erro]")
        return
    
    command = ["mpv", "--no-video", url]
    try:
        console.print(f"\n[info]Iniciando áudio com mpv...[/info]")
        subprocess.run(command, check=True)
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        console.print("\n[info]Reprodução de áudio finalizada ou interrompida.[/info]")

def exibir_lista_de_salmos(resultados: list) -> int | None:
    """
    Exibe uma tabela com a lista de versões encontradas e pede ao usuário
    para escolher uma. Retorna o índice da escolha na lista.
    """
    console.clear()
    console.print(Panel(f"Versões encontradas para o Salmo {resultados[0]['referencia'].split(' ')[0]}", style="titulo"))

    tabela_resultados = Table(show_header=True, header_style="bold cyan")
    tabela_resultados.add_column("Opção", justify="center", style="destaque")
    tabela_resultados.add_column("Referência")
    tabela_resultados.add_column("Tipo/Melodia")

    opcoes_validas = []
    for i, versao in enumerate(resultados):
        opcao = str(i + 1)
        opcoes_validas.append(opcao)
        tabela_resultados.add_row(
            opcao,
            versao['referencia'],
            f"{versao.get('tipo', '')} - {versao.get('melodia', '')}"
        )
    
    console.print(tabela_resultados)

    escolha = Prompt.ask(
        "\n[prompt]Digite o número da versão para ver os detalhes (ou Enter para voltar)[/prompt]",
        choices=opcoes_validas,
        show_choices=False,
        default=""
    )

    if escolha:
        return int(escolha) - 1  # Retorna o índice (ex: escolha '1' -> índice 0)
    return None

def exibir_detalhes_do_salmo(versao: dict):
    """Exibe o painel de detalhes completo para uma única versão do salmo."""
    console.clear()
    
    info_table = Table(box=None, show_header=False, padding=(0, 1))
    info_table.add_column(style="prompt", width=15)
    info_table.add_column()
    
    if versao.get('metrica'): info_table.add_row("Métrica:", versao['metrica'])
    if versao.get('melodia'): info_table.add_row("Melodia:", versao['melodia'])

    letra_panel = Panel(Text(versao.get('letra', 'N/D')), title="Letra")
    render_group = Group(info_table, letra_panel)
    titulo = f"Salmo {versao['referencia']} ([destaque]{versao['tipo']}[/destaque])"
    painel_principal = Panel(render_group, title=titulo, border_style="painel_borda", padding=(1, 2))
    
    console.print(painel_principal)

    if video_url := versao.get('video_url'):
        if Confirm.ask("\n[prompt]Ouvir o áudio desta versão com mpv?[/prompt]", default=False):
            _tocar_audio_mpv(video_url)
