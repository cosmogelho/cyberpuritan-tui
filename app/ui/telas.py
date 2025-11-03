import os
import pyfiglet
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

# --- Funções de Utilidade ---
def limpar_tela(): os.system("cls" if os.name == "nt" else "clear")
def criar_banner(texto, fonte="standard"): return Text(pyfiglet.figlet_format(texto, font=fonte, width=console.width), justify="center")
def criar_footer(estado, ajuda_texto):
    status_audio = "[red]• ÁUDIO TOCANDO ('stop' para parar)[/red] | " if estado.get("processo_audio") and estado["processo_audio"].poll() is None else ""
    mensagem = estado.get("mensagem_status", "")
    return Panel(f"[dim]{mensagem}[/dim]" if mensagem else f"{status_audio}{ajuda_texto}", box=box.DOUBLE)

# --- Telas de Menu ---
def desenhar_tela_principal(estado):
    header = Panel(criar_banner("Cyber Puritano"), box=box.DOUBLE)
    menu_texto = Text.from_markup("\n   [yellow]1)[/yellow] Canto\n   [yellow]2)[/yellow] Piedade\n   [yellow]3)[/yellow] Estudo\n")
    body = Panel(Group(Text("\n[bold cyan]MENU PRINCIPAL[/bold cyan]\n", justify="center"), menu_texto), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • Digite o número da opção. • 'q' para sair.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_piedade_menu(estado):
    header = Panel(criar_banner("Piedade"), box=box.DOUBLE)
    menu_texto = Text.from_markup("\n   [yellow]1)[/yellow] Diário\n   [yellow]2)[/yellow] Ações de Santificação\n   [yellow]3)[/yellow] Minhas Resoluções\n   [yellow]4)[/yellow] Autoexame Noturno\n   [yellow]5)[/yellow] Vigília Sabática\n")
    body = Panel(Group(Text("\n[bold cyan]PIEDADE[/bold cyan]\n", justify="center"), menu_texto), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • Digite o número da opção. • 'v' para voltar.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_estudo_menu(estado):
    header = Panel(criar_banner("Estudo"), box=box.DOUBLE)
    menu_texto = Text.from_markup("\n   [yellow]1)[/yellow] As Escrituras\n   [yellow]2)[/yellow] Doutrina\n   [yellow]3)[/yellow] Arquivo de Sermões\n   [yellow]4)[/yellow] Notas de Estudo\n")
    body = Panel(Group(Text("\n[bold cyan]ESTUDO[/bold cyan]\n", justify="center"), menu_texto), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • Digite o número da opção. • 'v' para voltar.")
    limpar_tela(); console.print(header, body, footer)

# --- Telas Finais (com modificações) ---
def desenhar_tela_biblia(estado):
    dados = estado.get("dados_tela")
    header = Panel(criar_banner("Escrituras"), box=box.DOUBLE)
    
    ajuda = "AJUDA: • 'ler <livro> <cap>' • 'nota add <ref> <texto>' • 'nota del <id>' • 'v' voltar"
    
    # Painel principal do texto bíblico
    if dados and dados.get("capitulo_info"):
        cap_info = dados["capitulo_info"]
        titulo_txt = f"[bold cyan]{cap_info['livro']} {cap_info['capitulo']}[/bold cyan]"
        versiculos_render = [Text.from_markup(f"[yellow]{v['verse']}[/yellow] {v['text']}") for v in cap_info['versiculos']]
        body_content = Group(Text.from_markup(titulo_txt), *versiculos_render)
    else:
        body_content = Text("\nUse 'ler <livro> <capítulo>' para buscar.\nEx: ler genesis 1\n", justify="center")
    
    body = Panel(body_content, box=box.DOUBLE)

    # Painel de Notas (renderizado separadamente)
    notas_panel = None
    if dados and dados.get("notas"):
        notas_render = [Text.from_markup(f"[yellow]{n['id']}.[/yellow] [bold]{n['referencia_biblica']}:[/bold] {n['texto']}") for n in dados['notas']]
        notas_panel = Panel(Group(Text.from_markup("[bold cyan]NOTAS DE ESTUDO[/bold cyan]"), *notas_render), box=box.MINIMAL)
        
    limpar_tela()
    console.print(header)
    console.print(body)
    if notas_panel:
        console.print(notas_panel)
    console.print(criar_footer(estado, ajuda))

# (O resto das telas permanece o mesmo)
def desenhar_tela_sermao_novo_passo(campo):
    titulos = {"titulo": "Título*", "tema": "Tema(s)", "pregador": "Pregador", "local": "Local", "data": "Data (AAAA-MM-DD)*", "link": "Link", "passagem_principal": "Passagem Principal*"}
    header = Panel(criar_banner("Sermoes"), box=box.DOUBLE)
    body = Panel(Text(f"\n{titulos.get(campo, campo)}\n"), box=box.DOUBLE)
    footer = Panel("Pressione [ENTER] para continuar. Campos com * são obrigatórios.", box=box.DOUBLE)
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_sermoes_lista(estado):
    dados = estado.get("dados_tela", {}); sermoes = dados.get("sermoes", [])
    header = Panel(criar_banner("Sermoes"), box=box.DOUBLE)
    if sermoes:
        tabela = Table(box=box.MINIMAL, expand=True)
        tabela.add_column("ID", style="yellow"); tabela.add_column("Título"); tabela.add_column("Pregador"); tabela.add_column("Passagem")
        for s in sermoes: tabela.add_row(str(s['id']), s['titulo'], s['pregador'], s['passagem_principal'])
        pag_txt = f"(Página {dados['pagina_atual']} de {dados['total_paginas']})"
        titulo = Text.from_markup(f"[bold cyan]SERMÕES ARQUIVADOS[/bold cyan] [dim]{pag_txt}[/dim]\n")
        body_content = Group(titulo, tabela)
    else: body_content = Text("\nNenhum sermão arquivado. Use 'n' para adicionar o primeiro.\n", justify="center")
    body = Panel(body_content, box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'ver <id>' • 'n' novo • 'n'/'p' pág. • 'v' voltar")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_sermao_detalhes(estado):
    sermao = estado.get("dados_tela")
    header = Panel(criar_banner("Sermoes"), box=box.DOUBLE)
    titulo = Text.from_markup(f"[bold cyan]SERMÃO: {sermao['titulo']}[/bold cyan]")
    info = Text.from_markup(f"\n[bold]Tema:[/bold] {sermao['tema'] or 'N/A'}\n[bold]Pregador:[/bold] {sermao['pregador'] or 'N/A'}\n[bold]Data/Local:[/bold] {sermao['data']} em {sermao['local'] or 'N/A'}\n[bold]Link:[/bold] {sermao['link'] or 'N/A'}\n\n[bold]Passagem Principal:[/bold] [yellow]{sermao['passagem_principal']}[/yellow]")
    body = Panel(Group(titulo, info), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'v' para voltar à lista.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_autoexame_pergunta(num_pergunta, total, texto_pergunta):
    header = Panel(criar_banner("Autoexame"), box=box.DOUBLE)
    paginacao = f"[dim](Pergunta {num_pergunta} de {total})[/dim]"
    titulo = Text.from_markup(f"[bold cyan]AUTOEXAME NOTURNO[/bold cyan] {paginacao}\n")
    pergunta = Text(texto_pergunta)
    body = Panel(Group(titulo, pergunta), box=box.DOUBLE)
    footer = Panel("Responda e pressione [ENTER]. Deixe em branco para 'em silêncio'.", box=box.DOUBLE)
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_vigilia_sabatica_passo(num_passo, total, texto_passo):
    header = Panel(criar_banner("Vigilia"), box=box.DOUBLE)
    paginacao = f"[dim](Passo {num_passo} de {total})[/dim]"
    titulo = Text.from_markup(f"[bold cyan]VIGÍLIA SABÁTICA[/bold cyan] {paginacao}\n")
    passo = Text(texto_passo)
    body = Panel(Group(titulo, passo), box=box.DOUBLE)
    footer = Panel("Reflita e pressione [ENTER]. Anote se desejar.", box=box.DOUBLE)
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_salterio(estado):
    dados = estado["dados_tela"]
    header = Panel(criar_banner("Canto"), box=box.DOUBLE)
    tabela = Table(box=box.MINIMAL, expand=True); tabela.add_column("Ref.", style="yellow"); tabela.add_column("Melodia"); tabela.add_column("Tema(s)", style="cyan")
    for salmo in dados["salmos"]: tabela.add_row(salmo['referencia'], salmo['melodia'], str(salmo['tema']))
    titulo = Text.from_markup(f"[bold cyan]SALTÉRIO[/bold cyan] [dim](Página {dados['pagina_atual']} de {dados['total_paginas']})[/dim]\n")
    body = Panel(Group(titulo, tabela), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 't <Ref>' tocar • 'c <Ref>' cantar • 'n'/'p' pág. • 'v' voltar.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_diario(estado):
    dados = estado.get("dados_tela")
    header = Panel(criar_banner("Diario"), box=box.DOUBLE)
    if dados and dados["entradas"]:
        pag_txt = f"(Página {dados['pagina_atual']} de {dados['total_paginas']})"
        titulo = Text.from_markup(f"[bold cyan]ENTRADAS DO DIÁRIO[/bold cyan] [dim]{pag_txt}[/dim]")
        entradas_render = [Panel(Text.from_markup(e['texto']), title=f"[yellow]{e['data'][:16]}[/yellow]", border_style="dim") for e in dados["entradas"]]
        body_content = Group(titulo, *entradas_render)
    else: body_content = Text("\nNenhuma entrada. Use 'n' para criar a primeira.\n", justify="center")
    body = Panel(body_content, box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'n' nova entrada • 'n'/'p' pág. • 'v' voltar.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_diario_nova_entrada():
    header = Panel(criar_banner("Diario"), box=box.DOUBLE)
    body = Panel(Text.from_markup("\n[bold]Nova Entrada[/bold]\nDigite o conteúdo abaixo.\n"), box=box.DOUBLE)
    footer = Panel("AJUDA: • Pressione [CTRL]+[D] para terminar.", box=box.DOUBLE)
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_acoes(estado):
    dados = estado.get("dados_tela", {}); acoes = dados.get("acoes", [])
    header = Panel(criar_banner("Acoes"), box=box.DOUBLE)
    if acoes:
        linhas = [f"{'[green][✓][/green]' if a['status'] == 'completo' else '[ ]'} [yellow]{a['id']}.[/yellow] [{ 'dim' if a['status'] == 'completo' else 'white' }]{a['descricao']}[/]" for a in acoes]
        body_content = Text.from_markup("\n".join(linhas))
    else: body_content = Text("\nNenhuma ação definida. Use 'n <descrição>' para criar uma.\n", justify="center")
    body = Panel(Group(Text.from_markup("[bold cyan]AÇÕES DE SANTIFICAÇÃO[/bold cyan]\n"), body_content), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'n <desc>' • 'c <id>' • 'p <id>' • 'd <id>' • 'v' voltar")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_resolucoes(estado):
    dados = estado.get("dados_tela", {}); resolucoes = dados.get("resolucoes", [])
    header = Panel(criar_banner("Resolucoes"), box=box.DOUBLE)
    if resolucoes:
        body_content = Text.from_markup("\n".join([f"[yellow]{res['id']}.[/yellow] {res['texto']}" for res in resolucoes]))
    else: body_content = Text("\nNenhuma resolução. Use 'n <texto>' para criar a primeira.\n", justify="center")
    body = Panel(Group(Text.from_markup("[bold cyan]MINHAS RESOLUÇÕES[/bold cyan]\n"), body_content), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'n <texto>' nova • 'd <id>' deletar • 'v' voltar")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_doutrina_menu(estado):
    header = Panel(criar_banner("Doutrina"), box=box.DOUBLE)
    menu_texto = Text.from_markup("\n   [yellow]1)[/yellow] Confissão de Fé\n   [yellow]2)[/yellow] Catecismo Maior\n   [yellow]3)[/yellow] Breve Catecismo\n")
    body = Panel(Group(Text("\n[bold cyan]DOUTRINA[/bold cyan]\n", justify="center"), menu_texto), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • Digite o número da opção. • 'v' para voltar.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_cfw_lista(estado):
    dados = estado["dados_tela"]; header = Panel(criar_banner("Doutrina"), box=box.DOUBLE)
    tabela = Table(box=box.MINIMAL, expand=True); tabela.add_column("Cap.", justify="right", style="yellow"); tabela.add_column("Título", style="white")
    for cap in dados["capitulos"]: tabela.add_row(str(cap['chapter']), cap['title'])
    titulo = Text.from_markup("[bold cyan]CONFISSÃO DE FÉ DE WESTMINSTER[/bold cyan]\n")
    body = Panel(Group(titulo, tabela), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'ler <cap>' para ler. • 'v' para voltar.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_cfw_capitulo(estado):
    dados = estado["dados_tela"]; header = Panel(criar_banner("Doutrina"), box=box.DOUBLE)
    titulo = Text.from_markup(f"[bold cyan]Capítulo {dados['numero']}: {dados['titulo']}[/bold cyan]\n")
    secoes = [Text.from_markup(f"\n[yellow]{s['section']}.[/yellow] {s['text']}") for s in dados["secoes"]]
    body = Panel(Group(titulo, *secoes), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'provas <cap>.<sec>' • 'v' para voltar.")
    limpar_tela(); console.print(header, body, footer)
def desenhar_tela_cfw_provas(estado):
    dados = estado["dados_tela"]; header = Panel(criar_banner("Doutrina"), box=box.DOUBLE)
    titulo = Text.from_markup(f"[bold cyan]PROVAS BÍBLICAS: CFW {dados['location']}[/bold cyan]\n")
    provas = [Text.from_markup(f"[yellow]{i+1}. {p['name']} {p['chapter']}:{p['verse']}[/yellow]\n{p['text']}\n") for i, p in enumerate(dados["provas"])]
    body = Panel(Group(titulo, *provas), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'v' para voltar ao capítulo.")
    limpar_tela(); console.print(header, body, footer)
def _desenhar_tela_catecismo_lista(estado, nome_catecismo):
    dados = estado["dados_tela"]; header = Panel(criar_banner("Doutrina"), box=box.DOUBLE)
    tabela = Table(box=box.MINIMAL, expand=True); tabela.add_column("Perg.", justify="right", style="yellow"); tabela.add_column("Pergunta", style="white")
    for p in dados["perguntas"]: tabela.add_row(str(p['id']), p['question'])
    paginacao = f"(Página {dados['pagina_atual']} de {dados['total_paginas']})"
    titulo = Text.from_markup(f"[bold cyan]{nome_catecismo.upper()}[/bold cyan] [dim]{paginacao}[/dim]\n")
    body = Panel(Group(titulo, tabela), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'ler <nº>' • 'n'/'p' pág. • 'v' para voltar.")
    limpar_tela(); console.print(header, body, footer)
def _desenhar_tela_catecismo_pergunta(estado, nome_catecismo):
    dados = estado["dados_tela"]; header = Panel(criar_banner("Doutrina"), box=box.DOUBLE)
    titulo = Text.from_markup(f"[bold cyan]{nome_catecismo.upper()} - Pergunta {dados['id']}[/bold cyan]\n")
    pergunta = Text.from_markup(f"[bold]P: {dados['pergunta']}[/bold]")
    resposta = Text.from_markup(f"\n[bold]R:[/bold] {dados['resposta']}")
    body = Panel(Group(titulo, pergunta, resposta), box=box.DOUBLE)
    footer = criar_footer(estado, "AJUDA: • 'v' para voltar à lista.")
    limpar_tela(); console.print(header, body, footer)

# --- Roteador Principal ---
def desenhar_tela(estado):
    telas = {
        "principal": desenhar_tela_principal, "salterio": desenhar_tela_salterio,
        "piedade_menu": desenhar_tela_piedade_menu, "diario": desenhar_tela_diario,
        "acoes": desenhar_tela_acoes, "resolucoes": desenhar_tela_resolucoes,
        "estudo_menu": desenhar_tela_estudo_menu, "biblia": desenhar_tela_biblia,
        "doutrina_menu": desenhar_tela_doutrina_menu, "sermoes_lista": desenhar_tela_sermoes_lista,
        "sermao_detalhes": desenhar_tela_sermao_detalhes,
        "cfw_lista": desenhar_tela_cfw_lista, "cfw_capitulo": desenhar_tela_cfw_capitulo,
        "cfw_provas": desenhar_tela_cfw_provas,
        "cmw_lista": lambda e: _desenhar_tela_catecismo_lista(e, "Catecismo Maior"),
        "cmw_pergunta": lambda e: _desenhar_tela_catecismo_pergunta(e, "Catecismo Maior"),
        "bcw_lista": lambda e: _desenhar_tela_catecismo_lista(e, "Breve Catecismo"),
        "bcw_pergunta": lambda e: _desenhar_tela_catecismo_pergunta(e, "Breve Catecismo"),
    }
    tela_func = telas.get(estado.get("tela_atual"))
    if tela_func: tela_func(estado)
    else:
        limpar_tela()
        console.print(f"Debug: Tela '[bold cyan]{estado.get('tela_atual')}[/bold cyan]' não implementada.")
        footer = criar_footer(estado, "Pressione 'v' para voltar.")
        console.print(footer)
