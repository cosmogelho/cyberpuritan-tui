use super::{biblia::BibliaComponent, symbols_menu::SymbolsMenuComponent, Action, Component, Module};
use crate::{app::App, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{widgets::Paragraph, Frame};

pub struct EstudoMenuComponent;

impl Component for EstudoMenuComponent {
    fn get_module(&self) -> Module { Module::Estudo }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('1') => Some(Action::Navigate(Box::new(SymbolsMenuComponent))),
            KeyCode::Char('2') => Some(Action::Navigate(Box::new(BibliaComponent::new()))),
            KeyCode::Esc | KeyCode::Char('v') => Some(Action::Pop),
            _ => None,
        }
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        frame.render_widget(
            Paragraph::new("\n\n   [1] Símbolos de Fé\n\n   [2] Bíblia")
                .block(crate::ui::styled_block("Estudo", theme))
                .style(theme.base_style),
            chunks[1],
        );
        let footer = Paragraph::new("Use os números para selecionar ou [v] para voltar.")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
