from app.cli import inicializar_estado, processar_input
from app.ui.telas import desenhar_tela
from app.core.db import inicializar_banco

def main():
    """Ponto de entrada e loop principal da aplicação."""
    inicializar_banco() # Garante que a tabela 'diario' exista
    estado = inicializar_estado()

    while estado.get("rodando", True):
        desenhar_tela(estado)
        comando = input("> ")
        estado = processar_input(estado, comando)

    print("Saindo. A paz de Cristo seja contigo.")

if __name__ == "__main__":
    main()
