use crate::app::{App, BiblePane, CfwPane, View, Acoes, Resolucoes, Diario};
use crossterm::event::{self, Event, KeyCode, KeyEvent};
use ratatui::widgets::{ListState, TableState};
use std::io;
use std::time::Duration;

pub fn handle_events(app: &mut App) -> io::Result<()> {
    if event::poll(Duration::from_millis(250))? {
        if let Event::Key(key) = event::read()? {
            if key.kind == event::KeyEventKind::Press {
                if let Some(view) = app.view_stack.last().cloned() {
                    // Global keys take precedence
                    match key.code {
                        KeyCode::Char('q') => { app.running = false; return Ok(()); },
                        KeyCode::Esc => { app.pop_view(); return Ok(()); },
                        _ => handle_view_keys(app, &key, &view),
                    }
                }
            }
        }
    }
    Ok(())
}

fn handle_view_keys(app: &mut App, key: &KeyEvent, view: &View) {
    let key_code = key.code;
    match view {
        View::BibleView => handle_bible_keys(app, key_code),
        View::ConfessionView => handle_cfw_keys(app, key_code),
        View::ActionEdit { .. } | View::ResolutionEdit { .. } | View::DiarioEdit { .. } => handle_input_keys(app, key_code, view),
        _ => handle_list_keys(app, key_code, view),
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
            if save_result.is_ok() {
                let _ = app.reload_piety_data();
                app.pop_view();
            }
        },
        KeyCode::Char(c) => app.handle_input(c),
        KeyCode::Backspace => app.handle_backspace(),
        _ => {}
    }
}

fn handle_list_keys(app: &mut App, key: KeyCode, view: &View) {
    match view {
        View::PsalmList => handle_table_nav(key, &mut app.psalm_list_state, app.salmos.len()),
        View::ActionList => handle_table_nav(key, &mut app.action_list_state, app.acoes.len()),
        View::ResolutionList => handle_table_nav(key, &mut app.resolution_list_state, app.resolucoes.len()),
        View::DiarioList => handle_table_nav(key, &mut app.diario_list_state, app.diario.len()),
        View::LargerCatechismView => handle_table_nav(key, &mut app.cmw_list_state, app.cmw.len()),
        View::ShorterCatechismView => handle_table_nav(key, &mut app.bcw_list_state, app.bcw.len()),
        _ => {}
    }

    match view {
        View::PsalmList => handle_psalm_keys(app, key),
        View::PietyMenu => handle_piety_menu_keys(app, key),
        View::StudyMenu => handle_study_menu_keys(app, key),
        View::ActionList => handle_crud_keys(app, key, |s: &Acoes| View::ActionEdit{id: Some(s.id), text: s.descricao.clone()}, View::ActionEdit{id: None, text: String::new()}, |a| { if let Some(sel) = a.action_list_state.selected() { let _ = a.piety_repo.delete_acao(a.acoes[sel].id).and_then(|_| a.reload_piety_data()); }}),
        View::ResolutionList => handle_crud_keys(app, key, |s: &Resolucoes| View::ResolutionEdit{id: Some(s.id), text: s.texto.clone()}, View::ResolutionEdit{id: None, text: String::new()}, |a| { if let Some(sel) = a.resolution_list_state.selected() { let _ = a.piety_repo.delete_resolucao(a.resolucoes[sel].id).and_then(|_| a.reload_piety_data()); }}),
        View::DiarioList => handle_crud_keys(app, key, |s: &Diario| View::DiarioEdit{id: Some(s.id), text: s.texto.clone()}, View::DiarioEdit{id: None, text: String::new()}, |a| { if let Some(sel) = a.diario_list_state.selected() { let _ = a.piety_repo.delete_diario(a.diario[sel].id).and_then(|_| a.reload_piety_data()); }}),
        View::FaithSymbolsMenu => handle_faith_symbols_keys(app, key),
        View::LargerCatechismView => { if key == KeyCode::Enter { app.push_view(View::LargerCatechismDetail); } },
        View::ShorterCatechismView => { if key == KeyCode::Enter { app.push_view(View::ShorterCatechismDetail); } },
        _ => {}
    }
}

fn handle_crud_keys<T: Clone>(app: &mut App, key: KeyCode, edit_view: impl Fn(&T) -> View, new_view: View, delete_fn: impl Fn(&mut App)) {
    match key {
        KeyCode::Char('d') => { if get_selected_index(app).is_some() { delete_fn(app); } },
        KeyCode::Char('n') => app.push_view(new_view),
        KeyCode::Enter => {
            if let Some(index) = get_selected_index(app) {
                if let Some(item) = get_cloned_item::<T>(app, index) {
                    app.push_view(edit_view(&item));
                }
            }
        },
        _ => {}
    }
}
fn get_selected_index(app: &App) -> Option<usize> { match app.view_stack.last() { Some(View::ActionList) => app.action_list_state.selected(), Some(View::ResolutionList) => app.resolution_list_state.selected(), Some(View::DiarioList) => app.diario_list_state.selected(), _ => None } }
fn get_cloned_item<T: Clone>(app: &App, index: usize) -> Option<T> {
    match app.view_stack.last() {
        Some(View::ActionList) => Some(unsafe { &*(&app.acoes[index] as *const _ as *const T) }.clone()),
        Some(View::ResolutionList) => Some(unsafe { &*(&app.resolucoes[index] as *const _ as *const T) }.clone()),
        Some(View::DiarioList) => Some(unsafe { &*(&app.diario[index] as *const _ as *const T) }.clone()),
        _ => None,
    }
}
fn handle_psalm_keys(app: &mut App, key: KeyCode) { match key { KeyCode::Enter => app.push_view(View::PsalmDetail), KeyCode::Char('s') => { let _ = app.stop_playback(); }, KeyCode::Char('t') => { let _ = app.start_playback(false); }, KeyCode::Char('c') => { let _ = app.start_playback(true); }, _ => handle_module_keys(app, key), } }
fn handle_module_keys(app: &mut App, key: KeyCode) { match key { KeyCode::Char('1') => { app.active_module = crate::app::Module::Canto; app.view_stack = vec![View::PsalmList]; }, KeyCode::Char('2') => { app.active_module = crate::app::Module::Piedade; app.view_stack = vec![View::PietyMenu]; }, KeyCode::Char('3') => { app.active_module = crate::app::Module::Estudo; app.view_stack = vec![View::StudyMenu]; }, _ => {} } }
fn handle_piety_menu_keys(app: &mut App, key: KeyCode) { match key { KeyCode::Char('1') => app.push_view(View::ActionList), KeyCode::Char('2') => app.push_view(View::ResolutionList), KeyCode::Char('3') => app.push_view(View::DiarioList), _ => handle_module_keys(app, key), } }
fn handle_study_menu_keys(app: &mut App, key: KeyCode) { match key { KeyCode::Char('1') => app.push_view(View::FaithSymbolsMenu), KeyCode::Char('2') => app.push_view(View::BibleView), _ => handle_module_keys(app, key), } }
fn handle_faith_symbols_keys(app: &mut App, key: KeyCode) { match key { KeyCode::Char('1') => app.push_view(View::ConfessionView), KeyCode::Char('2') => app.push_view(View::LargerCatechismView), KeyCode::Char('3') => app.push_view(View::ShorterCatechismView), _ => {} } }
fn handle_bible_keys(app: &mut App, key: KeyCode) { match key { KeyCode::Char('l') | KeyCode::Tab => app.next_bible_pane(), KeyCode::Enter => match app.bible_state.active_pane { BiblePane::Books => { let _ = app.select_book(); }, BiblePane::Chapters => { let _ = app.select_chapter(); }, BiblePane::Text => {}, }, KeyCode::Char('j') | KeyCode::Down => match app.bible_state.active_pane { BiblePane::Books => handle_list_nav(key, &mut app.bible_state.book_list_state, app.books.len()), BiblePane::Chapters => handle_list_nav(key, &mut app.bible_state.chapter_list_state, app.bible_state.chapters.len()), BiblePane::Text => app.bible_state.text_scroll = app.bible_state.text_scroll.saturating_add(1), }, KeyCode::Char('k') | KeyCode::Up => match app.bible_state.active_pane { BiblePane::Books => handle_list_nav(key, &mut app.bible_state.book_list_state, app.books.len()), BiblePane::Chapters => handle_list_nav(key, &mut app.bible_state.chapter_list_state, app.bible_state.chapters.len()), BiblePane::Text => app.bible_state.text_scroll = app.bible_state.text_scroll.saturating_sub(1), }, _ => {} } }
fn handle_cfw_keys(app: &mut App, key: KeyCode) { match key { KeyCode::Char('l') | KeyCode::Tab => app.next_cfw_pane(), KeyCode::Enter => match app.cfw_state.active_pane { CfwPane::Chapters => app.select_cfw_chapter(), CfwPane::Sections => app.push_view(View::ConfessionDetail), }, _ => match app.cfw_state.active_pane { CfwPane::Chapters => handle_list_nav(key, &mut app.cfw_state.chapter_list_state, app.cfw_state.chapters.len()), CfwPane::Sections => handle_list_nav(key, &mut app.cfw_state.section_list_state, app.cfw_state.sections.len()), } } }
fn handle_table_nav(key: KeyCode, state: &mut TableState, count: usize) { if count == 0 { return; } let i = match state.selected() { Some(i) => match key { KeyCode::Char('j') | KeyCode::Down => if i >= count - 1 { 0 } else { i + 1 }, KeyCode::Char('k') | KeyCode::Up => if i == 0 { count - 1 } else { i - 1 }, _ => i }, None => 0 }; state.select(Some(i)); }
fn handle_list_nav(key: KeyCode, state: &mut ListState, count: usize) { if count == 0 { return; } let i = match state.selected() { Some(i) => match key { KeyCode::Char('j') | KeyCode::Down => if i >= count - 1 { 0 } else { i + 1 }, KeyCode::Char('k') | KeyCode::Up => if i == 0 { count - 1 } else { i - 1 }, _ => i }, None => 0 }; state.select(Some(i)); }
