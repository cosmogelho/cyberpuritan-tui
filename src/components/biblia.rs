use super::{list_state::StatefulList, Action, Component, Module};
use crate::{
    app::App,
    db,
    models::{Livro, Versiculo},
    theme::Theme,
};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    widgets::{HighlightSpacing, Paragraph, Row, Table, Wrap},
    Frame,
};

enum ActivePane {
    Books,
    Chapters,
}

pub struct BibliaComponent {
    books: StatefulList<Livro>,
    chapters: StatefulList<i32>,
    verses: Vec<Versiculo>,
    active_pane: ActivePane,
    scroll: u16,
}

impl BibliaComponent {
    pub fn new() -> Self {
        let books = db::listar_livros().unwrap_or_default();
        let mut component = Self {
            books: StatefulList::with_items(books),
            chapters: StatefulList::with_items(vec![]),
            verses: vec![],
            active_pane: ActivePane::Books,
            scroll: 0,
        };
        component.on_book_change(); // Carrega capítulos e versos iniciais
        component
    }

    fn on_book_change(&mut self) {
        if let Some(book) = self.books.selected_item() {
            let chapter_count = db::contar_capitulos(book.id).unwrap_or(0);
            let chapters_vec: Vec<i32> = (1..=chapter_count).collect();
            self.chapters.set_items(chapters_vec);
        } else {
            self.chapters.set_items(vec![]);
        }
        self.on_chapter_change();
    }

    fn on_chapter_change(&mut self) {
        if let (Some(book), Some(chapter)) =
            (self.books.selected_item(), self.chapters.selected_item())
        {
            let verses_vec = db::ler_capitulo_biblia(&book.name, *chapter).unwrap_or_default();
            self.verses = verses_vec;
        } else {
            self.verses = vec![];
        }
        self.scroll = 0;
    }
}

impl Component for BibliaComponent {
    fn get_module(&self) -> Module {
        Module::Estudo
    }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('v') | KeyCode::Esc => return Some(Action::Pop),
            KeyCode::Char('l') | KeyCode::Tab => self.active_pane = ActivePane::Chapters,
            KeyCode::Char('h') => self.active_pane = ActivePane::Books,
            _ => {}
        }

        match self.active_pane {
            ActivePane::Books => match key.code {
                KeyCode::Char('j') | KeyCode::Down => {
                    self.books.next();
                    self.on_book_change();
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.books.previous();
                    self.on_book_change();
                }
                _ => {}
            },
            ActivePane::Chapters => match key.code {
                KeyCode::Char('j') | KeyCode::Down => {
                    self.chapters.next();
                    self.on_chapter_change();
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.chapters.previous();
                    self.on_chapter_change();
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
                Constraint::Percentage(15),
                Constraint::Percentage(60),
            ],
        )
        .split(content_area);

        self.render_books(frame, theme, layout[0]);
        self.render_chapters(frame, theme, layout[1]);
        self.render_verses(frame, theme, layout[2]);

        let footer = Paragraph::new("[h/l] Panes | [j/k] Navegar | [PgUp/PgDn] Scroll Texto | [v] Voltar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}

impl BibliaComponent {
    fn render_books(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let is_active = matches!(self.active_pane, ActivePane::Books);
        let block = crate::ui::styled_block("Livros", theme)
            .border_style(if is_active { theme.header_style } else { theme.base_style });
        let rows = self.books.items.iter().map(|b| Row::new([b.name.clone()]));
        let table = Table::new(rows, &[Constraint::Min(10)])
            .block(block)
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, area, &mut self.books.state);
    }

    fn render_chapters(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let is_active = matches!(self.active_pane, ActivePane::Chapters);
        let block = crate::ui::styled_block("Caps", theme)
            .border_style(if is_active { theme.header_style } else { theme.base_style });
        let rows = self
            .chapters.items.iter()
            .map(|c| Row::new([c.to_string()]));
        let table = Table::new(rows, &[Constraint::Min(5)])
            .block(block)
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, area, &mut self.chapters.state);
    }

    fn render_verses(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let title = match (self.books.selected_item(), self.chapters.selected_item()) {
            (Some(b), Some(c)) => format!("{} {}", b.name, c),
            _ => "Texto".to_string(),
        };

        let text = if self.verses.is_empty() {
            "Selecione um capítulo.".to_string()
        } else {
            self.verses
                .iter()
                .map(|v| format!("[{}] {}", v.verse, v.text))
                .collect::<Vec<_>>()
                .join("\n")
        };

        let p = Paragraph::new(text)
            .wrap(Wrap { trim: false })
            .scroll((self.scroll, 0))
            .block(crate::ui::styled_block(&title, theme))
            .style(theme.base_style);
        frame.render_widget(p, area);
    }
}
