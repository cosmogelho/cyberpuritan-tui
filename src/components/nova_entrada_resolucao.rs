use super::{Action, Component, Module};
use crate::{db, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Margin, Rect},
    widgets::Paragraph,
    Frame,
};

enum FocusedField { Texto, Objetivo, Metrica }
enum InputMode { Normal, Editing }

pub struct NovaEntradaResolucaoComponent {
    texto: String,
    objetivo: String,
    metrica: String,
    focused: FocusedField,
    input_mode: InputMode,
}

impl NovaEntradaResolucaoComponent {
    pub fn new() -> Self {
        Self {
            texto: String::new(),
            objetivo: String::new(),
            metrica: String::new(),
            focused: FocusedField::Texto,
            input_mode: InputMode::Normal,
        }
    }
}

impl Component for NovaEntradaResolucaoComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut crate::app::App) -> Option<Action> {
        match self.input_mode {
            InputMode::Normal => match key.code {
                KeyCode::Char('e') => self.input_mode = InputMode::Editing,
                KeyCode::Tab | KeyCode::Down => self.focused = match self.focused {
                    FocusedField::Texto => FocusedField::Objetivo,
                    FocusedField::Objetivo => FocusedField::Metrica,
                    FocusedField::Metrica => FocusedField::Texto,
                },
                KeyCode::Up => self.focused = match self.focused {
                    FocusedField::Texto => FocusedField::Metrica,
                    FocusedField::Objetivo => FocusedField::Texto,
                    FocusedField::Metrica => FocusedField::Objetivo,
                },
                KeyCode::Char('s') => {
                    db::criar_entrada_resolucao(&self.texto, &self.objetivo, &self.metrica).ok();
                    return Some(Action::Pop);
                }
                KeyCode::Esc | KeyCode::Char('v') => return Some(Action::Pop),
                _ => {}
            },
            InputMode::Editing => {
                let current_field = match self.focused {
                    FocusedField::Texto => &mut self.texto,
                    FocusedField::Objetivo => &mut self.objetivo,
                    FocusedField::Metrica => &mut self.metrica,
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
        let block = crate::ui::styled_block("Nova Resolução", theme);
        frame.render_widget(block, chunks[1]);
        let inner_area = chunks[1].inner(&Margin { vertical: 1, horizontal: 1 });
        let fields = [
            ("Resolução", &self.texto, FocusedField::Texto),
            ("Objetivo Concreto", &self.objetivo, FocusedField::Objetivo),
            ("Métrica", &self.metrica, FocusedField::Metrica),
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
