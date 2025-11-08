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
    style::{Color, Style, Stylize},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
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
        let num_days = 120;
        let start_date = today.checked_sub_days(Days::new(num_days - 1)).unwrap();
        
        let mut heatmap_spans = Vec::new();
        let month_names = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
        let mut last_month = 0;

        heatmap_spans.push(Line::from("    "));
        let mut week_pos = 0;
        for i in 0..num_days {
            let date = start_date.checked_add_days(Days::new(i)).unwrap();
            if date.weekday() == chrono::Weekday::Sun {
                if date.month() != last_month {
                    { let padding = " ".repeat(week_pos * 4 - heatmap_spans[0].width()); heatmap_spans[0].spans.push(Span::raw(padding)); }
                    heatmap_spans[0].spans.push(Span::raw(format!("{:<3}", month_names[date.month() as usize])));
                    last_month = date.month();
                }
                week_pos +=1;
            }
        }

        for day_of_week in [0,2,4,6] { // Sun, Tue, Thu, Sat
            let mut line = Line::from(match day_of_week {
                0 => " D ", 2 => " Q ", 4 => " S ", 6 => " S ", _ => "   "
            });
            for i in 0..num_days {
                let date = start_date.checked_add_days(Days::new(i)).unwrap();
                if date.weekday().num_days_from_sunday() == day_of_week {
                    let score = *self.scores.get(&date).unwrap_or(&0);
                    let color = match score {
                        0 => theme.dim_fg,
                        1 => Color::Rgb(0, 100, 0), 2..=3 => Color::Rgb(0, 175, 0), _ => Color::Rgb(0, 255, 0),
                    };
                    line.spans.push(Span::styled("■ ", Style::default().fg(color)));
                }
            }
            heatmap_spans.push(line);
        }
        frame.render_widget(Paragraph::new(heatmap_spans), inner_area);
    }
}
