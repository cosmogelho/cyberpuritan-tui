use crate::app::{App, BiblePane, View, Acoes, Resolucoes, Diario};
use crossterm::event::{self, Event, KeyCode, KeyEvent};
use ratatui::widgets::{ListState, TableState};
use std::io;
use std::time::Duration;

pub fn handle_events(app: &mut App) -> io::Result<()> {
    if !event::poll(Duration::from_millis(250))? { return Ok(()); }
    if let Event::Key(key) = event::read()? {
        if key.kind != event::KeyEventKind::Press { return Ok(()); }

        if let Some(view) = app.view_stack.last().cloned() {
            // Teclas globais (sempre ativas)
            if key.code == KeyCode::Char('q') { app.running = false; return Ok(()); }
            if key.code == KeyCode::Esc { app.pop_view(); return Ok(()); }

            // Lógica específica da View
            handle_view_keys(app, &key, &view);
        }
    }
    Ok(())
}

fn handle_view_keys(app: &mut App, key: &KeyEvent, view: &View) {
    let key_code = key.code;
    match view {
        View::PsalmList => handle_psalm_list_keys(app, key_code),
        View::PietyMenu => handle_piety_menu_keys(app, key_code),
        View::StudyMenu => handle_study_menu_keys(app, key_code),
        View::BibleView => handle_bible_keys(app, key_code),
        View::ActionList | View::ResolutionList | View::DiarioList => handle_crud_list_keys(app, key_code, view),
        View::ActionEdit { .. } | View::ResolutionEdit { .. } | View::DiarioEdit { .. } => handle_input_keys(app, key_code, view),
        View::FaithSymbolsMenu => handle_faith_symbols_keys(app, key_code),
        View::ConfessionView | View::LargerCatechismView | View::ShorterCatechismView => handle_symbol_list_keys(app, key_code, view),
        _ => {}
    }
}

// === Handlers Específicos por View ===

fn handle_psalm_list_keys(app: &mut App, key: KeyCode) {
    handle_table_nav(key, &mut app.psalm_list_state, app.salmos.len());
    match key {
        KeyCode::Char('2') => { app.active_module = crate::app::Module::Piedade; app.view_stack = vec![View::PietyMenu]; },
        KeyCode::Char('3') => { app.active_module = crate::app::Module::Estudo; app.view_stack = vec![View::StudyMenu]; },
        KeyCode::Enter => app.push_view(View::PsalmDetail),
        KeyCode::Char('s') => { let _ = app.stop_playback(); },
        KeyCode::Char('t') => { let _ = app.start_playback(false); },
        KeyCode::Char('c') => { let _ = app.start_playback(true); },
        _ => {}
    }
}

fn handle_piety_menu_keys(app: &mut App, key: KeyCode) {
    match key {
        KeyCode::Char('1') => app.push_view(View::ActionList),
        KeyCode::Char('2') => app.push_view(View::ResolutionList),
        KeyCode::Char('3') => app.push_view(View::DiarioList),
        _ => handle_module_keys(app, key), // Permite trocar de módulo
    }
}

fn handle_study_menu_keys(app: &mut App, key: KeyCode) {
    match key {
        KeyCode::Char('1') => app.push_view(View::FaithSymbolsMenu),
        KeyCode::Char('2') => app.push_view(View::BibleView),
        _ => handle_module_keys(app, key), // Permite trocar de módulo
    }
}

fn handle_input_keys(app: &mut App, key: KeyCode, view: &View) {
    match key {
        KeyCode::Enter => {
            let save_result = match view {
                View::ActionEdit { id, text } => if let Some(i) = id { app.piety_repo.update_acao(*i, text) } else { app.piety_repo.create_acao(text) },
                View::ResolutionEdit { id, text } => if let Some(i) = id { app.piety_repo.update_resolucao(*i, text) } else { app.piety_repo.create_resolucao(text) },
                View::DiarioEdit { id, text } => if let Some(i) = id { app.piety_repo.update_diario(*i, text) } else { app.piety_repo.create_diario(text) },
                _ => Ok(()),
            };
            if save_result.is_ok() { let _ = app.reload_piety_data(); app.pop_view(); }
        },
        KeyCode::Char(c) => app.handle_input(c),
        KeyCode::Backspace => app.handle_backspace(),
        _ => {}
    }
}

fn handle_crud_list_keys(app: &mut App, key: KeyCode, view: &View) {
    match view {
        View::ActionList => handle_table_nav(key, &mut app.action_list_state, app.acoes.len()),
        View::ResolutionList => handle_table_nav(key, &mut app.resolution_list_state, app.resolucoes.len()),
        View::DiarioList => handle_table_nav(key, &mut app.diario_list_state, app.diario.len()),
        _ => {}
    }
    match key {
        KeyCode::Char('d') => match view {
            View::ActionList => { if let Some(sel) = app.action_list_state.selected() { let _ = app.piety_repo.delete_acao(app.acoes[sel].id).and_then(|_| app.reload_piety_data()); } },
            View::ResolutionList => { if let Some(sel) = app.resolution_list_state.selected() { let _ = app.piety_repo.delete_resolucao(app.resolucoes[sel].id).and_then(|_| app.reload_piety_data()); } },
            View::DiarioList => { if let Some(sel) = app.diario_list_state.selected() { let _ = app.piety_repo.delete_diario(app.diario[sel].id).and_then(|_| app.reload_piety_data()); } },
            _ => {}
        },
        KeyCode::Char('n') => match view {
            View::ActionList => app.push_view(View::ActionEdit{id: None, text: String::new()}),
            View::ResolutionList => app.push_view(View::ResolutionEdit{id: None, text: String::new()}),
            View::DiarioList => app.push_view(View::DiarioEdit{id: None, text: String::new()}),
            _ => {}
        },
        KeyCode::Enter => match view {
            View::ActionList => { if let Some(sel) = app.action_list_state.selected() { let a = &app.acoes[sel]; app.push_view(View::ActionEdit{id: Some(a.id), text: a.descricao.clone()}); } },
            View::ResolutionList => { if let Some(sel) = app.resolution_list_state.selected() { let r = &app.resolucoes[sel]; app.push_view(View::ResolutionEdit{id: Some(r.id), text: r.texto.clone()}); } },
            View::DiarioList => { if let Some(sel) = app.diario_list_state.selected() { let d = &app.diario[sel]; app.push_view(View::DiarioEdit{id: Some(d.id), text: d.texto.clone()}); } },
            _ => {}
        },
        _ => {}
    }
}

fn handle_symbol_list_keys(app: &mut App, key: KeyCode, view: &View) {
    match view {
        View::ConfessionView => handle_table_nav(key, &mut app.cfw_list_state, app.cfw.len()),
        View::LargerCatechismView => handle_table_nav(key, &mut app.cmw_list_state, app.cmw.len()),
        View::ShorterCatechismView => handle_table_nav(key, &mut app.bcw_list_state, app.bcw.len()),
        _ => {}
    }
    if key == KeyCode::Enter {
        match view {
            View::ConfessionView => app.push_view(View::ConfessionDetail),
            View::LargerCatechismView => app.push_view(View::LargerCatechismDetail),
            View::ShorterCatechismView => app.push_view(View::ShorterCatechismDetail),
            _ => {}
        }
    }
}

fn handle_faith_symbols_keys(app: &mut App, key: KeyCode) {
    match key {
        KeyCode::Char('1') => app.push_view(View::ConfessionView),
        KeyCode::Char('2') => app.push_view(View::LargerCatechismView),
        KeyCode::Char('3') => app.push_view(View::ShorterCatechismView),
        _ => {}
    }
}

fn handle_bible_keys(app: &mut App, key: KeyCode) {
    match key {
        KeyCode::Char('l') | KeyCode::Tab => app.next_bible_pane(),
        KeyCode::Enter => match app.bible_state.active_pane {
            BiblePane::Books => { let _ = app.select_book(); },
            BiblePane::Chapters => { let _ = app.select_chapter(); },
            BiblePane::Text => {},
        },
        KeyCode::Char('j') | KeyCode::Down => match app.bible_state.active_pane {
            BiblePane::Books => handle_list_nav(key, &mut app.bible_state.book_list_state, app.books.len()),
            BiblePane::Chapters => handle_list_nav(key, &mut app.bible_state.chapter_list_state, app.bible_state.chapters.len()),
            BiblePane::Text => app.bible_state.text_scroll = app.bible_state.text_scroll.saturating_add(1),
        },
        KeyCode::Char('k') | KeyCode::Up => match app.bible_state.active_pane {
            BiblePane::Books => handle_list_nav(key, &mut app.bible_state.book_list_state, app.books.len()),
            BiblePane::Chapters => handle_list_nav(key, &mut app.bible_state.chapter_list_state, app.bible_state.chapters.len()),
            BiblePane::Text => app.bible_state.text_scroll = app.bible_state.text_scroll.saturating_sub(1),
        },
        _ => {}
    }
}

fn handle_module_keys(app: &mut App, key: KeyCode) {
    match key {
        KeyCode::Char('1') => { app.active_module = crate::app::Module::Canto; app.view_stack = vec![View::PsalmList]; },
        KeyCode::Char('2') => { app.active_module = crate::app::Module::Piedade; app.view_stack = vec![View::PietyMenu]; },
        KeyCode::Char('3') => { app.active_module = crate::app::Module::Estudo; app.view_stack = vec![View::StudyMenu]; },
        _ => {}
    }
}

fn handle_table_nav(key: KeyCode, state: &mut TableState, count: usize) {
    if count == 0 { return; }
    let i = match state.selected() {
        Some(i) => match key {
            KeyCode::Char('j') | KeyCode::Down => if i >= count - 1 { 0 } else { i + 1 },
            KeyCode::Char('k') | KeyCode::Up => if i == 0 { count - 1 } else { i - 1 },
            _ => i
        },
        None => 0,
    };
    state.select(Some(i));
}

fn handle_list_nav(key: KeyCode, state: &mut ListState, count: usize) {
    if count == 0 { return; }
    let i = match state.selected() {
        Some(i) => match key {
            KeyCode::Char('j') | KeyCode::Down => if i >= count - 1 { 0 } else { i + 1 },
            KeyCode::Char('k') | KeyCode::Up => if i == 0 { count - 1 } else { i - 1 },
            _ => i
        },
        None => 0,
    };
    state.select(Some(i));
}
