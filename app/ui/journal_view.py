# app/ui/journal_view.py
from datetime import datetime
from app.models import journal_model

def _display_entries(entries):
    if not entries:
        print("Nenhuma entrada encontrada.")
        return
    for entry in entries:
        print("-" * 40)
        print(f"ID: {entry['id']} | Data: {entry['entry_date']} | Tags: [{entry['tags']}]")
        print(f"\n{entry['content']}")
        print("-" * 40)

def show_journal_menu():
    while True:
        print("\n--- Menu do Diário ---")
        print("1. Nova Entrada no Diário")
        print("2. Ver Todas as Entradas")
        print("3. Buscar por Tag (ex: sermão, jejum)")
        print("0. Voltar ao Menu Principal")
        choice = input("Escolha uma opção: ")

        if choice == '1':
            content = input("Escreva sua entrada:\n")
            tags = input("Tags (separadas por vírgula, ex: autoexame, sermão): ")
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            journal_model.add_entry(current_date, content, tags)
            print("Entrada salva com sucesso!")
        elif choice == '2':
            all_entries = journal_model.get_all_entries()
            _display_entries(all_entries)
        elif choice == '3':
            tag_to_search = input("Digite a tag que deseja buscar: ")
            tagged_entries = journal_model.get_entries_by_tag(tag_to_search)
            _display_entries(tagged_entries)
        elif choice == '0':
            break
        else:
            print("Opção inválida.")
