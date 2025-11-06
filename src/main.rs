mod app;
mod db;
mod handler;
mod models;
mod theme;
mod ui;
use crate::app::{App, CurrentScreen, MessageType};
use crossterm::{
    event::{self, Event},
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
    ExecutableCommand,
};
use ratatui::{backend::CrosstermBackend, Terminal};
use std::fs;
use std::io::{self, stdout, Read, Stdout};
use std::process::Command;
use std::time::Duration;
use tempfile::NamedTempFile;

fn main() -> io::Result<()> {
    let salmos = db::listar_salmos().expect("Falha ao carregar salmos.");
    let cfw = db::listar_capitulos_cfw().expect("Falha ao carregar CFW.");
    let cmw = db::listar_perguntas_cmw().expect("Falha ao carregar CMW.");
    let bcw = db::listar_perguntas_bcw().expect("Falha ao carregar BCW.");
    let diario = db::listar_entradas_diario().expect("Falha ao carregar Diário.");
    let acoes = db::listar_acoes().expect("Falha ao carregar Ações.");
    let resolucoes = db::listar_resolucoes().expect("Falha ao carregar Resoluções.");

    let mut terminal = setup_terminal()?;
    let mut app = App::new(salmos, cfw, cmw, bcw, diario, acoes, resolucoes);

    run(&mut terminal, &mut app)?;

    app.stop_audio();
    restore_terminal()?;
    Ok(())
}

fn run(terminal: &mut Terminal<CrosstermBackend<Stdout>>, app: &mut App) -> io::Result<()> {
    while !app.should_quit {
        if let CurrentScreen::DiarioNew = app.current_screen {
            restore_terminal()?;
            app.status_message = match launch_editor_and_save_entry() {
                Ok(msg_tuple) => {
                    app.refresh_diario();
                    msg_tuple
                }
                Err(e) => (format!("Erro: {}", e), MessageType::Error),
            };
            setup_terminal()?;
            app.current_screen = CurrentScreen::DiarioList;
        }
        let _ = terminal.draw(|frame| ui::render(app, frame));
        app.check_audio_process();
        if event::poll(Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                handler::handle_key_events(key, app);
            }
        }
    }
    Ok(())
}

fn launch_editor_and_save_entry() -> io::Result<(String, MessageType)> {
    let editor = std::env::var("EDITOR").unwrap_or_else(|_| "nano".to_string());
    let temp_file = NamedTempFile::new()?;
    let temp_path = temp_file.path();
    let status = Command::new(&editor).arg(temp_path).status()?;

    if !status.success() {
        return Ok(("Criação cancelada.".to_string(), MessageType::Info));
    }
    let mut contents = String::new();
    fs::File::open(temp_path)?.read_to_string(&mut contents)?;
    if contents.trim().is_empty() {
        return Ok(("Criação cancelada (vazio).".to_string(), MessageType::Info));
    }

    match db::criar_entrada_diario(&contents) {
        Ok(_) => Ok(("Nova entrada salva!".to_string(), MessageType::Success)),
        Err(_) => Ok(("Erro ao salvar no banco.".to_string(), MessageType::Error)),
    }
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
