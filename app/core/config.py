import os

# --- Gestão de Caminhos ---
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# --- Arquivos de Dados ---
# Apontando para os novos bancos de dados centralizados
DB_BIBLIA_PATH = os.path.join(DATA_DIR, 'Biblia.sqlite')
DB_DADOS_PATH = os.path.join(DATA_DIR, 'dados.db')

# --- Configurações da Aplicação ---
VERSAO_BIBLIA_PADRAO = "NAA"
VERSOES_BIBLIA_DISPONIVEIS = ["NAA", "ARA", "NVI"] # Manter para o seletor da UI

# --- Constantes da Bíblia ---
LIVROS_E_ABREVIACOES = [
    ("Gênesis", "Gn"), ("Êxodo", "Ex"), ("Levítico", "Lv"), ("Números", "Nm"),
    ("Deuteronômio", "Dt"), ("Josué", "Js"), ("Juízes", "Jz"), ("Rute", "Rt"),
    ("1 Samuel", "1Sm"), ("2 Samuel", "2Sm"), ("1 Reis", "1Rs"), ("2 Reis", "2Rs"),
    ("1 Crônicas", "1Cr"), ("2 Crônicas", "2Cr"), ("Esdras", "Ed"), ("Neemias", "Ne"),
    ("Ester", "Et"), ("Jó", "Jó"), ("Salmos", "Sl"), ("Provérbios", "Pv"),
    ("Eclesiastes", "Ec"), ("Cantares", "Ct"), ("Isaías", "Is"), ("Jeremias", "Jr"),
    ("Lamentações", "Lm"), ("Ezequiel", "Ez"), ("Daniel", "Dn"), ("Oséias", "Os"),
    ("Joel", "Jl"), ("Amós", "Am"), ("Obadias", "Ob"), ("Jonas", "Jn"),
    ("Miquéias", "Mq"), ("Naum", "Na"), ("Habacuque", "Hc"), ("Sofonias", "Sf"),
    ("Ageu", "Ag"), ("Zacarias", "Zc"), ("Malaquias", "Ml"), ("Mateus", "Mt"),
    ("Marcos", "Mc"), ("Lucas", "Lc"), ("João", "Jo"), ("Atos", "At"),
    ("Romanos", "Rm"), ("1 Coríntios", "1Co"), ("2 Coríntios", "2Co"), ("Gálatas", "Gl"),
    ("Efésios", "Ef"), ("Filipenses", "Fp"), ("Colossenses", "Cl"),
    ("1 Tessalonicenses", "1Ts"), ("2 Tessalonicenses", "2Ts"), ("1 Timóteo", "1Tm"),
    ("2 Timóteo", "2Tm"), ("Tito", "Tt"), ("Filemom", "Fm"), ("Hebreus", "Hb"),
    ("Tiago", "Tg"), ("1 Pedro", "1Pe"), ("2 Pedro", "2Pe"), ("1 João", "1Jo"),
    ("2 João", "2Jo"), ("3 João", "3Jo"), ("Judas", "Jd"), ("Apocalipse", "Ap")
]
MAPA_ABREVIACOES = {abrev.lower(): nome for nome, abrev in LIVROS_E_ABREVIACOES}
