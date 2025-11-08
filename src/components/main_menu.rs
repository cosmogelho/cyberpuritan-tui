use super::{
    estudo_menu::EstudoMenuComponent, piedade_dashboard::PiedadeDashboardComponent,
    salterio_list::SalterioListComponent, Action, Component, Module,
};
use crate::{app::App, theme::Theme, ui::centered_rect};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::Rect,
    text::{Line, Span},
    widgets::{Paragraph, Wrap},
    Frame,
};

pub struct MainMenuComponent;

impl Component for MainMenuComponent {
    fn get_module(&self) -> Module { Module::Canto }

    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('1') => Some(Action::Navigate(Box::new(SalterioListComponent::new()))),
            KeyCode::Char('2') => Some(Action::Navigate(Box::new(PiedadeDashboardComponent::new()))),
            KeyCode::Char('3') => Some(Action::Navigate(Box::new(EstudoMenuComponent))),
            KeyCode::Char('q') | KeyCode::Esc => Some(Action::Quit),
            _ => None,
        }
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let text = vec![
            Line::from(""), Line::from(Span::raw("   [1] Canto")), Line::from(""),
            Line::from(Span::raw("   [2] Piedade")), Line::from(""), Line::from(Span::raw("   [3] Estudo")),
        ];
        let paragraph = Paragraph::new(text).wrap(Wrap { trim: true }).block(crate::ui::styled_block("CyberPuritan", theme));
        let area = centered_rect(60, 25, frame.size());
        frame.render_widget(paragraph, area);
        self.render_footer(frame, theme);
    }
}

impl MainMenuComponent {
    fn render_footer(&self, frame: &mut Frame, theme: &Theme) {
        let footer_area = Rect::new(frame.size().x, frame.size().height - 1, frame.size().width, 1);
        let footer = Paragraph::new("[1,2,3] Selecionar | [q] Sair").style(theme.base_style);
        frame.render_widget(footer, footer_area);
    }
}
