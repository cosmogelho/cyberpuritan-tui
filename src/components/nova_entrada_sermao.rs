use super::{Action, Component, Module};
use crate::{db, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{layout::{Margin, Rect}, widgets::Paragraph, Frame};

#[derive(PartialEq)]
enum FocusedField { Pregador, Titulo, Passagens, Pontos, Aplicacao }
enum InputMode { Normal, Editing }

pub struct NovaEntradaSermaoComponent {
    pregador: String,
    titulo: String,
    passagens: String,
    pontos: String,
    aplicacao: String,
    focused: FocusedField,
    input_mode: InputMode,
}

impl NovaEntradaSermaoComponent {
    pub fn new() -> Self {
        Self {
            pregador: String::new(),
            titulo: String::new(),
            passagens: String::new(),
            pontos: String::new(),
            aplicacao: String::new(),
            focused: FocusedField::Pregador,
            input_mode: InputMode::Normal,
        }
    }
}

impl Component for NovaEntradaSermaoComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut crate::app::App) -> Option<Action> {
        match self.input_mode {
            InputMode::Normal => match key.code {
                KeyCode::Char('e') => self.input_mode = InputMode::Editing,
                KeyCode::Tab | KeyCode::Down => self.focused = match self.focused {
                    FocusedField::Pregador => FocusedField::Titulo,
                    FocusedField::Titulo => FocusedField::Passagens,
                    FocusedField::Passagens => FocusedField::Pontos,
                    FocusedField::Pontos => FocusedField::Aplicacao,
                    FocusedField::Aplicacao => FocusedField::Pregador,
                },
                KeyCode::Up => self.focused = match self.focused {
                    FocusedField::Pregador => FocusedField::Aplicacao,
                    FocusedField::Titulo => FocusedField::Pregador,
                    FocusedField::Passagens => FocusedField::Titulo,
                    FocusedField::Pontos => FocusedField::Passagens,
                    FocusedField::Aplicacao => FocusedField::Pontos,
                },
                KeyCode::Char('s') => {
                    db::criar_entrada_sermao(&self.pregador, &self.titulo, &self.passagens, &self.pontos, &self.aplicacao).ok();
                    return Some(Action::Pop);
                }
                KeyCode::Esc | KeyCode::Char('v') => return Some(Action::Pop),
                _ => {}
            },
            InputMode::Editing => {
                let current_field = match self.focused {
                    FocusedField::Pregador => &mut self.pregador,
                    FocusedField::Titulo => &mut self.titulo,
                    FocusedField::Passagens => &mut self.passagens,
                    FocusedField::Pontos => &mut self.pontos,
                    FocusedField::Aplicacao => &mut self.aplicacao,
                };
                match key.code {
                    KeyCode::Enter => self.input_mode = InputMode::Normal,
                    KeyCode::Char(c) => current_field.push(c),
                    KeyCode::Backspace => { current_field.pop(); },
                    KeyCode::Esc => self.input_mode = InputMode::Normal,
                    _ => {}
                }
            }
        }
        None
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let block = crate::ui::styled_block("Nova Nota de Sermão", theme);
        frame.render_widget(block, chunks[1]);
        let inner_area = chunks[1].inner(&Margin { vertical: 1, horizontal: 1 });
        let fields = [
            ("Pregador", &self.pregador, FocusedField::Pregador),
            ("Título", &self.titulo, FocusedField::Titulo),
            ("Passagens", &self.passagens, FocusedField::Passagens),
            ("Pontos-Chave", &self.pontos, FocusedField::Pontos),
            ("Aplicação", &self.aplicacao, FocusedField::Aplicacao),
        ];
        for (i, (label, value, field_enum)) in fields.iter().enumerate() {
            let area = Rect::new(inner_area.x, inner_area.y + i as u16 * 2, inner_area.width, 1);
            let mut style = theme.base_style;
            if self.focused == *field_enum { style = theme.selected_style; }
            let text = format!("{}: {}", label, value);
            frame.render_widget(Paragraph::new(text).style(style), area);
            if self.focused == *field_enum && matches!(self.input_mode, InputMode::Editing) {
                frame.set_cursor(area.x + label.len() as u16 + 2 + value.len() as u16, area.y);
            }
        }
        let footer = Paragraph::new("[e] Editar | [s] Salvar | [Tab] Mudar Campo | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
