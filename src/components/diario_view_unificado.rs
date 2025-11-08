use super::{Action, Component, Module};
use crate::{db, models::{AutoExameDetail, SermaoDetail}, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::style::Stylize;
use ratatui::{text::{Line, Span}, widgets::{Paragraph, Wrap}, Frame};

pub enum EntryDetail {
    Sermao(SermaoDetail),
    AutoExame(AutoExameDetail),
    NotImplemented(String),
    Loading,
}

pub struct DiarioViewUnificadoComponent {
    detail: EntryDetail,
    scroll: u16,
}

impl DiarioViewUnificadoComponent {
    pub fn new(id: i32, tipo: String) -> Self {
        let detail = match tipo.as_str() {
            "SERMAO" => db::get_sermao_details(id)
                .ok().flatten()
                .map(EntryDetail::Sermao)
                .unwrap_or_else(|| EntryDetail::NotImplemented("Erro ao carregar sermão".to_string())),
            "AUTO_EXAME" => db::get_autoexame_details(id)
                .ok().flatten()
                .map(EntryDetail::AutoExame)
                .unwrap_or_else(|| EntryDetail::NotImplemented("Erro ao carregar autoexame".to_string())),
            _ => EntryDetail::NotImplemented(format!("Visualização para '{}' não implementada", tipo)),
        };
        Self { detail, scroll: 0 }
    }
}

impl Component for DiarioViewUnificadoComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut crate::app::App) -> Option<Action> {
        match key.code {
            KeyCode::Char('j') | KeyCode::Down => { self.scroll = self.scroll.saturating_add(1); None },
            KeyCode::Char('k') | KeyCode::Up => { self.scroll = self.scroll.saturating_sub(1); None },
            KeyCode::Esc | KeyCode::Char('v') => Some(Action::Pop),
            _ => None,
        }
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let (title, text): (&str, Vec<Line>) = match &self.detail {
            EntryDetail::Loading => ("Carregando...", vec![Line::from("Aguarde...")]),
            EntryDetail::NotImplemented(msg) => ("Não Implementado", vec![Line::from(msg.clone())]),
            EntryDetail::Sermao(s) => ("Detalhes do Sermão", vec![
                Line::from(vec![Span::styled("Pregador: ", theme.header_style), Span::raw(&s.pregador)]),
                Line::from(vec![Span::styled("Título: ", theme.header_style), Span::raw(&s.titulo)]),
                Line::from(vec![Span::styled("Passagens: ", theme.header_style), Span::raw(&s.passagens)]),
                Line::from(""),
                Line::from(Span::styled("Pontos-Chave:", theme.header_style)),
                Line::from(Span::raw(&s.pontos_chave)),
                Line::from(""),
                Line::from(Span::styled("Aplicação Pessoal:", theme.header_style)),
                Line::from(Span::raw(&s.aplicacao_pessoal)),
            ]),
            EntryDetail::AutoExame(ae) => {
                let mut lines = Vec::new();
                lines.push(Line::from(Span::styled("Respostas do Autoexame:", theme.header_style)));
                for r in &ae.respostas {
                    lines.push(Line::from(vec![Span::raw("P: "), Span::raw(&r.pergunta_texto)]));
                    lines.push(Line::from(vec![Span::raw("R: "), Span::styled(r.avaliacao.clone(), theme.selected_style)]));
                    lines.push(Line::from(""));
                }
                lines.push(Line::from(Span::styled("Passo Prático:", theme.header_style)));
                lines.push(Line::from(ae.passo_pratico.as_str()));
                ("Detalhes do Autoexame", lines)
            }
        };

        let p = Paragraph::new(text).wrap(Wrap { trim: true }).scroll((self.scroll, 0))
            .block(crate::ui::styled_block(title, theme));
        frame.render_widget(p, chunks[1]);
        
        let footer = Paragraph::new("[j/k] Rolar | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
