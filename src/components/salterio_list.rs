use super::{
    estudo_menu::EstudoMenuComponent, piedade_menu::PiedadeMenuComponent,
    salmo_view::SalmoViewComponent, Action, Component, Module,
};
use crate::{app::App, db, models::Salmo, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Rect},
    widgets::{HighlightSpacing, Paragraph, Row, Table, TableState},
    Frame,
};

pub struct SalterioListComponent {
    pub state: TableState,
    pub items: Vec<Salmo>,
}

impl SalterioListComponent {
    pub fn new() -> Self {
        let mut state = TableState::default();
        state.select(Some(0));
        let items = db::listar_salmos().unwrap_or_default();
        Self { state, items }
    }
    pub fn next(&mut self) {
        let i = match self.state.selected() { Some(i) => if i >= self.items.len() - 1 { 0 } else { i + 1 }, None => 0 };
        self.state.select(Some(i));
    }
    pub fn previous(&mut self) {
        let i = match self.state.selected() { Some(i) => if i == 0 { self.items.len() - 1 } else { i - 1 }, None => 0 };
        self.state.select(Some(i));
    }
    pub fn selected_salmo(&self) -> Option<&Salmo> {
        self.items.get(self.state.selected().unwrap_or(0))
    }
}

impl Component for SalterioListComponent {
    fn get_module(&self) -> Module { Module::Canto }
    fn handle_key_events(&mut self, key: KeyEvent, app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('q') => return Some(Action::Quit),
            KeyCode::Char('j') | KeyCode::Down => self.next(),
            KeyCode::Char('k') | KeyCode::Up => self.previous(),
            KeyCode::Char('2') => return Some(Action::Navigate(Box::new(PiedadeMenuComponent))),
            KeyCode::Char('3') => return Some(Action::Navigate(Box::new(EstudoMenuComponent))),
            KeyCode::Enter => {
                if let Some(salmo) = self.selected_salmo() {
                    return Some(Action::Navigate(Box::new(SalmoViewComponent::new(salmo.clone()))));
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
        let r = self.items.iter().map(|s| Row::new([s.referencia.clone(), s.melodia.clone().unwrap_or_default()]));
        let t = Table::new(r, &[Constraint::Percentage(40), Constraint::Percentage(60)])
            .header(h)
            .block(crate::ui::styled_block("Saltério", theme))
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(t, area, &mut self.state);
    }
    fn render_footer(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let p = Paragraph::new("[Enter] Ver Letra | [t] Tocar | [c] Cantar | [s] Parar")
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(p, area);
    }
}
