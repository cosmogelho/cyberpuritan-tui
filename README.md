# Cyber-Puritano: Ferramenta Devocional Pessoal

Esta é uma ferramenta de linha de comando (CLI) para auxiliar na disciplina e registro da vida devocional, inspirada nas práticas puritanas e reformadas.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

-   `main.py`: Ponto de entrada da aplicação.
-   `app/`: Contém todo o código fonte da aplicação.
    -   `app/cli.py`: Define os comandos da CLI usando `click`.
    -   `app/core/`: Módulos centrais (configuração, conexão com BD, temas).
    -   `app/models/`: Camada de acesso a dados. Cada arquivo é responsável por interagir com uma tabela específica do banco de dados.
    -   `app/reports/`: Lógica para gerar métricas e relatórios a partir dos dados.
    -   `app/ui/`: Lógica da interface do usuário (menus, visualizações, prompts).
-   `data/`: Contém os bancos de dados SQLite.
    -   `Biblia.sqlite`: Contém os textos bíblicos de múltiplas versões.
    -   `dados.db`: Contém todos os dados pessoais do usuário (diário, sermões, notas, etc.).
-   `tests/`: Contém os testes automatizados para garantir a qualidade do código.

## Como Usar

1.  **Executar a aplicação em modo interativo:**
    ```bash
    python main.py
    ```

2.  **Executar os testes:**
    ```bash
    pytest
    ```

## Estrutura do Banco de Dados (`dados.db`)

```sql
-- Tabela de Diário de Piedade
CREATE TABLE piety (
    date TEXT PRIMARY KEY,
    leitura_biblica INTEGER,
    oracao INTEGER,
    catecismo INTEGER,
    oracao_qualidade TEXT,
    pecado_atitude TEXT
);

-- Tabela de Resoluções Pessoais
CREATE TABLE resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    category TEXT,
    created_at TEXT,
    last_reviewed_at TEXT,
    review_count INTEGER DEFAULT 0
);

-- Tabela de Anotações de Sermões
CREATE TABLE sermons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    pregador TEXT,
    data TEXT,
    passagem_principal TEXT,
    outras_passagens TEXT,
    tema TEXT,
    anotacoes TEXT,
    aplicacoes TEXT,
    is_church INTEGER DEFAULT 0
);

-- Tabela de Anotações de Estudo
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Demais tabelas (salterio, cfw_articles, cmw, bcw, etc.)
```
