use super::{
    bcw_list::BcwListComponent, cfw_list::CfwListComponent, cmw_list::CmwListComponent, Action,
    Component, Module,
};
use crate::{app::App, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{widgets::Paragraph, Frame};

pub struct SymbolsMenuComponent;

impl Component for SymbolsMenuComponent {
    fn get_module(&self) -> Module { Module::Estudo }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('1') => Some(Action::Navigate(Box::new(CfwListComponent::new()))),
            KeyCode::Char('2') => Some(Action::Navigate(Box::new(CmwListComponent::new()))),
            KeyCode::Char('3') => Some(Action::Navigate(Box::new(BcwListComponent::new()))),
            KeyCode::Esc | KeyCode::Char('v') => Some(Action::Pop),
            _ => None,
        }
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let menu_text = "\n   [1] Confissão de Fé\n\n   [2] Catecismo Maior\n\n   [3] Breve Catecismo";
        frame.render_widget(
            Paragraph::new(menu_text)
                .block(crate::ui::styled_block("Símbolos de Fé", theme))
                .style(theme.base_style),
            chunks[1],
        );
        let footer = Paragraph::new("[1], [2], [3] Selecionar | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
