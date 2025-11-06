use super::{Action, Component, Module};
use crate::{app::App, db, models::CfwSecao, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{widgets::{Paragraph, Wrap}, Frame};

pub struct CfwSectionsComponent {
    title: String,
    sections: Vec<CfwSecao>,
    scroll: u16,
}

impl CfwSectionsComponent {
    pub fn new(chapter_number: i32, title: String) -> Self {
        Self { title, sections: db::ler_secoes_cfw(chapter_number).unwrap_or_default(), scroll: 0 }
    }
}

impl Component for CfwSectionsComponent {
    fn get_module(&self) -> Module { Module::Estudo }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
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
        let text: String = self.sections.iter().map(|s| format!("{}. {}\n\n", s.section, s.text)).collect();
        let title = format!("CFW: {}", self.title);
        let p = Paragraph::new(text).wrap(Wrap { trim: false }).scroll((self.scroll, 0))
            .block(crate::ui::styled_block(&title, theme)).style(theme.base_style);
        frame.render_widget(p, chunks[1]);
        let footer = Paragraph::new("[j/k] Rolar | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
