use super::{Action, Component, Module};
use crate::{models::CatecismoPergunta, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{style::Stylize, text::{Line, Span}, widgets::{Paragraph, Wrap}, Frame};

pub struct CatecismoAnswerComponent {
    prefix: String,
    question: CatecismoPergunta,
    scroll: u16,
}

impl CatecismoAnswerComponent {
    pub fn new(prefix: &str, question: CatecismoPergunta) -> Self {
        Self {
            prefix: prefix.to_string(),
            question,
            scroll: 0,
        }
    }
}

impl Component for CatecismoAnswerComponent {
    fn get_module(&self) -> Module { Module::Estudo }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut crate::app::App) -> Option<Action> {
        match key.code {
            KeyCode::Char('j') | KeyCode::Down => self.scroll = self.scroll.saturating_add(1),
            KeyCode::Char('k') | KeyCode::Up => self.scroll = self.scroll.saturating_sub(1),
            KeyCode::Char('v') | KeyCode::Esc => return Some(Action::Pop),
            _ => {}
        }
        None
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let title = format!("{} Pergunta {}", self.prefix, self.question.id);
        let txt = vec![
            Line::from(vec![Span::styled("P: ", theme.header_style.bold()), Span::raw(&self.question.question)]),
            Line::from(""),
            Line::from(vec![Span::styled("R: ", theme.header_style.bold()), Span::raw(&self.question.answer)]),
        ];
        let p = Paragraph::new(txt).wrap(Wrap { trim: true }).scroll((self.scroll, 0))
            .block(crate::ui::styled_block(&title, theme)).style(theme.base_style);
        frame.render_widget(p, chunks[1]);
        let footer = Paragraph::new("[j/k] Rolar | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
