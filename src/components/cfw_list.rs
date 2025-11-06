use super::{cfw_sections::CfwSectionsComponent, Action, Component, Module};
use crate::{app::App, db, models::CfwCapitulo, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{layout::Constraint, widgets::{HighlightSpacing, Paragraph, Row, Table, TableState}, Frame};

pub struct CfwListComponent {
    state: TableState,
    chapters: Vec<CfwCapitulo>,
}

impl CfwListComponent {
    pub fn new() -> Self {
        let mut state = TableState::default();
        let chapters = db::listar_capitulos_cfw().unwrap_or_default();
        if !chapters.is_empty() { state.select(Some(0)); }
        Self { state, chapters }
    }
    fn next(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i >= self.chapters.len() - 1 { 0 } else { i + 1 });
        self.state.select(Some(i));
    }
    fn previous(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i == 0 { self.chapters.len() - 1 } else { i - 1 });
        self.state.select(Some(i));
    }
    fn get_selected_chapter(&self) -> Option<&CfwCapitulo> {
        self.state.selected().and_then(|i| self.chapters.get(i))
    }
}

impl Component for CfwListComponent {
    fn get_module(&self) -> Module { Module::Estudo }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('v') | KeyCode::Esc => Some(Action::Pop),
            KeyCode::Char('j') | KeyCode::Down => { self.next(); None },
            KeyCode::Char('k') | KeyCode::Up => { self.previous(); None },
            KeyCode::Enter => self.get_selected_chapter().map(|c| Action::Navigate(Box::new(CfwSectionsComponent::new(c.chapter, c.title.clone())))),
            _ => None,
        }
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let h = Row::new(["Cap.", "Título"]).style(theme.header_style);
        let r = self.chapters.iter().map(|c| Row::new([c.chapter.to_string(), c.title.clone()]));
        let t = Table::new(r, &[Constraint::Length(5), Constraint::Min(20)])
            .header(h)
            .block(crate::ui::styled_block("Confissão de Fé", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(t, chunks[1], &mut self.state);
        let footer = Paragraph::new("[Enter] Ver | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
