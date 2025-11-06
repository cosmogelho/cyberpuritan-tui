use super::{list_state::StatefulList, Action, Component, Module};
use crate::{
    app::App,
    db,
    models::{CfwCapitulo, CfwSecao},
    theme::Theme,
};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    widgets::{HighlightSpacing, Paragraph, Row, Table, Wrap},
    Frame,
};

enum ActivePane {
    Chapters,
    Sections,
}

pub struct CfwListComponent {
    chapters: StatefulList<CfwCapitulo>,
    sections: StatefulList<CfwSecao>,
    active_pane: ActivePane,
    scroll: u16,
}

impl CfwListComponent {
    pub fn new() -> Self {
        let chapters = db::listar_capitulos_cfw().unwrap_or_default();
        let list = StatefulList::with_items(chapters);

        let initial_sections = list.selected_item().map_or_else(Vec::new, |c| {
            db::ler_secoes_cfw(c.chapter).unwrap_or_default()
        });

        Self {
            chapters: list,
            sections: StatefulList::with_items(initial_sections),
            active_pane: ActivePane::Chapters,
            scroll: 0,
        }
    }

    fn on_chapter_change(&mut self) {
        let new_sections = self.chapters.selected_item().map_or_else(Vec::new, |c| {
            db::ler_secoes_cfw(c.chapter).unwrap_or_default()
        });
        self.sections.set_items(new_sections);
        self.scroll = 0;
    }

    fn on_section_change(&mut self) {
        self.scroll = 0;
    }
}

impl Component for CfwListComponent {
    fn get_module(&self) -> Module {
        Module::Estudo
    }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('v') | KeyCode::Esc => return Some(Action::Pop),
            KeyCode::Char('l') | KeyCode::Tab => {
                self.active_pane = ActivePane::Sections;
                return None;
            }
            KeyCode::Char('h') => {
                self.active_pane = ActivePane::Chapters;
                return None;
            }
            _ => {}
        }

        match self.active_pane {
            ActivePane::Chapters => match key.code {
                KeyCode::Char('j') | KeyCode::Down => {
                    self.chapters.next();
                    self.on_chapter_change();
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.chapters.previous();
                    self.on_chapter_change();
                }
                _ => {}
            },
            ActivePane::Sections => match key.code {
                KeyCode::Char('j') | KeyCode::Down => {
                    self.sections.next();
                    self.on_section_change();
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.sections.previous();
                    self.on_section_change();
                }
                KeyCode::PageDown => self.scroll = self.scroll.saturating_add(5),
                KeyCode::PageUp => self.scroll = self.scroll.saturating_sub(5),
                _ => {}
            },
        }
        None
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let content_area = chunks[1];

        let layout = Layout::new(
            Direction::Horizontal,
            [
                Constraint::Percentage(25),
                Constraint::Percentage(25),
                Constraint::Percentage(50),
            ],
        )
        .split(content_area);

        self.render_chapters_list(frame, theme, layout[0]);
        self.render_sections_list(frame, theme, layout[1]);
        self.render_section_text(frame, theme, layout[2]);

        let footer = Paragraph::new("[h/l] Panes | [j/k] Navegar | [PgUp/PgDn] Scroll Texto | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}

impl CfwListComponent {
    fn render_chapters_list(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let is_active = matches!(self.active_pane, ActivePane::Chapters);
        let block = crate::ui::styled_block("Capítulos", theme)
            .border_style(if is_active { theme.header_style } else { theme.base_style });

        let rows = self
            .chapters.items.iter()
            .map(|c| Row::new([c.chapter.to_string(), c.title.clone()]));
        let table = Table::new(rows, &[Constraint::Length(4), Constraint::Min(10)])
            .header(Row::new(["#", "Título"]).style(theme.header_style))
            .block(block)
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, area, &mut self.chapters.state);
    }

    fn render_sections_list(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let is_active = matches!(self.active_pane, ActivePane::Sections);
        let block = crate::ui::styled_block("Seções", theme)
            .border_style(if is_active { theme.header_style } else { theme.base_style });

        let rows = self
            .sections.items.iter()
            .map(|s| Row::new([s.section.to_string()]));
        let table = Table::new(rows, &[Constraint::Min(5)])
            .header(Row::new(["#"]).style(theme.header_style))
            .block(block)
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, area, &mut self.sections.state);
    }

    fn render_section_text(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        if let Some(s) = self.sections.selected_item() {
            let end_title = s.text.find('.').unwrap_or(s.text.len()).min(50);
            let title = &s.text[..end_title];
            let p = Paragraph::new(s.text.clone())
                .wrap(Wrap { trim: false })
                .scroll((self.scroll, 0))
                .block(crate::ui::styled_block(title, theme))
                .style(theme.base_style);
            frame.render_widget(p, area);
        } else {
            let p = Paragraph::new("Selecione uma seção.")
                .block(crate::ui::styled_block("Texto", theme))
                .style(theme.base_style);
            frame.render_widget(p, area);
        }
    }
}
