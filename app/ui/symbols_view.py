# app/ui/symbols_view.py
from app.models import symbols

def show_symbols_menu():
    """
    Função de entrada que o main.py chama. Gerencia a interface dos Símbolos de Fé.
    """
    while True:
        print("\n--- Módulo dos Símbolos de Fé ---")
        print("1. Confissão de Fé de Westminster (CFW)")
        print("2. Catecismo Maior de Westminster (CMW)")
        print("3. Breve Catecismo de Westminster (BCW)")
        print("0. Voltar ao Menu Principal")
        choice = input("Escolha uma opção: ")

        if choice == '1':
            try:
                chap = int(input("Digite o capítulo da CFW: "))
                sec = int(input("Digite a seção: "))
                article = symbols.get_cfw_article(chap, sec)
                if article:
                    print(f"\n--- CFW {article['chapter']}.{article['section']}: {article['title']} ---")
                    print(article['text'])
                else:
                    print("Artigo não encontrado.")
            except ValueError:
                print("Entrada inválida. Por favor, digite números.")

        elif choice == '2':
            try:
                qid = int(input("Digite o número da pergunta do CMW: "))
                q = symbols.get_cmw_question(qid)
                if q:
                    print(f"\n--- CMW Pergunta {q['id']} ---")
                    print(f"P: {q['question']}")
                    print(f"R: {q['answer']}")
                else:
                    print("Pergunta não encontrada.")
            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")

        elif choice == '3':
            try:
                qid = int(input("Digite o número da pergunta do BCW: "))
                q = symbols.get_bcw_question(qid)
                if q:
                    print(f"\n--- BCW Pergunta {q['id']} ---")
                    print(f"P: {q['question']}")
                    print(f"R: {q['answer']}")
                else:
                    print("Pergunta não encontrada.")
            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")

        elif choice == '0':
            break
        else:
            print("Opção inválida.")
