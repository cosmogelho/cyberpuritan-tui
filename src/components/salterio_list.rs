use super::{
    estudo_menu::EstudoMenuComponent, list_state::StatefulList, piedade_menu::PiedadeMenuComponent,
    salmo_view::SalmoViewComponent, Action, Component, Module,
};
use crate::{app::App, db, models::Salmo, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Rect},
    widgets::{HighlightSpacing, Paragraph, Row, Table},
    Frame,
};

enum InputMode {
    Normal,
    Filtering,
}

pub struct SalterioListComponent {
    list: StatefulList<Salmo>,
    all_items: Vec<Salmo>,
    filter_input: String,
    input_mode: InputMode,
}

impl SalterioListComponent {
    pub fn new() -> Self {
        let all_items = db::listar_salmos().unwrap_or_default();
        let list = StatefulList::with_items(all_items.clone());
        Self {
            list,
            all_items,
            filter_input: String::new(),
            input_mode: InputMode::Normal,
        }
    }

    pub fn selected_salmo(&self) -> Option<&Salmo> {
        self.list.selected_item()
    }

    fn apply_filter(&mut self) {
        let filtered = if self.filter_input.is_empty() {
            self.all_items.clone()
        } else {
            let filter = self.filter_input.to_lowercase();
            self.all_items
                .iter()
                .filter(|s| {
                    s.referencia.to_lowercase().contains(&filter)
                        || s.melodia
                            .clone()
                            .unwrap_or_default()
                            .to_lowercase()
                            .contains(&filter)
                })
                .cloned()
                .collect()
        };
        self.list.set_items(filtered);
    }
}

impl Component for SalterioListComponent {
    fn get_module(&self) -> Module {
        Module::Canto
    }

    fn handle_key_events(&mut self, key: KeyEvent, app: &mut App) -> Option<Action> {
        if let InputMode::Filtering = self.input_mode {
            match key.code {
                KeyCode::Enter => self.input_mode = InputMode::Normal,
                KeyCode::Char(c) => {
                    self.filter_input.push(c);
                    self.apply_filter();
                }
                KeyCode::Backspace => {
                    self.filter_input.pop();
                    self.apply_filter();
                }
                KeyCode::Esc => {
                    self.filter_input.clear();
                    self.apply_filter();
                    self.input_mode = InputMode::Normal;
                }
                _ => {}
            }
            return None;
        }

        match key.code {
            KeyCode::Char('q') => return Some(Action::Quit),
            KeyCode::Char('j') | KeyCode::Down => self.list.next(),
            KeyCode::Char('k') | KeyCode::Up => self.list.previous(),
            KeyCode::Char('/') => self.input_mode = InputMode::Filtering,
            KeyCode::Char('2') => return Some(Action::Navigate(Box::new(PiedadeMenuComponent))),
            KeyCode::Char('3') => return Some(Action::Navigate(Box::new(EstudoMenuComponent))),
            KeyCode::Enter => {
                if let Some(salmo) = self.selected_salmo() {
                    return Some(Action::Navigate(Box::new(SalmoViewComponent::new(
                        salmo.clone(),
                    ))));
                }
            }
            KeyCode::Char('t') => app.play_audio("instrumental", self.selected_salmo()),
            KeyCode::Char('c') => app.play_audio("a_capela", self.selected_salmo()),
            KeyCode::Char('s') => app.stop_audio(),
            _ => {}
        }
        None
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        self.render_table(frame, theme, chunks[1]);
        self.render_footer(frame, theme, chunks[2]);
    }
}

impl SalterioListComponent {
    fn render_table(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let h = Row::new(["Ref.", "Melodia"]).style(theme.header_style);
        let r = self.list.items.iter().map(|s| {
            Row::new([
                s.referencia.clone(),
                s.melodia.clone().unwrap_or_default(),
            ])
        });
        let t = Table::new(r, &[Constraint::Percentage(40), Constraint::Percentage(60)])
            .header(h)
            .block(crate::ui::styled_block("Saltério", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(t, area, &mut self.list.state);
    }

    fn render_footer(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let (title, text) = match self.input_mode {
            InputMode::Normal => (
                "Ajuda",
                "[Enter] Ver | [t] Tocar | [c] Cantar | [s] Parar | [/] Filtrar",
            ),
            InputMode::Filtering => {
                frame.set_cursor(area.x + self.filter_input.len() as u16 + 1, area.y + 1);
                ("Filtrar", self.filter_input.as_str())
            }
        };
        let p = Paragraph::new(text).block(crate::ui::styled_block(title, theme));
        frame.render_widget(p, area);
    }
}
