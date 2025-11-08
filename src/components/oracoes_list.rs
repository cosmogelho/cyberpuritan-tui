use super::{
    list_state::StatefulList, oracao_view::OracaoViewComponent, Action, Component, Module,
};
use crate::{app::App, db, models::OracaoPuritana, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::Constraint,
    widgets::{HighlightSpacing, Paragraph, Row, Table},
    Frame,
};

pub struct OracoesListComponent {
    list: StatefulList<OracaoPuritana>,
}

impl OracoesListComponent {
    pub fn new() -> Self {
        let items = db::listar_oracoes().unwrap_or_default();
        Self {
            list: StatefulList::with_items(items),
        }
    }
}

impl Component for OracoesListComponent {
    fn get_module(&self) -> Module {
        Module::Piedade
    }

    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('j') | KeyCode::Down => {
                self.list.next();
                None
            }
            KeyCode::Char('k') | KeyCode::Up => {
                self.list.previous();
                None
            }
            KeyCode::Enter => self
                .list
                .selected_item()
                .map(|o| Action::Navigate(Box::new(OracaoViewComponent::new(o.clone())))),
            KeyCode::Esc | KeyCode::Char('v') => Some(Action::Pop),
            _ => None,
        }
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let rows = self.list.items.iter().map(|o| Row::new(vec![o.titulo.clone()]));
        let table = Table::new(rows, &[Constraint::Min(20)])
            .block(crate::ui::styled_block("Orações Puritanas", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);

        frame.render_stateful_widget(table, chunks[1], &mut self.list.state);

        let footer = Paragraph::new("[Enter] Ler | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
