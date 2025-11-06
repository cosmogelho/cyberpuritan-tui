use super::{Action, Component, Module};
use crate::{models::Salmo, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{widgets::{Paragraph, Wrap}, Frame};

pub struct SalmoViewComponent {
    pub salmo: Salmo,
    pub scroll: u16,
}

impl SalmoViewComponent {
    pub fn new(salmo: Salmo) -> Self { Self { salmo, scroll: 0 } }
}

impl Component for SalmoViewComponent {
    fn get_module(&self) -> Module { Module::Canto }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut crate::app::App) -> Option<Action> {
        match key.code {
            KeyCode::Char('j') | KeyCode::Down => self.scroll = self.scroll.saturating_add(1),
            KeyCode::Char('k') | KeyCode::Up => self.scroll = self.scroll.saturating_sub(1),
            KeyCode::Esc | KeyCode::Char('v') => return Some(Action::Pop),
            _ => {}
        }
        None
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let txt = self.salmo.letra.as_deref().unwrap_or("Letra não disponível.");
        let title = format!("Salmo - {}", self.salmo.referencia);
        let p = Paragraph::new(txt)
            .wrap(Wrap { trim: true })
            .scroll((self.scroll, 0))
            .block(crate::ui::styled_block(&title, theme))
            .style(theme.base_style);
        frame.render_widget(p, chunks[1]);
        let footer = Paragraph::new("[j/k] Rolar | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
