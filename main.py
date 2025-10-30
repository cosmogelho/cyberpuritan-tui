# main.py
import sys
import os

# Adiciona o diretório raiz do projeto ao path para que os imports funcionem
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# As novas interfaces de usuário que criamos
from app.ui import journal_view
from app.ui import action_item_view

# As interfaces que você já tinha e quer manter.
# Certifique-se que os nomes dos arquivos e funções estão corretos.
from app.ui import bible_view
from app.ui import symbols_view
from app.ui import psaltery_view
# from app.ui import notes_view # Descomente quando criar a view para as notas

def main_menu():
    """
    Exibe o menu principal da aplicação e direciona para os submódulos.
    """
    while True:
        print("\n====================")
        print("  Cyber-Puritano")
        print("====================")
        print("1. Diário Pessoal")
        print("2. Ações (Resoluções e Orações)")
        print("3. Estudos (Commonplace Book)")
        print("--------------------")
        print("4. Ler a Bíblia")
        print("5. Consultar Símbolos de Fé")
        print("6. Consultar o Saltério")
        print("--------------------")
        print("0. Sair")
        
        choice = input("Escolha uma opção: ")

        if choice == '1':
            journal_view.show_journal_menu()
        elif choice == '2':
            action_item_view.show_action_items_menu()
        elif choice == '3':
            # notes_view.show_notes_menu() # Chame a view de notas aqui quando estiver pronta
            print("\n[Módulo de Estudos (Notas) ainda não implementado.]")
        elif choice == '4':
            # Assumindo que sua view da bíblia tem uma função/método para iniciar
            # Ajuste 'show_bible_menu()' para o nome correto se for diferente
            bible_view.show_bible_menu() 
        elif choice == '5':
            # Ajuste 'show_symbols_menu()' para o nome correto se for diferente
            symbols_view.show_symbols_menu()
        elif choice == '6':
            # Ajuste 'show_psaltery_menu()' para o nome correto se for diferente
            psaltery_view.show_psaltery_menu()
        elif choice == '0':
            print("Saindo. Soli Deo Gloria!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main_menu()
