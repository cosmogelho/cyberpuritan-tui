# scripts/prepare_database.py
import sqlite3
import csv
import os

# --- Configuração ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'devocional.db')
SALTERIO_CSV_PATH = os.path.join(DATA_DIR, 'salterio_metadata.csv')

def create_tables(conn):
    """Cria as tabelas que estão faltando no banco de dados."""
    cursor = conn.cursor()
    sql_script = """
    CREATE TABLE IF NOT EXISTS piety (
        date TEXT PRIMARY KEY, leitura_biblica INTEGER, oracao INTEGER, catecismo INTEGER,
        oracao_qualidade TEXT, pecado_atitude TEXT
    );
    CREATE TABLE IF NOT EXISTS resolutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, category TEXT, created_at TEXT,
        last_reviewed_at TEXT, review_count INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS sermons (
        id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, pregador TEXT, data TEXT,
        passagem_principal TEXT, outras_passagens TEXT, tema TEXT, anotacoes TEXT,
        aplicacoes TEXT, is_church INTEGER DEFAULT 0
    );
    """
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print("✅ Tabelas 'piety', 'resolutions' e 'sermons' criadas/verificadas com sucesso.")
    except sqlite3.Error as e:
        print(f"❌ ERRO ao criar tabelas: {e}")
        conn.rollback()

def integrate_salterio_metadata(conn):
    """Lê o CSV e atualiza a tabela 'salterio' com os metadados."""
    if not os.path.exists(SALTERIO_CSV_PATH):
        print(f"⚠️ Aviso: Arquivo '{SALTERIO_CSV_PATH}' não encontrado. Pulando integração do saltério.")
        return

    cursor = conn.cursor()
    update_sql = """
    UPDATE salterio
    SET melodia = ?, compositor = ?, harmonizacao = ?, video_url = ?
    WHERE referencia = ?
    """
    
    try:
        with open(SALTERIO_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Normaliza os nomes das colunas para minúsculas e sem espaços
            headers = [h.strip().lower() for h in reader.fieldnames]
            reader.fieldnames = headers

            count = 0
            for row in reader:
                # --- AQUI ESTÁ A CORREÇÃO ---
                # Mapeamos os nomes corretos das colunas do seu CSV para os parâmetros do SQL
                params = (
                    row.get('origem/melodia'),  # CSV 'ORIGEM/MELODIA' -> DB 'melodia'
                    row.get('compositor'),      # CSV 'COMPOSITOR' -> DB 'compositor'
                    row.get('harmonização'),    # CSV 'HARMONIZAÇÃO' -> DB 'harmonizacao'
                    row.get('vídeo'),           # CSV 'VÍDEO' -> DB 'video_url'
                    row.get('salmo')            # CSV 'SALMO' -> Usado para encontrar o registro
                )
                
                if params[-1]: # Garante que a linha tem uma referência de salmo
                    cursor.execute(update_sql, params)
                    count += 1
            
            conn.commit()
            print(f"✅ Metadados de {count} salmos integrados com sucesso.")

    except sqlite3.Error as e:
        print(f"❌ ERRO ao integrar metadados do saltério: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ ERRO inesperado ao processar o CSV: {e}")

def main():
    """Função principal para executar a preparação do banco de dados."""
    print(f"Iniciando preparação do banco de dados: {DB_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        create_tables(conn)
        integrate_salterio_metadata(conn)
    except sqlite3.Error as e:
        print(f"❌ ERRO GERAL de conexão com o banco de dados: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()
