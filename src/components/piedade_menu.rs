use super::{
    acoes_list::AcoesListComponent, diario_list::DiarioListComponent,
    resolucoes_list::ResolucoesListComponent, Action, Component, Module,
};
use crate::{app::App, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{widgets::Paragraph, Frame};

pub struct PiedadeMenuComponent;

impl Component for PiedadeMenuComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('1') => Some(Action::Navigate(Box::new(DiarioListComponent::new()))),
            KeyCode::Char('2') => Some(Action::Navigate(Box::new(AcoesListComponent::new()))),
            KeyCode::Char('3') => Some(Action::Navigate(Box::new(ResolucoesListComponent::new()))),
            KeyCode::Esc | KeyCode::Char('v') => Some(Action::Pop),
            _ => None,
        }
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        frame.render_widget(
            Paragraph::new("\n [1] Diário\n\n [2] Ações de Santificação\n\n [3] Resoluções")
                .block(crate::ui::styled_block("Piedade", theme))
                .style(theme.base_style),
            chunks[1],
        );
        let footer = Paragraph::new("Use os números para selecionar ou [v] para voltar.")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
