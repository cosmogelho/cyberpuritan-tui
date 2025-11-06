use super::{list_state::StatefulList, Action, Component, Module};
use crate::{app::App, db, models::{CfwCapitulo, CfwSecao}, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    widgets::{HighlightSpacing, Paragraph, Row, Table, Wrap},
    Frame,
};

pub struct CfwListComponent {
    chapters: StatefulList<CfwCapitulo>,
    sections: Vec<CfwSecao>,
}

impl CfwListComponent {
    pub fn new() -> Self {
        let chapters = db::listar_capitulos_cfw().unwrap_or_default();
        let mut list = StatefulList::with_items(chapters);
        let sections = list
            .selected_item()
            .map_or_else(Vec::new, |c| {
                db::ler_secoes_cfw(c.chapter).unwrap_or_default()
            });

        Self { chapters: list, sections }
    }

    fn on_selection_change(&mut self) {
        self.sections = self
            .chapters
            .selected_item()
            .map_or_else(Vec::new, |c| {
                db::ler_secoes_cfw(c.chapter).unwrap_or_default()
            });
    }
}

impl Component for CfwListComponent {
    fn get_module(&self) -> Module {
        Module::Estudo
    }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('v') | KeyCode::Esc => Some(Action::Pop),
            KeyCode::Char('j') | KeyCode::Down => {
                self.chapters.next();
                self.on_selection_change();
                None
            }
            KeyCode::Char('k') | KeyCode::Up => {
                self.chapters.previous();
                self.on_selection_change();
                None
            }
            _ => None,
        }
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let content_area = chunks[1];

        let layout = Layout::new(
            Direction::Horizontal,
            [Constraint::Percentage(40), Constraint::Percentage(60)],
        )
        .split(content_area);

        self.render_chapters_list(frame, theme, layout[0]);
        self.render_sections_view(frame, theme, layout[1]);

        let footer = Paragraph::new("[j/k] Navegar | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}

impl CfwListComponent {
    fn render_chapters_list(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let h = Row::new(["Cap.", "Título"]).style(theme.header_style);
        let r = self
            .chapters
            .items
            .iter()
            .map(|c| Row::new([c.chapter.to_string(), c.title.clone()]));
        let t = Table::new(r, &[Constraint::Length(5), Constraint::Min(20)])
            .header(h)
            .block(crate::ui::styled_block("Confissão de Fé", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(t, area, &mut self.chapters.state);
    }

    fn render_sections_view(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let text: String = self
            .sections
            .iter()
            .map(|s| format!("{}. {}\n\n", s.section, s.text))
            .collect();

        let title = self.chapters.selected_item().map_or_else(
            || "Seções".to_string(),
            |c| format!("Capítulo {}: {}", c.chapter, c.title),
        );
        let p = Paragraph::new(text)
            .wrap(Wrap { trim: false })
            .block(crate::ui::styled_block(&title, theme))
            .style(theme.base_style);
        frame.render_widget(p, area);
    }
}
