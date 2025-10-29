import re
from app.core.config import LIVROS_E_ABREVIACOES

# Constrói um mapa de todas as abreviações e nomes para um nome canônico
BOOK_MAP = {}
for nome, abrev in LIVROS_E_ABREVIACOES:
    BOOK_MAP[nome.lower().replace(" ", "")] = nome
    BOOK_MAP[abrev.lower().replace(" ", "")] = nome

# Expressão regular para encontrar referências bíblicas
# Ex: 1 Jo 3:16-18, Gn 1:1, Pv 10:4
BIBLE_REFERENCE_REGEX = re.compile(
    r'(\d?\s*[a-zA-Záéíóúâêôãõç]+)\.?\s*(\d+)(?::(\d+)(?:-(\d+))?)?',
    re.IGNORECASE
)

def parse_references(text: str) -> list[dict]:
    """
    Analisa um texto e extrai todas as referências bíblicas encontradas.
    Retorna uma lista de dicionários com 'book', 'chapter', 'start_verse', 'end_verse'.
    """
    if not text:
        return []
    
    found_references = []
    matches = BIBLE_REFERENCE_REGEX.finditer(text)
    
    for match in matches:
        book_input, chapter, start_v, end_v = match.groups()
        
        # Normaliza o nome do livro
        book_key = book_input.lower().replace(" ", "").replace(".", "")
        book_canonical = BOOK_MAP.get(book_key)
        
        if not book_canonical:
            continue
            
        chapter_num = int(chapter)
        start_verse = int(start_v) if start_v else 1
        end_verse = int(end_v) if end_v else start_verse
        
        # Expande o intervalo de versículos
        for verse_num in range(start_verse, end_verse + 1):
            found_references.append({
                "book": book_canonical,
                "chapter": chapter_num,
                "verse": verse_num
            })
            
    return found_references
