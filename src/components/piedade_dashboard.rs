use super::{
    diario_list_unificado::DiarioListUnificadoComponent,
    gerenciar_perguntas::GerenciarPerguntasComponent, nova_entrada_menu::NovaEntradaMenuComponent,
    oracoes_list::OracoesListComponent, Action, Component, Module,
};
use crate::{app::App, db, theme::Theme};
use chrono::{Datelike, Days, Local, NaiveDate};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::Rect,
    style::{Color, Style},
    text::{Line, Span},
    widgets::Paragraph,
    Frame,
};
use std::collections::HashMap;

pub struct PiedadeDashboardComponent {
    scores: HashMap<NaiveDate, u8>,
}

impl PiedadeDashboardComponent {
    pub fn new() -> Self {
        let end_date = Local::now().date_naive();
        let start_date = end_date.checked_sub_days(Days::new(120)).unwrap();
        
        let entradas = db::get_entradas_diario_range(
            &start_date.format("%Y-%m-%d").to_string(),
            &end_date.format("%Y-%m-%d 23:59:59").to_string(),
        ).unwrap_or_default();

        let mut scores = HashMap::new();
        for entrada in entradas {
            if let Ok(date) = NaiveDate::parse_from_str(&entrada.data[0..10], "%Y-%m-%d") {
                let score = scores.entry(date).or_insert(0);
                *score += match entrada.tipo.as_str() {
                    "AUTO_EXAME" => 2,
                    _ => 1,
                };
            }
        }
        Self { scores }
    }
}

impl Component for PiedadeDashboardComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match key.code {
            KeyCode::Char('n') => Some(Action::Navigate(Box::new(NovaEntradaMenuComponent::new()))),
            KeyCode::Char('l') => Some(Action::Navigate(Box::new(DiarioListUnificadoComponent::new()))),
            KeyCode::Char('o') => Some(Action::Navigate(Box::new(OracoesListComponent::new()))),
            KeyCode::Char('g') => Some(Action::Navigate(Box::new(GerenciarPerguntasComponent::new()))),
            KeyCode::Esc | KeyCode::Char('v') => Some(Action::Pop),
            _ => None,
        }
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        self.render_heatmap(frame, theme, chunks[1]);
        let footer =
            Paragraph::new("[n] Nova Entrada | [l] Listar | [o] Orações | [g] Perguntas | [v] Voltar")
                .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}

impl PiedadeDashboardComponent {
    fn render_heatmap(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let block = crate::ui::styled_block("Atividade Espiritual (Últimos 4 Meses)", theme);
        let inner_area = block.inner(area);
        frame.render_widget(block, area);
        
        let today = Local::now().date_naive();
        let days_to_show = 120;
        let start_date = today.checked_sub_days(Days::new(days_to_show -1)).unwrap();
        
        let mut lines = Vec::new();
        
        for day_of_week in 0..7 {
            let mut line = Line::default();
            for i in 0..days_to_show {
                let date = start_date.checked_add_days(Days::new(i)).unwrap();
                if date.weekday().num_days_from_sunday() == day_of_week {
                    if date > today {
                        line.spans.push(Span::raw("  "));
                    } else {
                        let score = *self.scores.get(&date).unwrap_or(&0);
                        let color = match score {
                            0 => theme.dim_fg,
                            1 => Color::Rgb(0, 100, 0),
                            2..=3 => Color::Rgb(0, 175, 0),
                            _ => Color::Rgb(0, 255, 0),
                        };
                        line.spans.push(Span::styled("■ ", Style::default().fg(color)));
                    }
                }
            }
            lines.push(line);
        }
        frame.render_widget(Paragraph::new(lines), inner_area);
    }
}
