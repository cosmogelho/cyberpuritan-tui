use crate::components::nova_entrada_autoexame::NovaEntradaAutoExameComponent;
use super::{
    list_state::StatefulList, nova_entrada_evangelismo::NovaEntradaEvangelismoComponent,
    nova_entrada_jejum::NovaEntradaJejumComponent,
    nova_entrada_leitura::NovaEntradaLeituraComponent,
    nova_entrada_resolucao::NovaEntradaResolucaoComponent,
    nova_entrada_sermao::NovaEntradaSermaoComponent, Action, Component, Module,
};
use crate::{app::App, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{layout::Constraint, widgets::{HighlightSpacing, Row, Table}, Frame};

pub struct NovaEntradaMenuComponent {
    list: StatefulList<&'static str>,
}

impl NovaEntradaMenuComponent {
    pub fn new() -> Self {
        let items = vec![
            "Nota de Sermão",
            "Resolução",
            "Jejum",
            "Leitura Bíblica",
            "Evangelismo",
            // "Autoexame" será adicionado na próxima fase
        ];
        Self {
            list: StatefulList::with_items(items),
        }
    }
}

impl Component for NovaEntradaMenuComponent {
    fn get_module(&self) -> Module {
        Module::Piedade
    }

    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('j') | KeyCode::Down => self.list.next(),
            KeyCode::Char('k') | KeyCode::Up => self.list.previous(),
            KeyCode::Enter => {
                let selection = self.list.selected_item().unwrap_or(&"");
                return match *selection {
                    "Nota de Sermão" => Some(Action::Navigate(Box::new(NovaEntradaSermaoComponent::new()))),
                    "Resolução" => Some(Action::Navigate(Box::new(NovaEntradaResolucaoComponent::new()))),
                    "Jejum" => Some(Action::Navigate(Box::new(NovaEntradaJejumComponent::new()))),
                    "Leitura Bíblica" => Some(Action::Navigate(Box::new(NovaEntradaLeituraComponent::new()))),
                    "Evangelismo" => Some(Action::Navigate(Box::new(NovaEntradaEvangelismoComponent::new()))),
                    "Autoexame" => Some(Action::Navigate(Box::new(NovaEntradaAutoExameComponent::new()))),
                    _ => None,
                };
            }
            KeyCode::Esc | KeyCode::Char('v') => return Some(Action::Pop),
            _ => {}
        }
        None
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let rows = self.list.items.iter().map(|i| Row::new(vec![*i]));
        let table = Table::new(rows, &[Constraint::Min(20)])
            .block(crate::ui::styled_block("Selecione o Tipo de Entrada", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, chunks[1], &mut self.list.state);
    }
}
