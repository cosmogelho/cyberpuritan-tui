# app/ui/bible_view.py
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Group
from app.core.theme import console
from app.core.config import LIVROS_E_ABREVIACOES

def exibir_passagem(resultado: dict):
    """Formata e exibe uma passagem bíblica e suas referências cruzadas."""
    if "erro" in resultado:
        console.print(f"[erro]{resultado['erro']}[/erro]")
        return

    # Painel do Texto Bíblico
    texto_formatado = Text()
    for v in resultado['versiculos']:
        texto_formatado.append(f"[{v['numero']}] ", style="referencia")
        texto_formatado.append(f"{v['texto']} ")
    titulo = f"Bíblia {resultado['versao']} | {resultado['referencia']}"
    painel_texto = Panel(texto_formatado, title=titulo, border_style="painel_borda")

    console.print(painel_texto)

    # Painel das Referências Cruzadas
    if resultado.get("cross_references"):
        tabela_refs = Table(title="Sua Concordância Pessoal", box=None, padding=(0, 1))
        tabela_refs.add_column("ID", style="destaque")
        tabela_refs.add_column("Título do Registro")
        tabela_refs.add_column("Autor/Pregador")
        
        for ref in resultado["cross_references"]:
            tabela_refs.add_row(
                str(ref['record_id']),
                ref['titulo'],
                ref['author']
            )
        console.print(Panel(tabela_refs, border_style="dim white"))


def mostrar_tabela_livros():
    # ... (esta função permanece a mesma)
    tabela = Table(title="Livros da Bíblia e Abreviações", box=None, padding=(0, 1))
    tabela.add_column("Nome", style="cyan"); tabela.add_column("Abrev.", style="yellow")
    tabela.add_column("Nome", style="cyan"); tabela.add_column("Abrev.", style="yellow")
    metade = (len(LIVROS_E_ABREVIACOES) + 1) // 2
    for i in range(metade):
        p1 = LIVROS_E_ABREVIACOES[i]
        p2 = LIVROS_E_ABREVIACOES[i + metade] if i + metade < len(LIVROS_E_ABREVIACOES) else ("", "")
        tabela.add_row(p1[0], p1[1], p2[0], p2[1])
    console.print(tabela)
