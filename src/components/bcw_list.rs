use super::{bcw_answer::BcwAnswerComponent, Action, Component, Module};
use crate::{app::App, db, models::CatecismoPergunta, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{layout::Constraint, widgets::{HighlightSpacing, Paragraph, Row, Table, TableState}, Frame};

pub struct BcwListComponent {
    state: TableState,
    questions: Vec<CatecismoPergunta>,
}

impl BcwListComponent {
    pub fn new() -> Self {
        let mut state = TableState::default();
        let questions = db::listar_perguntas_bcw().unwrap_or_default();
        if !questions.is_empty() { state.select(Some(0)); }
        Self { state, questions }
    }
    fn next(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i >= self.questions.len() - 1 { 0 } else { i + 1 });
        self.state.select(Some(i));
    }
    fn previous(&mut self) {
        let i = self.state.selected().map_or(0, |i| if i == 0 { self.questions.len() - 1 } else { i - 1 });
        self.state.select(Some(i));
    }
    fn get_selected_item(&self) -> Option<&CatecismoPergunta> {
        self.state.selected().and_then(|i| self.questions.get(i))
    }
}

impl Component for BcwListComponent {
    fn get_module(&self) -> Module { Module::Estudo }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('v') | KeyCode::Esc => Some(Action::Pop),
            KeyCode::Char('j') | KeyCode::Down => { self.next(); None },
            KeyCode::Char('k') | KeyCode::Up => { self.previous(); None },
            KeyCode::Enter => self.get_selected_item().map(|q| Action::Navigate(Box::new(BcwAnswerComponent::new(q.clone())))),
            _ => None,
        }
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let h = Row::new(["Per.", "Pergunta"]).style(theme.header_style);
        let r = self.questions.iter().map(|p| Row::new([p.id.to_string(), p.question.clone()]));
        let t = Table::new(r, &[Constraint::Length(5), Constraint::Min(20)])
            .header(h)
            .block(crate::ui::styled_block("Breve Catecismo", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(t, chunks[1], &mut self.state);
        let footer = Paragraph::new("[Enter] Ver | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
