use super::{Action, Component, Module};
use crate::{models::OracaoPuritana, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    widgets::{Paragraph, Wrap},
    Frame,
};

pub struct OracaoViewComponent {
    oracao: OracaoPuritana,
    scroll: u16,
}

impl OracaoViewComponent {
    pub fn new(oracao: OracaoPuritana) -> Self {
        Self { oracao, scroll: 0 }
    }
}

impl Component for OracaoViewComponent {
    fn get_module(&self) -> Module {
        Module::Piedade
    }

    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut crate::app::App) -> Option<Action> {
        match key.code {
            KeyCode::Char('j') | KeyCode::Down => self.scroll = self.scroll.saturating_add(1),
            KeyCode::Char('k') | KeyCode::Up => self.scroll = self.scroll.saturating_sub(1),
            KeyCode::PageDown => self.scroll = self.scroll.saturating_add(5),
            KeyCode::PageUp => self.scroll = self.scroll.saturating_sub(5),
            KeyCode::Esc | KeyCode::Char('v') => return Some(Action::Pop),
            _ => {}
        }
        None
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let p = Paragraph::new(self.oracao.texto_completo.as_str())
            .wrap(Wrap { trim: true })
            .scroll((self.scroll, 0))
            .block(crate::ui::styled_block(&self.oracao.titulo, theme))
            .style(theme.base_style);
        frame.render_widget(p, chunks[1]);
        let footer = Paragraph::new("[j/k] Rolar | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
