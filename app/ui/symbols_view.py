# app/ui/symbols_view.py
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm
from app.core.theme import console

def exibir_simbolos(resultados: list | dict, tipo: str):
    """Formata e exibe os itens dos Símbolos de Fé."""
    if isinstance(resultados, dict) and "erro" in resultados:
        console.print(f"[erro]{resultados['erro']}[/erro]")
        return

    for item in resultados:
        if tipo == 'cfw':
            titulo = f"CFW {item['chapter']}.{item['section']} - {item['title']}"
            console.print(Panel(Markdown(item['text']), title=titulo, border_style="painel_borda"))
        else:
            titulo = f"{tipo.upper()} - Pergunta {item['id']}"
            pergunta_panel = Panel(f"[prompt]P:[/prompt] {item['question']}", title=titulo, border_style="painel_borda")
            console.print(pergunta_panel)
            
            if Confirm.ask("Ver resposta?", default=True):
                resposta_panel = Panel(f"[prompt]R:[/prompt] {item['answer']}", border_style="dim white")
                console.print(resposta_panel)
