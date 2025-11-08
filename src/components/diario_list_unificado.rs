use super::{list_state::StatefulList, Action, Component, Module, diario_view_unificado::DiarioViewUnificadoComponent};
use crate::{app::App, db, models::DiarioEntrada, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{layout::Constraint, widgets::{HighlightSpacing, Paragraph, Row, Table}, Frame};

pub struct DiarioListUnificadoComponent {
    list: StatefulList<DiarioEntrada>,
}

impl DiarioListUnificadoComponent {
    pub fn new() -> Self {
        let items = db::get_entradas_diario_range("1900-01-01", "9999-12-31").unwrap_or_default();
        Self { list: StatefulList::with_items(items) }
    }
}

impl Component for DiarioListUnificadoComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('j') | KeyCode::Down => { self.list.next(); None },
            KeyCode::Char('k') | KeyCode::Up => { self.list.previous(); None },
            KeyCode::Enter => self.list.selected_item().map(|item| {
                Action::Navigate(Box::new(DiarioViewUnificadoComponent::new(item.id, item.tipo.clone())))
            }),
            KeyCode::Esc | KeyCode::Char('v') => Some(Action::Pop),
            _ => None,
        }
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let header = Row::new(vec!["Data", "Tipo", "Resumo"]).style(theme.header_style);
        let rows = self.list.items.iter().map(|item| {
            Row::new(vec![item.data.clone(), item.tipo.clone(), item.resumo.clone()])
        });

        let table = Table::new(rows, &[Constraint::Length(20), Constraint::Length(15), Constraint::Min(40)])
            .header(header)
            .block(crate::ui::styled_block("Histórico do Diário", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        
        frame.render_stateful_widget(table, chunks[1], &mut self.list.state);
        let footer = Paragraph::new("[Enter] Ver Detalhes | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
