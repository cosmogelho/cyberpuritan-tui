use super::{Action, Component, Module};
use crate::{db, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Margin, Rect},
    widgets::Paragraph,
    Frame,
};

enum FocusedField { Tema, Passagens, Salmo, Aplicacao }
enum InputMode { Normal, Editing }

pub struct NovaEntradaLeituraComponent {
    tema: String,
    passagens: String,
    salmo: String,
    aplicacao: String,
    focused: FocusedField,
    input_mode: InputMode,
}

impl NovaEntradaLeituraComponent {
    pub fn new() -> Self {
        Self {
            tema: String::new(),
            passagens: String::new(),
            salmo: String::new(),
            aplicacao: String::new(),
            focused: FocusedField::Tema,
            input_mode: InputMode::Normal,
        }
    }
}

impl Component for NovaEntradaLeituraComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut crate::app::App) -> Option<Action> {
        match self.input_mode {
            InputMode::Normal => match key.code {
                KeyCode::Char('e') => self.input_mode = InputMode::Editing,
                KeyCode::Tab | KeyCode::Down => self.focused = match self.focused {
                    FocusedField::Tema => FocusedField::Passagens,
                    FocusedField::Passagens => FocusedField::Salmo,
                    FocusedField::Salmo => FocusedField::Aplicacao,
                    FocusedField::Aplicacao => FocusedField::Tema,
                },
                KeyCode::Up => self.focused = match self.focused {
                    FocusedField::Tema => FocusedField::Aplicacao,
                    FocusedField::Passagens => FocusedField::Tema,
                    FocusedField::Salmo => FocusedField::Passagens,
                    FocusedField::Aplicacao => FocusedField::Salmo,
                },
                KeyCode::Char('s') => {
                    db::criar_entrada_leitura(&self.tema, &self.passagens, &self.salmo, &self.aplicacao).ok();
                    return Some(Action::Pop);
                }
                KeyCode::Esc | KeyCode::Char('v') => return Some(Action::Pop),
                _ => {}
            },
            InputMode::Editing => {
                let current_field = match self.focused {
                    FocusedField::Tema => &mut self.tema,
                    FocusedField::Passagens => &mut self.passagens,
                    FocusedField::Salmo => &mut self.salmo,
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
        let block = crate::ui::styled_block("Novo Registro de Leitura Bíblica", theme);
        frame.render_widget(block, chunks[1]);
        let inner_area = chunks[1].inner(&Margin { vertical: 1, horizontal: 1 });
        let fields = [
            ("Tema Semanal", &self.tema, FocusedField::Tema),
            ("Passagens Lidas", &self.passagens, FocusedField::Passagens),
            ("Salmo do Dia", &self.salmo, FocusedField::Salmo),
            ("Aplicação", &self.aplicacao, FocusedField::Aplicacao),
        ];
        for (i, (label, value, field_enum)) in fields.iter().enumerate() {
            let area = Rect::new(inner_area.x, inner_area.y + i as u16 * 2, inner_area.width, 1);
            let mut style = theme.base_style;
            if matches!(&self.focused, field_enum) { style = theme.selected_style; }
            let text = format!("{}: {}", label, value);
            frame.render_widget(Paragraph::new(text).style(style), area);
            if matches!(&self.focused, field_enum) && matches!(self.input_mode, InputMode::Editing) {
                frame.set_cursor(area.x + label.len() as u16 + 2 + value.len() as u16, area.y);
            }
        }
        let footer = Paragraph::new("[e] Editar | [s] Salvar | [Tab] Mudar Campo | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}
