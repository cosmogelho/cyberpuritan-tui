# app/cli/__init__.py (VERSÃO FINAL COM PAGER)
import os
from rich.prompt import Prompt
from rich.panel import Panel
from app.ui import telas
from app.ui import actions
from app.core.theme import console

def run_interactive_mode():
    """Inicia o loop principal da aplicação no modo TUI."""
    estado = {
        'tela_atual': 'menu_principal',
        'salterio': {'pagina_atual': 1, 'total_paginas': 1},
    }
    conteudo_principal = None
    mensagem_rodape = ""

    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            tela = estado['tela_atual']

            # 1. DESENHA A TELA
            if tela == 'menu_principal':
                banner, ajuda, conteudo_principal, prompt_txt = telas.desenhar_menu_principal()
                telas.desenhar_layout_geral(banner, ajuda, conteudo_principal, prompt_txt, mensagem_rodape)
            elif tela == 'tela_salterio':
                # Garante que a lista está sempre carregada
                conteudo_principal, total_paginas = actions.listar_salmos(estado['salterio']['pagina_atual'])
                estado['salterio']['total_paginas'] = total_paginas
                telas.desenhar_tela_salterio(conteudo_principal, mensagem_rodape)
            elif tela == 'tela_diario':
                conteudo_principal = actions.ver_diario()
                telas.desenhar_tela_diario(conteudo_principal, mensagem_rodape)
            
            mensagem_rodape = ""

            # 2. AGUARDA A ENTRADA
            raw_input = Prompt.ask("")
            if not raw_input.strip():
                continue

            partes = raw_input.split()
            comando = partes[0].lower()
            args = partes[1:]

            # 3. PROCESSA A ENTRADA
            if tela == 'menu_principal':
                if comando == 'q':
                    break
                elif comando == '1':
                    estado['tela_atual'] = 'tela_diario'
                elif comando == '6':
                    estado['tela_atual'] = 'tela_salterio'
                    estado['salterio']['pagina_atual'] = 1
                
            elif tela == 'tela_salterio':
                estado_salterio = estado['salterio']
                
                if comando == 'voltar':
                    estado['tela_atual'] = 'menu_principal'
                
                elif comando in ['proximo', 'p']:
                    if estado_salterio['pagina_atual'] < estado_salterio['total_paginas']:
                        estado_salterio['pagina_atual'] += 1
                
                elif comando in ['anterior', 'a']:
                    if estado_salterio['pagina_atual'] > 1:
                        estado_salterio['pagina_atual'] -= 1
                
                elif comando in ['listar', 'l']:
                    estado_salterio['pagina_atual'] = 1
                
                elif comando == 'ver':
                    if not args:
                        mensagem_rodape = "[erro]Uso: ver <número do salmo>[/erro]"
                    else:
                        # ===== USA O PAGER INTEGRADO DO RICH =====
                        conteudo_para_pager, titulo = actions.ver_salmo(args[0])
                        if titulo: # Se não houve erro
                            os.system('cls' if os.name == 'nt' else 'clear')
                            with console.pager(styles=True):
                                console.print(Panel(conteudo_para_pager, title=f"[bold]{titulo}[/bold]"))
                            # Quando o Pager fecha, o loop continua e vai redesenhar a lista
                        else:
                            mensagem_rodape = conteudo_para_pager # Mensagem de erro
                
                elif comando == 'tocar':
                    if not args:
                        mensagem_rodape = "[erro]Uso: tocar <número do salmo>[/erro]"
                    else:
                        mensagem_rodape = actions.tocar_salmo(args[0])
                else:
                    mensagem_rodape = f"[erro]Comando '{comando}' desconhecido.[/erro]"

            elif tela == 'tela_diario':
                if comando == 'voltar':
                    estado['tela_atual'] = 'menu_principal'
                elif comando == 'add':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    _, mensagem_rodape = actions.adicionar_entrada_diario()
                else:
                    # 'ver' e 'buscar' apenas redesenham, o que o loop já faz
                    pass

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print_exception()
            print(f"\nOcorreu um erro inesperado: {e}")
            break

    print("\n[bold]Soli Deo Gloria![/bold]")
