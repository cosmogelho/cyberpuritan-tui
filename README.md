# 🕊️ cyberpuritan-tui

Uma aplicação de terminal (TUI) para registro e consulta de disciplinas espirituais, com foco em ferramentas da tradição puritana reformada.

---

## 📖 Sobre o Projeto

O Cyberpuritan TUI é uma ferramenta para registrar, organizar e revisar práticas devocionais e de estudo a partir da linha de comando. A interface é dividida em três módulos, acessíveis pelas teclas `1`, `2` e `3`.

---

## 🔹 1. Módulo de Canto (Saltério)

- **Funcionalidade:** Navegação, leitura e reprodução de áudio dos 150 Salmos do Saltério de Genebra.
- **Recursos de Áudio:**
  - `t`: Reproduz a faixa instrumental.
  - `c`: Reproduz a faixa vocal (a capela).
- **Fonte:** Dados e áudios baseados na compilação da Comissão Brasileira de Salmodia.

---

## 🔹 2. Módulo de Piedade (Diário)

Este módulo funciona como um sistema de registro para atividades devocionais.

- **Dashboard:** A tela principal apresenta:
  - **Calendar Heatmap:** Grade visual que exibe a frequência de atividades registradas nos últimos 4 meses, com a cor de cada dia indicando o volume de entradas.
  - **Painel de Status:** Exibe o dia da semana, a contagem regressiva para domingo, o estado de jejum (se ativo), e um checklist de rotinas do dia.

- **Tipos de Entrada:** O sistema permite criar entradas de diário para as seguintes disciplinas:
  - **Autoexame:** Um assistente guiado para selecionar perguntas de um catálogo, registrar avaliações (`Boa`, `Precisa melhorar`, `Problema grave`) e definir um passo prático.
  - **Notas de Sermão:** Formulário para registrar pregador, passagens, pontos principais e aplicação.
  - **Resoluções:** Registro de resoluções pessoais, incluindo objetivo e métrica.
  - **Jejum:** Registro de tipo, propósito e observações.
  - **Leitura Bíblica:** Anotação de tema, passagens lidas e aplicação.
  - **Evangelismo:** Registro de contatos e resultados.

- **Ferramentas Adicionais:**
  - **Consulta de Orações:** Um leitor para as Orações Puritanas pré-carregadas.
  - **Gerenciador de Perguntas:** Interface para adicionar, editar ou desativar perguntas no catálogo de autoexame.

---

## 🔹 3. Módulo de Estudo (Recursos Teológicos)

- **Símbolos de Fé:** Leitor para a *Confissão de Fé de Westminster*, *Catecismo Maior* e *Breve Catecismo*.
- **Bíblia:** Leitor de texto bíblico (tradução ARA), com navegação por livro e capítulo.

---

## 🧰 Dependências

- **Rust:** Dependências definidas no `Cargo.toml`. `serde` é usado para serialização.
- **Externas:** `mpv` é necessário para a funcionalidade de reprodução de áudio.

---

## 🗂️ Estrutura de Dados

- **`canon.db` (Banco de Dados Estático):** Contém Escritura, salmos, catecismos, orações e perguntas padrão.
- **`piety.db` (Banco de Dados do Usuário):** Armazena todas as entradas de diário criadas pelo usuário e as personalizações do catálogo de perguntas. É gerado na primeira execução.
- **Áudios:** Arquivos `.opus` localizados em `data/saltério/`.

---

Para iniciar a aplicação principal:

```
cargo run
```

O aplicativo criará automaticamente o banco pessoal (data/piety.db) caso ainda não exista.


---

## Navegação e Atalhos

### Atalhos Globais
| Tecla(s)      | Ação                              |
|---------------|-----------------------------------|
| `q`           | Sair                              |
| `1`, `2`, `3` | Alternar entre módulos (Canto, Piedade, Estudo) |
| `j`/`k`/`↓`/`↑`| Navegar em listas                 |
| `Enter`       | Selecionar / Abrir                |
| `v` / `Esc`   | Voltar / Cancelar                 |

### Módulo de Piedade
| Tecla(s) | Ação                               | Contexto                      |
|----------|------------------------------------|-------------------------------|
| `n`      | Abrir menu de nova entrada         | Dashboard de Piedade          |
| `l`      | Listar histórico de entradas       | Dashboard de Piedade          |
| `o`      | Abrir leitor de Orações            | Dashboard de Piedade          |
| `g`      | Abrir Gerenciador de Perguntas     | Dashboard de Piedade          |
| `e`      | Ativar modo de edição              | Formulários                   |
| `s`      | Salvar formulário                  | Formulários                   |
| `Tab`    | Mover para o próximo campo         | Formulários                   |
| `Espaço` | Marcar/desmarcar item              | Assistente de Autoexame       |
| `h` / `l`| Alternar entre painéis             | Gerenciador de Perguntas      |

---

> O código e a arquitetura do projeto foram desenvolvidos com apoio de modelos de IA, a partir de diretrizes conceituais e estruturais humanas. A autoria intelectual permanece humana.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

✝️ Soli Deo Gloria
