mod app;
mod components;
mod db;
mod models;
mod theme;
mod ui;
use crate::{
    app::App,
    components::{salterio_list::SalterioListComponent, Action},
};
use crossterm::{
    event::{self, Event},
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
    ExecutableCommand,
};
use ratatui::{backend::CrosstermBackend, Terminal};
use rusqlite::Connection;
use std::io::{self, stdout, Stdout};
use std::path::Path;
use std::time::Duration;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    criar_banco_se_nao_existir();
    let mut terminal = setup_terminal()?;
    let mut app = App::new();
    app.push_component(Box::new(SalterioListComponent::new()));
    let run_result = run(&mut terminal, &mut app);
    app.stop_audio();
    restore_terminal()?;
    run_result?;
    Ok(())
}

fn run(terminal: &mut Terminal<CrosstermBackend<Stdout>>, app: &mut App) -> io::Result<()> {
    while !app.should_quit {
        terminal.draw(|frame| ui::render(frame, app))?;
        app.check_audio_process();
        if event::poll(Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                if let Some(mut component) = app.component_stack.pop() {
                    let action = component.handle_key_events(key, app);

                    if let Some(action) = action {
                        match action {
                            Action::Quit => app.quit(),
                            Action::Pop => (), // Component is not pushed back
                            Action::Navigate(new_component) => {
                                app.component_stack.push(component);
                                app.component_stack.push(new_component);
                            }
                        }
                    } else {
                        // No action, push the component back
                        app.component_stack.push(component);
                    }
                }
            }
        }
        if app.component_stack.is_empty() {
            app.quit();
        }
    }
    Ok(())
}

fn setup_terminal() -> io::Result<Terminal<CrosstermBackend<Stdout>>> {
    enable_raw_mode()?;
    stdout().execute(EnterAlternateScreen)?;
    Terminal::new(CrosstermBackend::new(stdout()))
}
fn restore_terminal() -> io::Result<()> {
    disable_raw_mode()?;
    stdout().execute(LeaveAlternateScreen)?;
    Ok(())
}
fn criar_banco_se_nao_existir() {
    let base_dir = format!("{}/data", env!("CARGO_MANIFEST_DIR"));
    let caminho = format!("{}/piety.db", base_dir);
    if Path::new(&caminho).exists() {
        return;
    }
    std::fs::create_dir_all(base_dir).unwrap();
    let conexao = Connection::open(caminho).unwrap();
    conexao
        .execute_batch(
            "
        -- Tabela Central
        CREATE TABLE diario_entradas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'AUTO_EXAME', 'SERMAO', 'RESOLUCAO', 'LEITURA', 'JEJUM', 'NOTA', 'EVANGELISMO'
            passo_pratico TEXT,
            tags TEXT
        );

        -- Tabelas Específicas
        CREATE TABLE entradas_auto_exame(
            id INTEGER PRIMARY KEY, -- FK para diario_entradas.id
            respostas TEXT -- Armazenar como JSON: [{'pergunta_id': 1, 'avaliacao': 'Boa'}, ...]
        );
        CREATE TABLE entradas_sermoes(
            id INTEGER PRIMARY KEY, -- FK para diario_entradas.id
            pregador TEXT,
            titulo TEXT,
            passagens TEXT,
            pontos_chave TEXT,
            aplicacao_pessoal TEXT
        );
        CREATE TABLE entradas_resolucoes(
            id INTEGER PRIMARY KEY, -- FK para diario_entradas.id
            numero_edwards INTEGER,
            texto_resolucao TEXT NOT NULL,
            objetivo_concreto TEXT,
            metrica TEXT,
            status TEXT DEFAULT 'ativa'
        );
        CREATE TABLE entradas_leitura_biblica(
            id INTEGER PRIMARY KEY, -- FK para diario_entradas.id
            tema_semanal TEXT,
            passagens_lidas TEXT,
            salmo_do_dia TEXT,
            aplicacao TEXT
        );
        CREATE TABLE entradas_jejum(
            id INTEGER PRIMARY KEY, -- FK para diario_entradas.id
            tipo_jejum TEXT NOT NULL,
            proposito TEXT,
            observacoes TEXT
        );
        CREATE TABLE entradas_evangelismo(
            id INTEGER PRIMARY KEY, -- FK para diario_entradas.id
            tipo_contato TEXT,
            resultado TEXT,
            observacao TEXT
        );
        CREATE TABLE perguntas_usuario(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            texto_pergunta TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1
        );
        ",
        )
        .unwrap();
}
