use super::{list_state::StatefulList, Action, Component, Module};
use crate::{app::App, db, models::PerguntaAutoExame, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::{Style, Stylize},
    widgets::{HighlightSpacing, Paragraph, Row, Table},
    Frame,
};
use std::collections::HashMap;

enum ActivePane {
    Categorias,
    Perguntas,
}

enum InputMode {
    Normal,
    Editing(Option<i32>), // None para criar, Some(id) para editar
}

pub struct GerenciarPerguntasComponent {
    categorias: StatefulList<String>,
    perguntas: StatefulList<PerguntaAutoExame>,
    active_pane: ActivePane,
    input_mode: InputMode,
    input: String,
}

impl GerenciarPerguntasComponent {
    pub fn new() -> Self {
        let categorias_vec = vec![
            "A - Relacionamento com Deus".to_string(),
            "B - Motivações e Coração".to_string(),
            "C - Escritura e Palavra".to_string(),
            "D - Família e Relacionamentos".to_string(),
            "E - Trabalho / Estudos / Serviço".to_string(),
            "F - Comunhão dos Santos".to_string(),
            "G - Lazer, Mídia e Tempo Livre".to_string(),
            "H - Saúde Física e Mental".to_string(),
            "I - Finanças".to_string(),
            "J - Testemunho e Missão".to_string(),
        ];
        let mut component = Self {
            categorias: StatefulList::with_items(categorias_vec),
            perguntas: StatefulList::with_items(vec![]),
            active_pane: ActivePane::Categorias,
            input_mode: InputMode::Normal,
            input: String::new(),
        };
        component.refresh_perguntas();
        component
    }

    fn get_selected_category_code(&self) -> String {
        self.categorias
            .selected_item()
            .map_or("A".to_string(), |s| s.chars().next().unwrap_or('A').to_string())
    }

    fn refresh_perguntas(&mut self) {
        let category_code = self.get_selected_category_code();
        let padrao = db::listar_perguntas_padrao(&category_code).unwrap_or_default();
        let usuario = db::listar_perguntas_usuario(&category_code).unwrap_or_default();

        let mut user_overrides = HashMap::new();
        for p_user in &usuario {
            if !p_user.is_user_defined { // Na verdade, estas são as desativadas
                 user_overrides.insert(p_user.texto.clone(), p_user.is_active);
            }
        }

        let mut combined_list: Vec<PerguntaAutoExame> = padrao
            .into_iter()
            .map(|mut p| {
                if let Some(active_state) = user_overrides.get(&p.texto) {
                    p.is_active = *active_state;
                }
                p
            })
            .collect();

        combined_list.extend(usuario.into_iter().filter(|p| p.is_user_defined));
        self.perguntas.set_items(combined_list);
    }
}

impl Component for GerenciarPerguntasComponent {
    fn get_module(&self) -> Module {
        Module::Piedade
    }

    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        if let InputMode::Editing(maybe_id) = &self.input_mode {
            match key.code {
                KeyCode::Enter => {
                    if !self.input.is_empty() {
                        let category_code = self.get_selected_category_code();
                        if let Some(id) = maybe_id {
                            db::atualizar_pergunta_usuario(*id, &self.input).ok();
                        } else {
                            db::criar_pergunta_usuario(&category_code, &self.input).ok();
                        }
                    }
                    self.input.clear();
                    self.input_mode = InputMode::Normal;
                    self.refresh_perguntas();
                }
                KeyCode::Char(c) => self.input.push(c),
                KeyCode::Backspace => {
                    self.input.pop();
                }
                KeyCode::Esc => {
                    self.input.clear();
                    self.input_mode = InputMode::Normal;
                }
                _ => {}
            }
            return None;
        }

        match key.code {
            KeyCode::Char('v') | KeyCode::Esc => return Some(Action::Pop),
            KeyCode::Char('l') | KeyCode::Tab => self.active_pane = ActivePane::Perguntas,
            KeyCode::Char('h') => self.active_pane = ActivePane::Categorias,
            _ => {}
        }

        match self.active_pane {
            ActivePane::Categorias => match key.code {
                KeyCode::Char('j') | KeyCode::Down => {
                    self.categorias.next();
                    self.refresh_perguntas();
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.categorias.previous();
                    self.refresh_perguntas();
                }
                _ => {}
            },
            ActivePane::Perguntas => match key.code {
                KeyCode::Char('j') | KeyCode::Down => self.perguntas.next(),
                KeyCode::Char('k') | KeyCode::Up => self.perguntas.previous(),
                KeyCode::Char('n') => self.input_mode = InputMode::Editing(None),
                KeyCode::Char('e') => {
                    if let Some(p) = self.perguntas.selected_item() {
                        if p.is_user_defined {
                            self.input = p.texto.clone();
                            self.input_mode = InputMode::Editing(Some(p.id));
                        }
                    }
                }
                KeyCode::Char('d') => {
                    if let Some(p) = self.perguntas.selected_item() {
                        if p.is_user_defined {
                            db::alternar_estado_pergunta_usuario(p.id, !p.is_active).ok();
                        } else {
                            // Se já existe um override, alterna. Se não, cria um para desativar.
                             if let Ok(Some(is_active)) = db::obter_estado_pergunta_padrao(&p.texto) {
                                 db::alternar_estado_pergunta_usuario(p.id, !is_active).ok(); // Bug: p.id aqui é do canon.db
                             } else {
                                 db::desativar_pergunta_padrao(&p.categoria, &p.texto).ok();
                             }
                        }
                        self.refresh_perguntas();
                    }
                }
                _ => {}
            },
        }
        None
    }

    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let main_layout = Layout::new(
            Direction::Horizontal,
            [Constraint::Percentage(30), Constraint::Percentage(70)],
        )
        .split(chunks[1]);

        self.render_categorias(frame, theme, main_layout[0]);
        self.render_perguntas(frame, theme, main_layout[1]);

        let footer_text = match self.input_mode {
            InputMode::Normal => "[n] Nova | [e] Editar | [d] Ativar/Desativar | [h/l] Panes | [v] Voltar",
            InputMode::Editing(_) => "[Enter] Salvar | [Esc] Cancelar",
        };
        let footer = Paragraph::new(footer_text)
            .block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);

        if let InputMode::Editing(_) = self.input_mode {
            let area = crate::ui::centered_rect(60, 20, frame.size());
            let title = if let InputMode::Editing(Some(_)) = self.input_mode { "Editar Pergunta" } else { "Nova Pergunta" };
            let p = Paragraph::new(self.input.as_str())
                .block(crate::ui::styled_block(title, theme));
            frame.render_widget(crate::ui::clear_area(), area);
            frame.render_widget(p, area);
            frame.set_cursor(area.x + self.input.len() as u16 + 1, area.y + 1);
        }
    }
}

impl GerenciarPerguntasComponent {
    fn render_categorias(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let is_active = matches!(self.active_pane, ActivePane::Categorias);
        let block = crate::ui::styled_block("Categorias", theme)
            .border_style(if is_active { theme.header_style } else { theme.base_style });

        let rows = self.categorias.items.iter().map(|c| Row::new(vec![c.clone()]));
        let table = Table::new(rows, &[Constraint::Min(10)])
            .block(block)
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, area, &mut self.categorias.state);
    }

    fn render_perguntas(&mut self, frame: &mut Frame, theme: &Theme, area: Rect) {
        let is_active = matches!(self.active_pane, ActivePane::Perguntas);
        let block = crate::ui::styled_block("Perguntas", theme)
            .border_style(if is_active { theme.header_style } else { theme.base_style });

        let rows = self.perguntas.items.iter().map(|p| {
            let text = if p.is_user_defined { format!("[U] {}", p.texto) } else { p.texto.clone() };
            let style = if p.is_active { theme.base_style } else { theme.base_style.dim() };
            Row::new(vec![text]).style(style)
        });

        let table = Table::new(rows, &[Constraint::Min(20)])
            .block(block)
            .highlight_style(theme.selected_style)
            .highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, area, &mut self.perguntas.state);
    }
}
