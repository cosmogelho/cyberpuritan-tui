use super::{list_state::StatefulList, Action, Component, Module, utils};
use crate::{app::App, db, models::PerguntaAutoExame, theme::Theme};
use crossterm::event::{KeyCode, KeyEvent};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::Stylize,
    widgets::{HighlightSpacing, Paragraph, Row, Table},
    Frame,
};
use std::collections::{HashMap, HashSet};

enum Step { Selecao, Respostas, PassoPratico }
enum ActivePane { Categorias, Perguntas }
enum InputMode { Normal, Editing }

struct Resposta {
    pergunta_id: i32,
    texto_pergunta: String,
    avaliacao: String,
}

pub struct NovaEntradaAutoExameComponent {
    step: Step,
    categorias: StatefulList<String>,
    perguntas: StatefulList<PerguntaAutoExame>,
    active_pane: ActivePane,
    selected_ids: HashSet<i32>,
    respostas: Vec<Resposta>,
    current_question_index: usize,
    avaliacao_list: StatefulList<&'static str>,
    passo_pratico: String,
    input_mode: InputMode,
}

impl NovaEntradaAutoExameComponent {
    pub fn new() -> Self {
        let categorias_vec = utils::get_categorias_autoexame();
        let mut component = Self {
            step: Step::Selecao,
            categorias: StatefulList::with_items(categorias_vec),
            perguntas: StatefulList::with_items(vec![]),
            active_pane: ActivePane::Categorias,
            selected_ids: HashSet::new(),
            respostas: Vec::new(),
            current_question_index: 0,
            avaliacao_list: StatefulList::with_items(vec!["Boa", "Precisa melhorar", "Problema grave"]),
            passo_pratico: String::new(),
            input_mode: InputMode::Normal,
        };
        component.refresh_perguntas();
        component
    }

    fn get_selected_category_code(&self) -> String {
        self.categorias.selected_item().map_or("A".to_string(), |s| s.chars().next().unwrap_or('A').to_string())
    }

    fn refresh_perguntas(&mut self) {
        let category_code = self.get_selected_category_code();
        let padrao = db::listar_perguntas_padrao(&category_code).unwrap_or_default();
        let usuario = db::listar_perguntas_usuario(&category_code).unwrap_or_default();
        let mut user_overrides = HashMap::new();
        for p_user in &usuario {
            if !p_user.is_user_defined { user_overrides.insert(p_user.texto.clone(), p_user.is_active); }
        }
        let mut combined_list: Vec<PerguntaAutoExame> = padrao.into_iter()
            .filter(|p| *user_overrides.get(&p.texto).unwrap_or(&true))
            .collect();
        combined_list.extend(usuario.into_iter().filter(|p| p.is_user_defined && p.is_active));
        self.perguntas.set_items(combined_list);
    }

    fn handle_selecao(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Tab | KeyCode::Char('h') | KeyCode::Char('l') => self.active_pane = match self.active_pane {
                ActivePane::Categorias => ActivePane::Perguntas,
                ActivePane::Perguntas => ActivePane::Categorias,
            },
            KeyCode::Enter => {
                let selected_perguntas: Vec<_> = self.perguntas.items.iter().filter(|p| self.selected_ids.contains(&p.id)).cloned().collect();
                if !selected_perguntas.is_empty() {
                    self.respostas = selected_perguntas.into_iter().map(|p| Resposta {
                        pergunta_id: p.id,
                        texto_pergunta: p.texto.clone(),
                        avaliacao: String::new(),
                    }).collect();
                    self.step = Step::Respostas;
                }
            }
            _ => match self.active_pane {
                ActivePane::Categorias => match key.code {
                    KeyCode::Down | KeyCode::Char('j') => { self.categorias.next(); self.refresh_perguntas(); },
                    KeyCode::Up | KeyCode::Char('k') => { self.categorias.previous(); self.refresh_perguntas(); },
                    _ => {}
                },
                ActivePane::Perguntas => match key.code {
                    KeyCode::Down | KeyCode::Char('j') => self.perguntas.next(),
                    KeyCode::Up | KeyCode::Char('k') => self.perguntas.previous(),
                    KeyCode::Char(' ') => if let Some(p) = self.perguntas.selected_item() {
                        if !self.selected_ids.remove(&p.id) { self.selected_ids.insert(p.id); }
                    },
                    _ => {}
                }
            }
        }
    }

    fn handle_respostas(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Down | KeyCode::Char('j') => self.avaliacao_list.next(),
            KeyCode::Up | KeyCode::Char('k') => self.avaliacao_list.previous(),
            KeyCode::Enter => {
                if let Some(avaliacao) = self.avaliacao_list.selected_item() {
                    self.respostas[self.current_question_index].avaliacao = (*avaliacao).to_string();
                    if self.current_question_index >= self.respostas.len() - 1 {
                        self.step = Step::PassoPratico;
                        self.input_mode = InputMode::Editing;
                    } else {
                        self.current_question_index += 1;
                        self.avaliacao_list.state.select(Some(0));
                    }
                }
            }
            _ => {}
        }
    }

    fn handle_passo_pratico(&mut self, key: KeyEvent) -> Option<Action> {
        match self.input_mode {
            InputMode::Editing => match key.code {
                KeyCode::Enter => {
                    let respostas_json_parts: Vec<String> = self.respostas.iter()
                        .map(|r| format!("{{\"id\":{},\"eval\":\"{}\"}}", r.pergunta_id, r.avaliacao))
                        .collect();
                    let respostas_json = format!("[{}]", respostas_json_parts.join(","));
                    db::criar_entrada_auto_exame(&respostas_json, &self.passo_pratico).ok();
                    return Some(Action::Pop);
                }
                KeyCode::Char(c) => self.passo_pratico.push(c),
                KeyCode::Backspace => { self.passo_pratico.pop(); },
                KeyCode::Esc => self.input_mode = InputMode::Normal,
                _ => {}
            },
            InputMode::Normal => if key.code == KeyCode::Char('e') { self.input_mode = InputMode::Editing },
        }
        None
    }

    fn render_selecao(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let layout = Layout::new(Direction::Horizontal, [Constraint::Percentage(30), Constraint::Percentage(70)]).split(chunks[1]);
        let cat_border = if matches!(self.active_pane, ActivePane::Categorias) { theme.header_style } else { theme.base_style };
        let per_border = if matches!(self.active_pane, ActivePane::Perguntas) { theme.header_style } else { theme.base_style };
        let cat_rows = self.categorias.items.iter().map(|c| Row::new(vec![c.clone()]));
        let cat_table = Table::new(cat_rows, &[Constraint::Min(10)])
            .block(crate::ui::styled_block("Categorias", theme).border_style(cat_border))
            .highlight_style(theme.selected_style).highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(cat_table, layout[0], &mut self.categorias.state);
        let per_rows = self.perguntas.items.iter().map(|p| {
            let prefix = if self.selected_ids.contains(&p.id) { "[X]" } else { "[ ]" };
            Row::new(vec![format!("{} {}", prefix, p.texto)])
        });
        let title = format!("Perguntas ({}/{})", self.selected_ids.len(), self.perguntas.items.len());
        let per_table = Table::new(per_rows, &[Constraint::Min(20)])
            .block(crate::ui::styled_block(&title, theme).border_style(per_border))
            .highlight_style(theme.selected_style).highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(per_table, layout[1], &mut self.perguntas.state);
        let footer = Paragraph::new("[Espaço] Selecionar | [Enter] Continuar | [h/l/Tab] Panes | [v] Voltar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }

    fn render_respostas(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let title = format!("Respondendo {} de {}", self.current_question_index + 1, self.respostas.len());
        let block = crate::ui::styled_block(&title, theme);
        let inner_chunks = Layout::new(Direction::Vertical, [Constraint::Percentage(50), Constraint::Percentage(50)]).margin(1).split(block.inner(chunks[1]));
        frame.render_widget(block, chunks[1]);
        let pergunta = &self.respostas[self.current_question_index].texto_pergunta;
        let pergunta_para = Paragraph::new(pergunta.clone()).wrap(ratatui::widgets::Wrap { trim: true });
        frame.render_widget(pergunta_para, inner_chunks[0]);
        let rows = self.avaliacao_list.items.iter().map(|txt| Row::new(vec![*txt]));
        let table = Table::new(rows, &[Constraint::Min(20)]).highlight_style(theme.selected_style).highlight_spacing(HighlightSpacing::Always);
        frame.render_stateful_widget(table, inner_chunks[1], &mut self.avaliacao_list.state);
        let footer = Paragraph::new("[j/k] Selecionar | [Enter] Confirmar").block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
    
    fn render_passo_pratico(&mut self, frame: &mut Frame, theme: &Theme) {
        let chunks = crate::ui::get_layout_chunks(frame.size());
        let p = Paragraph::new(self.passo_pratico.as_str()).block(crate::ui::styled_block("Passo Prático Decorrente do Exame", theme));
        frame.render_widget(p, chunks[1]);
        if matches!(self.input_mode, InputMode::Editing) {
            frame.set_cursor(chunks[1].x + self.passo_pratico.len() as u16 + 1, chunks[1].y + 1);
        }
        let footer_text = if matches!(self.input_mode, InputMode::Normal) { "[e] Editar | [Enter] Salvar" } else { "[Enter] Salvar | [Esc] Cancelar Edição" };
        let footer = Paragraph::new(footer_text).block(crate::ui::styled_block("Ajuda", theme));
        frame.render_widget(footer, chunks[2]);
    }
}

impl Component for NovaEntradaAutoExameComponent {
    fn get_module(&self) -> Module { Module::Piedade }
    fn handle_key_events(&mut self, key: KeyEvent, _app: &mut App) -> Option<Action> {
        if key.code == KeyCode::Esc { return Some(Action::Pop) }
        match self.step {
            Step::Selecao => { self.handle_selecao(key); None },
            Step::Respostas => { self.handle_respostas(key); None },
            Step::PassoPratico => self.handle_passo_pratico(key),
        }
    }
    fn render(&mut self, frame: &mut Frame, theme: &Theme) {
        match self.step {
            Step::Selecao => self.render_selecao(frame, theme),
            Step::Respostas => self.render_respostas(frame, theme),
            Step::PassoPratico => self.render_passo_pratico(frame, theme),
        }
    }
}
