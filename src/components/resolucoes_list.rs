use super::{Action, Component, Module};
use crate::{app::App, db, models::Resolucao, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Rect},
    widgets::{HighlightSpacing, Paragraph, Row, Table, TableState},
    Frame,
};

enum InputMode { Normal, Editing }

pub struct ResolucoesListComponent {
    state: TableState,
    items: Vec<Resolucao>,
    input: String,
    input_mode: InputMode,
}

impl ResolucoesListComponent {
    pub fn new() -> Self {
        let mut state = TableState::default();
        let items = db::listar_resolucoes().unwrap_or_default();
        if !items.is_empty() { state.select(Some(0)); }
        Self { state, items, input: String::new(), input_mode: InputMode::Normal }
    }
    fn next(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i >= self.items.len() - 1 { 0 } else { i + 1 });
        self.state.select(Some(i));
    }
    fn previous(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i == 0 { self.items.len() - 1 } else { i - 1 });
        self.state.select(Some(i));
    }
    fn get_selected_item_id(&self) -> Option<i32> {
        self.state.selected().and_then(|i| self.items.get(i)).map(|item| item.id)
    }
    fn refresh(&mut self) {
        self.items = db::listar_resolucoes().unwrap_or_default();
        if self.items.is_empty() { self.state.select(None); } else { self.state.select(Some(0)); }
    }
}

impl Component for ResolucoesListComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match self.input_mode {
            InputMode::Normal => match key.code {
                KeyCode::Char('v') | KeyCode::Esc => return Some(Action::Pop),
                KeyCode::Char('j') | KeyCode::Down => self.next(),
                KeyCode::Char('k') | KeyCode::Up => self.previous(),
                KeyCode::Char('n') => self.input_mode = InputMode::Editing,
                KeyCode::Char('d') => { if let Some(id) = self.get_selected_item_id() { db::deletar_resolucao(id).ok(); self.refresh(); } }
                _ => {}
            },
            InputMode::Editing => match key.code {
                KeyCode::Enter => {
                    if !self.input.is_empty() { db::criar_resolucao(&self.input).ok(); self.input.clear(); self.refresh(); }
                    self.input_mode = InputMode::Normal;
                },
                KeyCode::Char(c) => self.input.push(c),
                KeyCode::Backspace => { self.input.pop(); },
                KeyCode::Esc => { self.input.clear(); self.input_mode = InputMode::Normal; },
                _ => {}
            },
        }
        None
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        self.render_table(frame, theme, chunks[1]);
        self.render_footer(frame, theme, chunks[2]);
    }
}

impl ResolucoesListComponent {
    fn render_table(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let h = Row::new(["ID", "Texto"]).style(theme.header_style);
        let r = self.items.iter().map(|item| Row::new(vec![item.id.to_string(), item.texto.clone()]));
        let t = Table::new(r, &[Constraint::Length(4), Constraint::Min(20)])
            .header(h)
            .block(crate::ui::styled_block("Minhas Resoluções", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(t, area, &mut self.state);
    }
    fn render_footer(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let (text, title) = match self.input_mode {
            InputMode::Normal => ("[n] Nova | [d] Deletar | [v] Voltar", "Comandos"),
            InputMode::Editing => { frame.set_cursor(area.x + self.input.len() as u16 + 1, area.y + 1); (self.input.as_str(), "Nova Resolução") }
        };
        frame.render_widget(Paragraph::new(text).block(crate::ui::styled_block(title, theme)), area);
    }
}
