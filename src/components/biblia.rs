use super::{Action, Component, Module};
use crate::{app::{App, MessageType}, db, models::Versiculo, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::Rect,
    widgets::{Paragraph, Wrap},
    Frame,
};

enum InputMode { Normal, Editing }

pub struct BibliaComponent {
    verses: Vec<Versiculo>,
    reference: String,
    scroll: u16,
    input: String,
    input_mode: InputMode,
    status_message: (String, MessageType),
}

impl BibliaComponent {
    pub fn new() -> Self {
        Self {
            verses: Vec::new(),
            reference: "Nenhuma passagem".to_string(),
            scroll: 0,
            input: String::new(),
            input_mode: InputMode::Normal,
            status_message: ("Use [e] para buscar. Ex: ler genesis 1".to_string(), MessageType::Info),
        }
    }
    fn submit_command(&mut self) {
        let command_text = self.input.trim();
        if command_text.is_empty() { return; }
        let parts: Vec<_> = command_text.split_whitespace().collect();
        if parts.get(0) == Some(&"ler") && parts.len() == 3 {
            let book = parts[1];
            if let Ok(chapter) = parts[2].parse::<i32>() {
                match db::ler_capitulo_biblia(book, chapter) {
                    Ok(v) if !v.is_empty() => {
                        self.verses = v;
                        self.reference = format!("{} {}", book, chapter).to_uppercase();
                        self.status_message = (format!("Carregado: {}.", self.reference), MessageType::Success);
                        self.scroll = 0;
                    }
                    Ok(_) => self.status_message = (format!("Nenhum resultado para '{} {}'.", book, chapter), MessageType::Info),
                    Err(_) => self.status_message = (format!("Erro: Livro '{}' não encontrado.", book), MessageType::Error),
                }
            } else { self.status_message = ("Erro: Capítulo inválido.".to_string(), MessageType::Error); }
        } else { self.status_message = ("Comando inválido. Use: ler <livro> <capítulo>".to_string(), MessageType::Error); }
    }
}

impl Component for BibliaComponent {
    fn get_module(&self) -> Module { Module::Estudo }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        match self.input_mode {
            InputMode::Normal => match key.code {
                KeyCode::Char('v') | KeyCode::Esc => return Some(Action::Pop),
                KeyCode::Char('j') | KeyCode::Down => self.scroll = self.scroll.saturating_add(1),
                KeyCode::Char('k') | KeyCode::Up => self.scroll = self.scroll.saturating_sub(1),
                KeyCode::Char('e') => self.input_mode = InputMode::Editing,
                _ => {}
            },
            InputMode::Editing => match key.code {
                KeyCode::Enter => { self.submit_command(); self.input.clear(); self.input_mode = InputMode::Normal; },
                KeyCode::Char(c) => self.input.push(c),
                KeyCode::Backspace => { self.input.pop(); },
                KeyCode::Esc => { self.input.clear(); self.input_mode = InputMode::Normal; },
                _ => {}
            }
        }
        None
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        self.render_view(frame, theme, chunks[1]);
        self.render_footer(frame, theme, chunks[2]);
    }
}

impl BibliaComponent {
    fn render_view(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let text = if self.verses.is_empty() { "\n\n\nUse [e] para buscar uma passagem.".to_string() }
        else { self.verses.iter().map(|v| format!("[{}] {}\n", v.verse, v.text)).collect() };
        let title = format!("Bíblia: {}", self.reference);
        let p = Paragraph::new(text)
            .wrap(Wrap { trim: false })
            .scroll((self.scroll, 0))
            .block(crate::ui::styled_block(&title, theme))
            .style(theme.base_style);
        frame.render_widget(p, area);
    }
    fn render_footer(&self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let (block_title, text, style) = match self.input_mode {
            InputMode::Editing => {
                frame.set_cursor(area.x + self.input.len() as u16 + 1, area.y + 1);
                ("Comando", self.input.as_str(), theme.base_style)
            },
            InputMode::Normal => {
                let (status_text, msg_type) = &self.status_message;
                let color = match msg_type {
                    MessageType::Success => theme.green, MessageType::Error => theme.red, MessageType::Info => theme.fg,
                };
                ("Status", status_text.as_str(), theme.base_style.fg(color))
            }
        };
        let p = Paragraph::new(text).style(style).block(crate::ui::styled_block(block_title, theme));
        frame.render_widget(p, area);
    }
}
