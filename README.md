# 🕊️ cyberpuritan-tui

Um aplicativo **TUI (Terminal User Interface)** para auxílio na **piedade e estudo teológico pessoal**, com foco na **tradição puritana reformada** e na **prática devocional diária**.

---

## 📖 Sobre o Projeto

O **Cyberpuritan TUI** foi concebido como uma ferramenta para o cristão reformado cultivar a piedade, organizar seus estudos e refletir espiritualmente — tudo dentro do terminal, com simplicidade e foco.

O sistema é dividido em três módulos principais, acessíveis pelas teclas `1`, `2` e `3`.

---

## 🔹 1. Canto — *Saltério de Genebra*

- **Listagem e Visualização:** Navegue pelos **150 Salmos** metrificados.
- **Leitura:** Visualize a letra completa de cada salmo.
- **Áudio:**
  - `t` — reproduz o áudio **instrumental** (todos os salmos possuem);
  - `c` — reproduz o áudio **a capela (cantado)** (disponível apenas para alguns).
- **Fonte:** Os salmos são do **Saltério de Genebra**, conforme edição e compilação da  
  **Comissão Brasileira de Salmodia** e dos irmãos **Arthur Elohim Pires, Lucas Grassi Freire e Vítor Augusto Olivier**.  
  📜 Site oficial: [https://salteriodegenebra.com.br/](https://salteriodegenebra.com.br/)

> 💡 Os metadados incluem indicação de autoria, metrificação e informações complementares de cada salmo.

---

## 🔹 2. Piedade — *Vida Devocional*

- **Diário:** Crie e visualize entradas pessoais no diário devocional.  
  (As edições usam o editor de texto padrão definido em `$EDITOR`.)
- **Ações de Santificação:** Registre e acompanhe ações práticas de piedade, marcando como `pendente` ou `completa`.
- **Resoluções:** Anote e gerencie suas resoluções espirituais pessoais.

---

## 🔹 3. Estudo — *Teologia e Escritura*

- **Símbolos de Fé:** Leitura integral da  
  - *Confissão de Fé de Westminster*  
  - *Catecismo Maior de Westminster*  
  - *Breve Catecismo de Westminster*
- **Bíblia:** Ferramenta de leitura bíblica com capítulos completos da tradução **Almeida Revista e Atualizada (ARA)**.

---

## 🧰 Dependências

- **Rust:** As dependências estão listadas em `Cargo.toml`.  
- **Externa:**  
  - [`mpv`](https://mpv.io/) — necessário para reprodução de áudio.  
    Certifique-se de que está instalado e acessível no `PATH`.

---

## 🗂️ Estrutura de Dados

- **Banco fixo (`canon.db`):** Contém textos teológicos, catecismos, confissões e Escritura.
- **Banco pessoal (`piety.db`):** Armazena suas anotações, diários, ações e resoluções.  
  É criado automaticamente na primeira execução, caso não exista.
- **Áudios:**  
  - Local: `data/saltério/`  
  - Formato: `.opus`  
  - Contém todos os instrumentais (mas nem todos "à capela").

---

## Como Executar

Para iniciar a aplicação principal:

```bash
cargo run
```
O aplicativo criará automaticamente o banco pessoal (data/piety.db) caso ainda não exista.

## Navegação e Atalhos

| Tecla(s)              | Ação                                    | Contexto                  |
| --------------------- | --------------------------------------- | ------------------------- |
| `q`                   | Sair do aplicativo                      | Global                    |
| `1`, `2`, `3`         | Navegar entre os módulos principais     | Menu Principal            |
| `j` / `k` / `↓` / `↑` | Navegar para baixo/cima em listas       | Todas as listas           |
| `Enter`               | Selecionar / Ver detalhes do item       | Todas as listas           |
| `v` / `Esc`           | Voltar para a tela anterior             | Geral                     |
| `t`                   | Tocar áudio **t**riunfal (instrumental) | Lista de Salmos           |
| `c`                   | Tocar áudio para **c**antar (a capela)  | Lista de Salmos           |
| `s`                   | Parar áudio (**s**top)                  | Lista de Salmos           |
| `n`                   | Criar **n**ova entrada/item             | Diário, Ações, Resoluções |
| `d`                   | **D**eletar item selecionado            | Ações, Resoluções         |
| `c`                   | Marcar ação como **c**ompleta           | Ações                     |
| `p`                   | Marcar ação como **p**endente           | Ações                     |
| `e`                   | **E**ditar comando de busca             | Bíblia                    |
| `Enter`               | Submeter comando/input                  | Modo de Edição            |
| `Esc`                 | Cancelar edição                         | Modo de Edição            |

---

> O código e a arquitetura do projeto foram desenvolvidos com apoio intenso de modelos de IA (incluindo o Google Gemini 2.5 Pro e o ChatGPT GPT-5), a partir de diretrizes conceituais, teológicas e estruturais inteiramente humanas.
>
> A autoria intelectual e teológica permanece 100% humana, enquanto a implementação foi amplamente auxiliada por IA.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

✝️ Soli Deo Gloria
