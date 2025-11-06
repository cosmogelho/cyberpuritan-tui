use super::{diario_view::DiarioViewComponent, Action, Component, Module};
use crate::{app::App, db, models::EntradaDiario, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Rect},
    widgets::{HighlightSpacing, Paragraph, Row, Table, TableState},
    Frame,
};

pub struct DiarioListComponent {
    state: TableState,
    entries: Vec<EntradaDiario>,
}

impl DiarioListComponent {
    pub fn new() -> Self {
        let mut state = TableState::default();
        let entries = db::listar_entradas_diario().unwrap_or_default();
        if !entries.is_empty() { state.select(Some(0)); }
        Self { state, entries }
    }
    fn next(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i >= self.entries.len() - 1 { 0 } else { i + 1 });
        self.state.select(Some(i));
    }
    fn previous(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i == 0 { self.entries.len() - 1 } else { i - 1 });
        self.state.select(Some(i));
    }
    fn get_selected_entry(&self) -> Option<&EntradaDiario> {
        self.state.selected().and_then(|i| self.entries.get(i))
    }
    fn refresh_entries(&mut self) {
        self.entries = db::listar_entradas_diario().unwrap_or_default();
        if self.entries.is_empty() { self.state.select(None); }
        else { self.state.select(Some(0)); }
    }
}

impl Component for DiarioListComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('n') => {
                let action = Some(Action::LaunchEditor);
                self.refresh_entries();
                return action;
            }
            KeyCode::Char('j') | KeyCode::Down => self.next(),
            KeyCode::Char('k') | KeyCode::Up => self.previous(),
            KeyCode::Enter => {
                if let Some(entry) = self.get_selected_entry() {
                    return Some(Action::Navigate(Box::new(DiarioViewComponent::new(entry.clone()))));
                }
            }
            KeyCode::Char('v') | KeyCode::Esc => return Some(Action::Pop),
            _ => {}
        }
        None
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        self.render_table(frame, theme, chunks[1]);
        self.render_footer(frame, theme, chunks[2]);
    }
}

impl DiarioListComponent {
    fn render_table(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let h = Row::new(["Data", "Início da Entrada"]).style(theme.header_style);
        let r = self.entries.iter().map(|e| {
            let preview = e.texto.chars().take(80).collect::<String>() + "...";
            Row::new(vec![e.data.clone(), preview])
        });
        let t = Table::new(r, &[Constraint::Length(20), Constraint::Min(20)])
            .header(h)
            .block(crate::ui::styled_block("Diário", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(t, area, &mut self.state);
    }
    fn render_footer(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let p = Paragraph::new("[n] Nova Entrada | [Enter] Ver | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(p, area);
    }
}
