# app/ui/action_item_view.py
from datetime import datetime
from app.models import action_item_model

def _display_items(items, item_type):
    if not items:
        print(f"Nenhum(a) {item_type} encontrado(a).")
        return
    print(f"\n--- Lista de {item_type}s ---")
    for item in items:
        print(f"ID: {item['id']} | Status: {item['status']} | Criado em: {item['created_at']}")
        print(f"  Texto: {item['text']}")
    print("-" * 20)

def show_action_items_menu():
    while True:
        print("\n--- Menu de Ações (Resoluções e Orações) ---")
        print("1. Ver Resoluções")
        print("2. Ver Pedidos de Oração")
        print("3. Adicionar Nova Resolução")
        print("4. Adicionar Novo Pedido de Oração")
        print("5. Atualizar Status de um Item")
        print("0. Voltar ao Menu Principal")
        choice = input("Escolha uma opção: ")

        if choice in ('1', '2'):
            item_type = 'Resolução' if choice == '1' else 'Pedido de Oração'
            items = action_item_model.get_items(item_type)
            _display_items(items, item_type)
        elif choice in ('3', '4'):
            item_type = 'Resolução' if choice == '3' else 'Pedido de Oração'
            text = input(f"Digite o texto da nova {item_type}:\n")
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            action_item_model.add_item(item_type, text, current_date)
            print(f"{item_type} adicionado(a) com sucesso!")
        elif choice == '5':
            try:
                item_id = int(input("Digite o ID do item para atualizar: "))
                new_status = input("Digite o novo status (ex: Revisado, Respondido): ")
                current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                action_item_model.update_item_status(item_id, new_status, current_date)
                print("Status atualizado com sucesso!")
            except ValueError:
                print("ID inválido. Por favor, insira um número.")
        elif choice == '0':
            break
        else:
            print("Opção inválida.")
