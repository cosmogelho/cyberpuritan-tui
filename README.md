# cyberpuritan-tui

Um aplicativo TUI (Terminal User Interface) para auxílio na piedade e estudo teológico pessoal, com foco na tradição puritana reformada.

## Módulos Principais

O sistema é dividido em três seções, acessíveis pelas teclas `1`, `2` e `3`.

### 1. Canto (Saltério)
- **Listagem e Visualização:** Navegue pelos 150 Salmos.
- **Leitura:** Visualize a letra completa do salmo selecionado.
- **Áudio:** Reproduza o áudio instrumental (`t`) ou a capela (`c`) do salmo.

### 2. Piedade (Devocional)
- **Diário:** Crie e visualize entradas de um diário pessoal. A criação de uma nova entrada utiliza o editor de texto padrão do sistema (definido na variável de ambiente `$EDITOR`).
- **Ações de Santificação:** Mantenha uma lista de tarefas para o crescimento espiritual. Ações podem ser marcadas como `pendente` ou `completa`.
- **Resoluções:** Liste e gerencie resoluções pessoais.

### 3. Estudo (Teológico)
- **Símbolos de Fé:** Leia os textos completos da Confissão de Fé de Westminster, do Catecismo Maior de Westminster e do Breve Catecismo de Westminster.
- **Bíblia:** Uma ferramenta para leitura bíblica. Carregue e leia capítulos completos da tradução Almeida Revista e Atualizada (ARA).

## Dependências
- **Externa:** O `mpv` é necessário para a reprodução de áudio. Ele deve estar instalado e acessível no `PATH` do sistema.
- **Rust:** As dependências do projeto estão listadas no arquivo `Cargo.toml`.

## Estrutura de Dados
- **Banco de Dados:** Todas as informações textuais (salmos, diário, símbolos, Bíblia, etc.) são armazenadas em um único banco de dados SQLite em `data/dados.db`.
- **Áudios:** Os arquivos de áudio dos salmos, no formato `.opus`, devem estar no diretório `data/saltério/`.

## Como Executar

Para iniciar a aplicação principal:

```bash
cargo run
Utilitários
O projeto inclui um binário auxiliar para inspecionar os livros e versões da Bíblia disponíveis no banco de dados:

bash
Copiar código
cargo run --bin inspector
Navegação e Atalhos
Tecla(s)	Ação	Contexto
q	Sair do aplicativo	Global
1, 2, 3	Navegar entre os módulos principais	Menu Principal
j / k / ↓ / ↑	Navegar para baixo/cima em listas	Todas as listas
Enter	Selecionar / Ver detalhes do item	Todas as listas
v / Esc	Voltar para a tela anterior	Geral
t	Tocar áudio triunfal (instrumental)	Lista de Salmos
c	Tocar áudio para cantar (a capela)	Lista de Salmos
s	Parar áudio (stop)	Lista de Salmos
n	Criar nova entrada/item	Diário, Ações, Resoluções
d	Deletar item selecionado	Ações, Resoluções
c	Marcar ação como completa	Ações
p	Marcar ação como pendente	Ações
e	Editar comando de busca	Bíblia
Enter	Submeter comando/input	Modo de Edição
Esc	Cancelar edição	Modo de Edição

O cyberpuritan-tui foi desenvolvido sob direção e revisão de cosmogelho, com apoio do Google AI Studio (modelo Gemini 2.5 Pro) para geração inicial de código e documentação.

As decisões conceituais, teológicas e estruturais foram totalmente humanas.

Licença
Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.
