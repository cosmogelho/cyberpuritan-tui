use crate::app::{App, CurrentScreen, InputMode};
use crate::db;
use crossterm::event::{KeyCode, KeyEvent, KeyEventKind};

fn handle_normal_mode(key: KeyEvent, app: &mut App) {
    if let KeyCode::Char('q') = key.code {
        app.quit();
        return;
    }

    match app.current_screen {
        CurrentScreen::SalterioList => match key.code {
            KeyCode::Char('2') => app.current_screen = CurrentScreen::PiedadeMenu,
            KeyCode::Char('3') => app.current_screen = CurrentScreen::EstudoMenu,
            KeyCode::Enter => app.enter_salmo_view(),
            KeyCode::Char('j') | KeyCode::Down => app.next(),
            KeyCode::Char('k') | KeyCode::Up => app.previous(),
            KeyCode::Char('t') => app.play_audio("instrumental"),
            KeyCode::Char('c') => app.play_audio("a_capela"),
            KeyCode::Char('s') => app.stop_audio(),
            _ => {}
        },
        CurrentScreen::SalmoView => match key.code {
            KeyCode::Char('j') | KeyCode::Down => app.next(),
            KeyCode::Char('k') | KeyCode::Up => app.previous(),
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::SalterioList,
            _ => {}
        },
        CurrentScreen::PiedadeMenu => match key.code {
            KeyCode::Char('1') => app.current_screen = CurrentScreen::DiarioList,
            KeyCode::Char('2') => app.current_screen = CurrentScreen::AcoesList,
            KeyCode::Char('3') => app.current_screen = CurrentScreen::ResolucoesList,
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::SalterioList,
            _ => {}
        },
        // ... outras telas ...
        CurrentScreen::AcoesList => match key.code {
            KeyCode::Char('j') | KeyCode::Down => app.next(),
            KeyCode::Char('k') | KeyCode::Up => app.previous(),
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::PiedadeMenu,
            KeyCode::Char('n') => app.input_mode = InputMode::Editing,
            KeyCode::Char('d') | KeyCode::Char('c') | KeyCode::Char('p') => {
                if let Some(index) = app.acoes_list_state.selected() {
                    if let Some(acao) = app.acoes.get(index) {
                        let id = acao.id;
                        let success = match key.code {
                            KeyCode::Char('d') => db::deletar_acao(id).is_ok(),
                            KeyCode::Char('c') => db::atualizar_status_acao(id, "completo").is_ok(),
                            KeyCode::Char('p') => db::atualizar_status_acao(id, "pendente").is_ok(),
                            _ => false,
                        };
                        if success {
                            app.refresh_acoes();
                        }
                    }
                }
            }
            _ => {}
        },
        CurrentScreen::ResolucoesList => match key.code {
            KeyCode::Char('j') | KeyCode::Down => app.next(),
            KeyCode::Char('k') | KeyCode::Up => app.previous(),
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::PiedadeMenu,
            KeyCode::Char('n') => app.input_mode = InputMode::Editing,
            KeyCode::Char('d') => {
                if let Some(index) = app.resolucoes_list_state.selected() {
                    if let Some(res) = app.resolucoes.get(index) {
                        if db::deletar_resolucao(res.id).is_ok() {
                            app.refresh_resolucoes();
                        }
                    }
                }
            }
            _ => {}
        },
        CurrentScreen::EstudoMenu => match key.code {
            KeyCode::Char('1') => app.current_screen = CurrentScreen::SymbolsMenu,
            KeyCode::Char('2') => app.current_screen = CurrentScreen::Biblia,
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::SalterioList,
            _ => {}
        },
        CurrentScreen::SymbolsMenu => match key.code {
            KeyCode::Char('1') => app.current_screen = CurrentScreen::CfwList,
            KeyCode::Char('2') => app.current_screen = CurrentScreen::CmwList,
            KeyCode::Char('3') => app.current_screen = CurrentScreen::BcwList,
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::EstudoMenu,
            _ => {}
        },
        CurrentScreen::DiarioList => match key.code {
            KeyCode::Char('n') => app.current_screen = CurrentScreen::DiarioNew,
            KeyCode::Char('j') | KeyCode::Down => app.next(),
            KeyCode::Char('k') | KeyCode::Up => app.previous(),
            KeyCode::Enter => app.enter_diario_view(),
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::PiedadeMenu,
            _ => {}
        },
        CurrentScreen::CfwList | CurrentScreen::CmwList | CurrentScreen::BcwList => {
            match key.code {
                KeyCode::Char('j') | KeyCode::Down => app.next(),
                KeyCode::Char('k') | KeyCode::Up => app.previous(),
                KeyCode::Enter => match app.current_screen {
                    CurrentScreen::CfwList => app.enter_cfw_chapter_view(),
                    CurrentScreen::CmwList => app.enter_cmw_answer_view(),
                    CurrentScreen::BcwList => app.enter_bcw_answer_view(),
                    _ => {}
                },
                KeyCode::Char('v') | KeyCode::Esc => {
                    app.current_screen = CurrentScreen::SymbolsMenu
                }
                _ => {}
            }
        }
        CurrentScreen::DiarioView
        | CurrentScreen::CfwSections
        | CurrentScreen::CmwAnswer
        | CurrentScreen::BcwAnswer => match key.code {
            KeyCode::Char('j') | KeyCode::Down => app.next(),
            KeyCode::Char('k') | KeyCode::Up => app.previous(),
            KeyCode::Char('v') | KeyCode::Esc => match app.current_screen {
                CurrentScreen::DiarioView => app.current_screen = CurrentScreen::DiarioList,
                CurrentScreen::CfwSections => app.current_screen = CurrentScreen::CfwList,
                CurrentScreen::CmwAnswer => app.current_screen = CurrentScreen::CmwList,
                CurrentScreen::BcwAnswer => app.current_screen = CurrentScreen::BcwList,
                _ => {}
            },
            _ => {}
        },
        CurrentScreen::Biblia => match key.code {
            KeyCode::Char('j') | KeyCode::Down => app.next(),
            KeyCode::Char('k') | KeyCode::Up => app.previous(),
            KeyCode::Char('e') => app.input_mode = InputMode::Editing,
            KeyCode::Char('v') | KeyCode::Esc => app.current_screen = CurrentScreen::EstudoMenu,
            _ => {}
        },
        _ => {}
    }
}
pub fn handle_key_events(key: KeyEvent, app: &mut App) {
    if key.kind != KeyEventKind::Press {
        return;
    }
    match app.input_mode {
        InputMode::Normal => handle_normal_mode(key, app),
        InputMode::Editing => match key.code {
            KeyCode::Enter => app.submit_command(),
            KeyCode::Char(c) => app.input.push(c),
            KeyCode::Backspace => {
                app.input.pop();
            }
            KeyCode::Esc => {
                app.input.clear();
                app.input_mode = InputMode::Normal;
            }
            _ => {}
        },
    }
}
