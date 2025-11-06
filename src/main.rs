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
use std::io::{self, stdout, Read, Stdout};
use std::path::Path;
use std::time::Duration;
use tempfile::NamedTempFile;

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
                            Action::LaunchEditor => {
                                app.component_stack.push(component);
                                restore_terminal()?;
                                let _ = launch_editor_and_save_entry();
                                enable_raw_mode()?;
                                stdout().execute(EnterAlternateScreen)?;
                                terminal.clear()?;
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

fn launch_editor_and_save_entry() -> io::Result<()> {
    use std::{fs, process::Command};
    let editor = std::env::var("EDITOR").unwrap_or_else(|_| "nano".to_string());
    let temp_file = NamedTempFile::new()?;
    let temp_path = temp_file.path();
    if !Command::new(&editor).arg(temp_path).status()?.success() {
        return Ok(());
    }
    let mut contents = String::new();
    fs::File::open(temp_path)?.read_to_string(&mut contents)?;
    if !contents.trim().is_empty() {
        db::criar_entrada_diario(&contents).ok();
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
    let caminho = "data/piety.db";
    if Path::new(caminho).exists() { return; }
    std::fs::create_dir_all("data").unwrap();
    let conexao = Connection::open(caminho).unwrap();
    conexao.execute_batch(
        "
        CREATE TABLE diario(id INTEGER PRIMARY KEY, data TEXT, texto TEXT);
        CREATE TABLE acoes(id INTEGER PRIMARY KEY, descricao TEXT, status TEXT, data_criacao TEXT);
        CREATE TABLE resolucoes(id INTEGER PRIMARY KEY, texto TEXT, data_criacao TEXT);
        CREATE TABLE sermoes(id INTEGER PRIMARY KEY, titulo TEXT, tema TEXT, pregador TEXT, local TEXT, data TEXT, link TEXT, passagem_principal TEXT);
        CREATE TABLE notas_estudo(id INTEGER PRIMARY KEY, referencia_biblica TEXT, texto TEXT, data_criacao TEXT);
        ").unwrap();
}
