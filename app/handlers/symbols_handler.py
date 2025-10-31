# app/handlers/symbols_handler.py
from rich.panel import Panel
from rich.markup import escape
from rich.text import Text
from app.models import symbols

def handle_symbols_command(args: list[str]):
    if not args:
        return Panel("[bold red]Uso:[/bold red] symbols [cfw|cmw|bcw] [referência]", border_style="red")
    
    doc = args[0].lower()
    ref = " ".join(args[1:])
    
    if doc == 'cfw':
        try:
            chap, sec = map(int, ref.split('.'))
            article = symbols.get_cfw_article(chap, sec)
            if article:
                return Panel(escape(article['text']), title=f"CFW {chap}.{sec}: {article['title']}")
            return Panel("[yellow]Artigo não encontrado.[/yellow]", border_style="yellow")
        except ValueError:
            return Panel("[bold red]Formato inválido.[/bold red] Use 'cfw capitulo.secao'", border_style="red")
            
    elif doc in ['cmw', 'bcw']:
        try:
            qid = int(ref)
            q_func = symbols.get_cmw_question if doc == 'cmw' else symbols.get_bcw_question
            q = q_func(qid)
            if q:
                content = Text.assemble(("P: ", "bold yellow"), f"{escape(q['question'])}\n\n", ("R: ", "bold green"), escape(q['answer']))
                return Panel(content, title=f"{doc.upper()} Pergunta {qid}")
            return Panel("[yellow]Pergunta não encontrada.[/yellow]", border_style="yellow")
        except ValueError:
            return Panel("[bold red]Referência inválida.[/bold red] Deve ser um número.", border_style="red")
            
    return Panel("[bold red]Documento inválido.[/bold red] Use 'cfw', 'cmw', ou 'bcw'.", border_style="red")
