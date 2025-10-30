# Cyber-Puritano: Ferramenta Devocional Pessoal

Esta é uma ferramenta de linha de comando (CLI) para auxiliar na disciplina e registro da vida devocional, inspirada nas práticas puritanas e reformadas, com foco na simplicidade e na reflexão textual.

## Como Usar

1.  **Instalar as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Executar a aplicação em modo interativo:**
    ```bash
    python main.py
    ```

3.  **Dentro da aplicação, use os seguintes comandos:**

| Comando   | Alias | Exemplo de Uso                                 | Descrição                                         |
|-----------|-------|------------------------------------------------|-----------------------------------------------------|
| `journal` | `j`   | `j add`, `j view`, `j find sermão`             | Gerencia seu diário espiritual unificado.           |
| `actions` | `a`   | `a add res ...`, `a view ora`                  | Gerencia resoluções e pedidos de oração.          |
| `notes`   | `n`   | `n add`, `n view`, `n read 1`                  | Seu "Commonplace Book" para notas de estudo.        |
| `psaltery`| `p`   | `p 15A`, `p 23 play`, `p list`                 | Consulta o Saltério, com música e metadados.      |
| `bible`   | `b`   | `b jo 3:16-18`                                 | Lê passagens da Bíblia (versão NAA).              |
| `symbols` | `s`   | `s cfw 1.1`, `s cmw 1`                         | Consulta os Símbolos de Fé de Westminster.        |
| `reports` | `rep` | `rep`                                          | Mostra um resumo da sua atividade na última semana. |
| `help`    | `h`   | `h`                                            | Mostra esta tabela de ajuda.                      |
| `clear`   | `cls` | `cls`                                          | Limpa a tela do terminal.                         |
| `exit`    | `q`   | `q`                                            | Encerra a aplicação.                              |

## Estrutura do Banco de Dados (`dados.db`)

A aplicação usa uma estrutura de banco de dados simplificada e poderosa:

-   `journal`: Armazena todas as entradas cronológicas (diário, meditações, sermões) em formato de texto livre com tags.
-   `action_items`: Armazena itens que requerem acompanhamento, como resoluções (`Resolução`) e pedidos de oração (`Pedido de Oração`).
-   `notes`: Armazena notas de estudo temáticas e mais longas, funcionando como um "Commonplace Book".
-   Tabelas de consulta: `salterio`, `cfw_articles`, `cmw`, `bcw`.

---
**Soli Deo Gloria**
