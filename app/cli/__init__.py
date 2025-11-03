import sys
from datetime import datetime
from app.ui.actions import *
from app.ui.telas import (
    desenhar_tela_diario_nova_entrada, desenhar_tela_autoexame_pergunta,
    desenhar_tela_vigilia_sabatica_passo, desenhar_tela_sermao_novo_passo
)

ESTADO_INICIAL = {"rodando": True, "tela_atual": "principal", "processo_audio": None, "dados_tela": None, "mensagem_status": ""}
def inicializar_estado(): return ESTADO_INICIAL.copy()
def parar_audio(estado):
    if estado.get("processo_audio"):
        estado["processo_audio"].terminate(); estado["processo_audio"].wait()
        estado.update({"processo_audio": None, "mensagem_status": "Áudio parado."})
def _coletar_e_salvar_entrada_diario():
    desenhar_tela_diario_nova_entrada(); print("> ", end="")
    texto = "".join(sys.stdin.readlines()).strip()
    return salvar_entrada_diario(texto) if texto else "Entrada cancelada."
def _executar_autoexame():
    respostas = {}
    for i, pergunta in enumerate(PERGUNTAS_EXAME):
        desenhar_tela_autoexame_pergunta(i + 1, len(PERGUNTAS_EXAME), pergunta)
        respostas[i] = input("> ").strip() or "(em silêncio)"
    salvar_entrada_diario(formatar_resultado_exame(respostas))
    return "Autoexame salvo no diário."
def _executar_vigilia_sabatica():
    respostas = {}
    for i, passo in enumerate(PASSOS_VIGILIA):
        desenhar_tela_vigilia_sabatica_passo(i + 1, len(PASSOS_VIGILIA), passo)
        respostas[i] = input("> ").strip() or "(em oração/meditação)"
    salvar_entrada_diario(formatar_resultado_vigilia(respostas))
    return "Vigília Sabática salva no diário."
def _coletar_e_salvar_sermao():
    campos = ["titulo", "tema", "pregador", "local", "data", "link", "passagem_principal"]
    dados_sermao = {}
    for campo in campos:
        desenhar_tela_sermao_novo_passo(campo)
        valor = input("> ").strip()
        if not valor and campo in ["titulo", "passagem_principal", "data"]: return "Título, Passagem e Data são obrigatórios. Cancelado."
        if campo == "data":
            try: datetime.strptime(valor, '%Y-%m-%d')
            except ValueError: return "Formato de data inválido (AAAA-MM-DD). Cancelado."
        dados_sermao[campo] = valor if valor else None
    return adicionar_sermao(dados_sermao)

def processar_input(estado, comando):
    estado["mensagem_status"] = ""
    acao, *args = comando.lower().split() if comando else ("",)
    tela = estado.get("tela_atual")

    if acao == 'q': parar_audio(estado); estado['rodando'] = False; return estado
    if acao == 'stop': parar_audio(estado); return estado
    if acao == 'v':
        voltar_mapa = {
            "piedade_menu": "principal", "diario": "piedade_menu", "acoes": "piedade_menu", "resolucoes": "piedade_menu",
            "estudo_menu": "principal", "biblia": "estudo_menu", "doutrina_menu": "estudo_menu", "sermoes_lista": "estudo_menu",
            "sermao_detalhes": "sermoes_lista", "cfw_lista": "doutrina_menu", "cmw_lista": "doutrina_menu", "bcw_lista": "doutrina_menu",
            "cfw_capitulo": "cfw_lista", "cmw_pergunta": "cmw_lista", "bcw_pergunta": "bcw_lista", "cfw_provas": "cfw_capitulo",
        }
        tela_anterior = voltar_mapa.get(tela, "principal")
        dados = None
        if tela_anterior in ["sermoes_lista", "cfw_lista", "cmw_lista", "bcw_lista"]:
            if tela_anterior == "sermoes_lista": dados = listar_sermoes()
            elif tela_anterior == "cfw_lista": dados = listar_capitulos_cfw()
            elif tela_anterior == "cmw_lista": dados = listar_perguntas_cmw()
            elif tela_anterior == "bcw_lista": dados = listar_perguntas_bcw()
        elif tela_anterior == "cfw_capitulo": dados = estado.get('dados_tela_anterior')
        estado.update({"tela_atual": tela_anterior, "dados_tela": dados})
        return estado

    # --- Navegação e Ações por Tela ---
    if tela == "principal":
        if acao == '1': estado.update({'tela_atual': 'salterio', 'dados_tela': listar_salmos()})
        elif acao == '2': estado.update({'tela_atual': 'piedade_menu'})
        elif acao == '3': estado.update({'tela_atual': 'estudo_menu'})
    elif tela == "piedade_menu":
        if acao == '1': estado.update({'tela_atual': 'diario', 'dados_tela': listar_entradas_diario()})
        elif acao == '2': estado.update({'tela_atual': 'acoes', 'dados_tela': listar_acoes()})
        elif acao == '3': estado.update({'tela_atual': 'resolucoes', 'dados_tela': listar_resolucoes()})
        elif acao == '4': estado.update({'tela_atual': 'piedade_menu', 'mensagem_status': _executar_autoexame()})
        elif acao == '5': estado.update({'tela_atual': 'piedade_menu', 'mensagem_status': _executar_vigilia_sabatica()})
    elif tela == "estudo_menu":
        if acao == '1': estado.update({"tela_atual": "biblia"})
        elif acao == '2': estado.update({"tela_atual": "doutrina_menu"})
        elif acao == '3': estado.update({"tela_atual": "sermoes_lista", "dados_tela": listar_sermoes()})
    
    elif tela == "biblia":
        # Recarrega os dados da Bíblia e das notas após uma ação
        def recarregar_biblia_e_notas(estado):
            capitulo_atual = estado.get("dados_tela", {}).get("capitulo_info", {})
            if capitulo_atual:
                dados, _ = ler_capitulo_biblia(capitulo_atual['livro'], capitulo_atual['capitulo'])
                if dados:
                    dados['notas'] = listar_notas_por_referencia(f"{dados['livro']} {dados['capitulo']}")
                estado["dados_tela"] = dados

        if acao == 'ler' and len(args) >= 2 and args[1].isdigit():
            livro, cap = args[0], int(args[1])
            dados, erro = ler_capitulo_biblia(livro, cap)
            if erro: estado["mensagem_status"] = erro
            else:
                dados['notas'] = listar_notas_por_referencia(f"{dados['livro']} {dados['capitulo']}")
                estado["dados_tela"] = dados
        elif acao == 'nota' and args and args[0] == 'add' and len(args) >= 3:
            referencia = args[1]
            texto_nota = " ".join(args[2:])
            estado["mensagem_status"] = criar_nota_estudo(referencia, texto_nota)
            recarregar_biblia_e_notas(estado)
        elif acao == 'nota' and args and args[0] == 'del' and len(args) >= 2 and args[1].isdigit():
            estado["mensagem_status"] = deletar_nota_estudo(int(args[1]))
            recarregar_biblia_e_notas(estado)
        elif acao in ['ler', 'nota']:
            estado["mensagem_status"] = "Comandos: 'ler <livro> <cap>', 'nota add <ref> <texto>', 'nota del <id>'"

    # (Outras telas permanecem as mesmas)
    elif tela == "sermoes_lista":
        dados = estado['dados_tela']
        if acao == 'n' and not args:
            mensagem = _coletar_e_salvar_sermao()
            estado.update({'mensagem_status': mensagem, 'dados_tela': listar_sermoes()})
        elif acao == 'ver' and args and args[0].isdigit():
            sermao = ver_sermao(int(args[0]))
            if sermao: estado.update({"tela_atual": "sermao_detalhes", "dados_tela": sermao})
            else: estado["mensagem_status"] = f"Sermão ID {args[0]} não encontrado."
        elif acao == 'n' and dados['pagina_atual'] < dados['total_paginas']: dados.update(listar_sermoes(pagina=dados['pagina_atual'] + 1))
        elif acao == 'p' and dados['pagina_atual'] > 1: dados.update(listar_sermoes(pagina=dados['pagina_atual'] - 1))
    elif tela == "doutrina_menu":
        if acao == '1': estado.update({'tela_atual': 'cfw_lista', 'dados_tela': listar_capitulos_cfw()})
        elif acao == '2': estado.update({'tela_atual': 'cmw_lista', 'dados_tela': listar_perguntas_cmw()})
        elif acao == '3': estado.update({'tela_atual': 'bcw_lista', 'dados_tela': listar_perguntas_bcw()})
    elif tela == "acoes":
        try:
            if acao == 'n' and args: estado["mensagem_status"] = criar_acao(" ".join(args))
            elif acao in ['c', 'p', 'd'] and args:
                if acao == 'd': estado["mensagem_status"] = deletar_acao(int(args[0]))
                else: estado["mensagem_status"] = atualizar_status_acao(int(args[0]), 'completo' if acao == 'c' else 'pendente')
            if acao in ['n', 'c', 'p', 'd']: estado['dados_tela'] = listar_acoes()
        except (ValueError, IndexError): estado["mensagem_status"] = "Comando inválido."
    elif tela == "resolucoes":
        try:
            if acao == 'n' and args: estado["mensagem_status"] = criar_resolucao(" ".join(args))
            elif acao == 'd' and args: estado["mensagem_status"] = deletar_resolucao(int(args[0]))
            if acao in ['n', 'd']: estado['dados_tela'] = listar_resolucoes()
        except (ValueError, IndexError): estado["mensagem_status"] = "Comando inválido."
    elif tela.startswith("salterio"):
        dados = estado['dados_tela']
        if acao == 'n' and dados['pagina_atual'] < dados['total_paginas']: dados.update(listar_salmos(pagina=dados['pagina_atual'] + 1))
        elif acao == 'p' and dados['pagina_atual'] > 1: dados.update(listar_salmos(pagina=dados['pagina_atual'] - 1))
        elif acao in ['t', 'c'] and args:
            parar_audio(estado); tipo = 'instrumental' if acao == 't' else 'a_capela'
            processo, msg = tocar_audio_salmo(args[0], tipo)
            estado.update({"processo_audio": processo, "mensagem_status": msg})
    elif tela.startswith("diario"):
        dados = estado.get('dados_tela', {})
        if acao == 'n' and not args:
            mensagem = _coletar_e_salvar_entrada_diario()
            estado.update({'mensagem_status': mensagem, 'dados_tela': listar_entradas_diario()})
        elif acao == 'n' and dados and dados.get('pagina_atual', 1) < dados.get('total_paginas', 1): dados.update(listar_entradas_diario(pagina=dados['pagina_atual'] + 1))
        elif acao == 'p' and dados and dados.get('pagina_atual', 1) > 1: dados.update(listar_entradas_diario(pagina=dados['pagina_atual'] - 1))
    elif tela == "cfw_lista":
        if acao == 'ler' and args and args[0].isdigit():
            dados_cap = ler_capitulo_cfw(int(args[0]))
            if dados_cap: estado.update({"tela_atual": "cfw_capitulo", "dados_tela": dados_cap})
            else: estado['mensagem_status'] = f"Capítulo {args[0]} não encontrado."
    elif tela == "cfw_capitulo":
        if acao == 'provas' and args:
            try:
                cap, sec = args[0].split('.'); dados_provas = buscar_provas_cfw(cap, sec)
                if dados_provas:
                    estado['dados_tela_anterior'] = estado['dados_tela']
                    estado.update({"tela_atual": "cfw_provas", "dados_tela": dados_provas})
                else: estado['mensagem_status'] = f"Nenhuma prova para {cap}.{sec}"
            except (ValueError, IndexError): estado['mensagem_status'] = "Formato inválido."
    elif tela in ["cmw_lista", "bcw_lista"]:
        is_cmw = tela == "cmw_lista"; listar_func = listar_perguntas_cmw if is_cmw else listar_perguntas_bcw; ler_func = ler_pergunta_cmw if is_cmw else ler_pergunta_bcw; proxima_tela = "cmw_pergunta" if is_cmw else "bcw_pergunta"
        dados = estado['dados_tela']
        if acao == 'n' and dados['pagina_atual'] < dados['total_paginas']: dados.update(listar_func(pagina=dados['pagina_atual'] + 1))
        elif acao == 'p' and dados['pagina_atual'] > 1: dados.update(listar_func(pagina=dados['pagina_atual'] - 1))
        elif acao == 'ler' and args and args[0].isdigit():
            pergunta = ler_func(int(args[0]))
            if pergunta: estado.update({"tela_atual": proxima_tela, "dados_tela": pergunta})
            else: estado['mensagem_status'] = f"Pergunta {args[0]} não encontrada."
            
    return estado
