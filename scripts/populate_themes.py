import sqlite3
import json
import re
import os

# Define os caminhos com base na localização do script
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'dados.db')
JSON_PATH = os.path.join(PROJECT_ROOT, 'salmos.json')

def parse_salmos_string(salmos_str: str) -> list[int]:
    """
    Converte uma string como "24; 47; 48" ou "[93–99]" em uma lista de números de salmo.
    """
    numeros = []
    # Remove colchetes e espaços extras
    clean_str = salmos_str.strip().strip('[]')
    
    partes = [p.strip() for p in clean_str.split(';')]
    
    for parte in partes:
        # Verifica se é um intervalo (ex: 93–99)
        if '–' in parte or '-' in parte:
            # Lida com ambos os tipos de traço
            range_parts = re.split(r'[–-]', parte)
            if len(range_parts) == 2:
                try:
                    start, end = int(range_parts[0]), int(range_parts[1])
                    numeros.extend(range(start, end + 1))
                except ValueError:
                    print(f"  [Aviso] Intervalo malformado ignorado: '{parte}'")
        else:
            # É um número único
            try:
                # Remove caracteres não numéricos que possam ter sobrado
                num_only = re.sub(r'\D', '', parte)
                if num_only:
                    numeros.append(int(num_only))
            except ValueError:
                print(f"  [Aviso] Valor não numérico ignorado: '{parte}'")
                
    return numeros

def build_theme_map() -> dict[int, list[str]]:
    """
    Lê o arquivo JSON e cria um mapa de {numero_salmo: [lista_de_temas]}.
    """
    theme_map = {}
    print(f"Lendo temas de '{JSON_PATH}'...")
    
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{JSON_PATH}' não encontrado. Certifique-se de que ele está na raiz do projeto.")
        return {}
    except json.JSONDecodeError:
        print(f"[ERRO] O arquivo '{JSON_PATH}' não é um JSON válido.")
        return {}

    for item in data:
        tema = item.get("TEMA")
        salmos_str = item.get("SALMOS")
        
        if not tema or not salmos_str:
            continue
            
        numeros_salmo = parse_salmos_string(salmos_str)
        for num in numeros_salmo:
            if num not in theme_map:
                theme_map[num] = []
            theme_map[num].append(tema)
            
    print(f"Mapa de temas construído com sucesso para {len(theme_map)} salmos distintos.")
    return theme_map

def update_database(theme_map: dict[int, list[str]]):
    """
    Conecta ao banco de dados, adiciona a coluna 'tema' se não existir,
    e atualiza cada salmo com seus temas correspondentes.
    """
    print(f"\nConectando ao banco de dados em '{DB_PATH}'...")
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado em '{DB_PATH}'.")
        return
        
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Adicionar a coluna 'tema' se ela não existir
        cursor.execute("PRAGMA table_info(salterio)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'tema' not in columns:
            print("Coluna 'tema' não encontrada. Adicionando à tabela 'salterio'...")
            cursor.execute("ALTER TABLE salterio ADD COLUMN tema TEXT")
            print("Coluna 'tema' adicionada com sucesso.")
        else:
            print("Coluna 'tema' já existe na tabela 'salterio'.")

        # 2. Obter todas as referências de salmos do banco
        cursor.execute("SELECT id, referencia FROM salterio")
        salmos_db = cursor.fetchall()
        print(f"\nEncontrados {len(salmos_db)} registros na tabela 'salterio'. Atualizando temas...")

        updated_count = 0
        for salmo_id, referencia in salmos_db:
            # Extrai o número do salmo da referência (ex: '119A' -> 119)
            match = re.match(r'(\d+)', referencia)
            if not match:
                continue
            
            numero_salmo = int(match.group(1))
            
            # Busca os temas no mapa
            temas = theme_map.get(numero_salmo)
            
            if temas:
                # Junta a lista de temas em uma única string separada por vírgula
                tema_str = ", ".join(temas)
                cursor.execute("UPDATE salterio SET tema = ? WHERE id = ?", (tema_str, salmo_id))
                updated_count += 1
        
        conn.commit()
        print(f"\nAtualização concluída. {updated_count} registros de salmos foram atualizados com temas.")

    except sqlite3.Error as e:
        print(f"[ERRO] Ocorreu um erro no banco de dados: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == '__main__':
    theme_map = build_theme_map()
    if theme_map:
        update_database(theme_map)
