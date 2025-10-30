# app/ui/bible_view.py
import re
from app.models import bible

def _parse_reference(ref_string: str):
    """
    Analisa uma string de referência bíblica (ex: 'João 3:16-18') e retorna as partes.
    Retorna None se o formato for inválido.
    """
    # Regex para capturar Livro, Capítulo, Versículo inicial e Versículo final (opcional)
    pattern = re.compile(r'^\s*([1-3]?\s*\w+)\s*(\d+):(\d+)(?:-(\d+))?\s*$')
    match = pattern.match(ref_string)
    
    if not match:
        return None
        
    groups = match.groups()
    book = groups[0].strip()
    chapter = int(groups[1])
    start_verse = int(groups[2])
    end_verse = int(groups[3]) if groups[3] else None
    
    return book, chapter, start_verse, end_verse

def show_bible_menu():
    """
    Função de entrada que o main.py chama. Gerencia a interface da Bíblia.
    """
    print("\n--- Módulo da Bíblia ---")
    print("Digite a referência bíblica (ex: 'Gênesis 1:1', 'Jo 3:16-18') ou 'sair'.")

    while True:
        ref_input = input("\nBuscar referência: ")
        if ref_input.lower() in ['sair', '0', 'exit', 'voltar']:
            break
            
        parsed_ref = _parse_reference(ref_input)
        
        if not parsed_ref:
            print("Formato de referência inválido. Use 'Livro Capítulo:Versículo'.")
            continue
            
        book, chapter, start_verse, end_verse = parsed_ref
        
        verses = bible.get_verses(book, chapter, start_verse, end_verse)
        
        if not verses:
            print("Referência não encontrada. Verifique o nome do livro e os números.")
        else:
            # Imprime o cabeçalho com o nome completo do livro e capítulo
            full_book_name = verses[0]['book_name']
            print(f"\n--- {full_book_name} {chapter} ---")
            for verse in verses:
                print(f"[{verse['verse']}] {verse['text']}")
