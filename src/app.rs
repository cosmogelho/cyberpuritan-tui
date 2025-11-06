use crate::{db, models::*, theme::Theme};
use ratatui::widgets::TableState;
use std::path::Path;
use std::process::{Child, Command};

#[derive(Clone, Copy, Debug)]
pub enum MessageType {
    Info,
    Success,
    Error,
}
pub enum InputMode {
    Normal,
    Editing,
}
pub enum CurrentScreen {
    SalterioList,
    SalmoView,
    PiedadeMenu,
    EstudoMenu,
    DiarioList,
    DiarioNew,
    DiarioView,
    AcoesList,
    ResolucoesList,
    SymbolsMenu,
    CfwList,
    CfwSections,
    CmwList,
    CmwAnswer,
    BcwList,
    BcwAnswer,
    Biblia,
}

pub struct App {
    pub should_quit: bool,
    pub current_screen: CurrentScreen,
    pub input: String,
    pub input_mode: InputMode,
    pub status_message: (String, MessageType),
    pub theme: Theme,
    pub salmos: Vec<Salmo>,
    pub salmos_state: TableState,
    pub salmo_scroll: u16,
    pub acoes: Vec<Acao>,
    pub acoes_list_state: TableState,
    pub resolucoes: Vec<Resolucao>,
    pub resolucoes_list_state: TableState,
    pub cfw_capitulos: Vec<CfwCapitulo>,
    pub cfw_list_state: TableState,
    pub cfw_secoes: Vec<CfwSecao>,
    pub cfw_capitulo_titulo: String,
    pub cfw_scroll: u16,
    pub cmw_perguntas: Vec<CatecismoPergunta>,
    pub cmw_list_state: TableState,
    pub cmw_scroll: u16,
    pub bcw_perguntas: Vec<CatecismoPergunta>,
    pub bcw_list_state: TableState,
    pub bcw_scroll: u16,
    pub biblia_versiculos: Vec<Versiculo>,
    pub biblia_referencia: String,
    pub biblia_scroll: u16,
    pub diario_entradas: Vec<EntradaDiario>,
    pub diario_list_state: TableState,
    pub diario_scroll: u16,
    pub audio_process: Option<Child>,
}

impl App {
    pub fn new(
        s: Vec<Salmo>,
        cfw: Vec<CfwCapitulo>,
        cmw: Vec<CatecismoPergunta>,
        bcw: Vec<CatecismoPergunta>,
        diario: Vec<EntradaDiario>,
        acoes: Vec<Acao>,
        resolucoes: Vec<Resolucao>,
    ) -> Self {
        Self {
            should_quit: false,
            current_screen: CurrentScreen::SalterioList,
            input: String::new(),
            input_mode: InputMode::Normal,
            status_message: ("Bem-vindo!".to_string(), MessageType::Info),
            theme: Theme::new(),
            salmos: s,
            salmos_state: TableState::default().with_selected(0),
            salmo_scroll: 0,
            acoes,
            acoes_list_state: TableState::default().with_selected(0),
            resolucoes,
            resolucoes_list_state: TableState::default().with_selected(0),
            cfw_capitulos: cfw,
            cfw_list_state: TableState::default().with_selected(0),
            cfw_secoes: Vec::new(),
            cfw_capitulo_titulo: String::new(),
            cfw_scroll: 0,
            cmw_perguntas: cmw,
            cmw_list_state: TableState::default().with_selected(0),
            cmw_scroll: 0,
            bcw_perguntas: bcw,
            bcw_list_state: TableState::default().with_selected(0),
            bcw_scroll: 0,
            biblia_versiculos: Vec::new(),
            biblia_referencia: "Nenhuma passagem".to_string(),
            biblia_scroll: 0,
            diario_entradas: diario,
            diario_list_state: TableState::default().with_selected(0),
            diario_scroll: 0,
            audio_process: None,
        }
    }
    pub fn refresh_diario(&mut self) {
        if let Ok(e) = db::listar_entradas_diario() {
            self.diario_entradas = e;
            self.diario_list_state.select(Some(0));
        }
    }
    pub fn refresh_acoes(&mut self) {
        if let Ok(a) = db::listar_acoes() {
            self.acoes = a;
            self.acoes_list_state.select(Some(0));
        }
    }
    pub fn refresh_resolucoes(&mut self) {
        if let Ok(r) = db::listar_resolucoes() {
            self.resolucoes = r;
            self.resolucoes_list_state.select(Some(0));
        }
    }
    pub fn enter_salmo_view(&mut self) {
        self.salmo_scroll = 0;
        self.current_screen = CurrentScreen::SalmoView;
    }
    pub fn enter_diario_view(&mut self) {
        self.diario_scroll = 0;
        self.current_screen = CurrentScreen::DiarioView;
    }
    pub fn selected_diario_entry(&self) -> Option<&EntradaDiario> {
        self.diario_entradas
            .get(self.diario_list_state.selected().unwrap_or(0))
    }
    pub fn enter_cfw_chapter_view(&mut self) {
        if let Some(i) = self.cfw_list_state.selected() {
            if let Some(c) = self.cfw_capitulos.get(i) {
                if let Ok(s) = db::ler_secoes_cfw(c.chapter) {
                    self.cfw_secoes = s;
                    self.cfw_capitulo_titulo = c.title.clone();
                    self.cfw_scroll = 0;
                    self.current_screen = CurrentScreen::CfwSections;
                }
            }
        }
    }
    pub fn enter_cmw_answer_view(&mut self) {
        self.cmw_scroll = 0;
        self.current_screen = CurrentScreen::CmwAnswer;
    }
    pub fn enter_bcw_answer_view(&mut self) {
        self.bcw_scroll = 0;
        self.current_screen = CurrentScreen::BcwAnswer;
    }
    pub fn selected_salmo(&self) -> Option<&Salmo> {
        self.salmos.get(self.salmos_state.selected().unwrap_or(0))
    }
    pub fn selected_cmw_question(&self) -> Option<&CatecismoPergunta> {
        self.cmw_perguntas
            .get(self.cmw_list_state.selected().unwrap_or(0))
    }
    pub fn selected_bcw_question(&self) -> Option<&CatecismoPergunta> {
        self.bcw_perguntas
            .get(self.bcw_list_state.selected().unwrap_or(0))
    }
    pub fn stop_audio(&mut self) {
        if let Some(mut child) = self.audio_process.take() {
            if child.kill().is_ok() {
                let _ = child.wait();
                self.status_message = ("Áudio parado.".to_string(), MessageType::Info);
            }
        }
    }
    pub fn play_audio(&mut self, audio_type: &str) {
        self.stop_audio();
        let filename = self.selected_salmo().and_then(|s| {
            match audio_type {
                "instrumental" => s.instrumental.as_ref(),
                "a_capela" => s.a_capela.as_ref(),
                _ => None,
            }
            .cloned()
        });
        if let Some(name) = filename {
            let path = Path::new("./data/saltério").join(&name);
            if path.exists() {
                if let Ok(child) = Command::new("mpv")
                    .args(["--no-video", "--really-quiet", path.to_str().unwrap()])
                    .spawn()
                {
                    self.audio_process = Some(child);
                    self.status_message = (format!("Tocando: {}", name), MessageType::Info);
                } else {
                    self.status_message = (
                        "Erro: 'mpv' não encontrado.".to_string(),
                        MessageType::Error,
                    );
                }
            } else {
                self.status_message = (
                    "Erro: Arquivo não encontrado.".to_string(),
                    MessageType::Error,
                );
            }
        } else {
            self.status_message = (
                format!("Áudio '{}' indisponível.", audio_type),
                MessageType::Info,
            );
        }
    }
    pub fn check_audio_process(&mut self) {
        if let Some(child) = self.audio_process.as_mut() {
            if let Ok(Some(_)) = child.try_wait() {
                self.audio_process.take();
                self.status_message = ("Reprodução terminada.".to_string(), MessageType::Info);
            }
        }
    }
    pub fn submit_command(&mut self) {
        let command_text = self.input.trim();
        if command_text.is_empty() {
            self.input_mode = InputMode::Normal;
            self.input.clear();
            return;
        }
        match self.current_screen {
            CurrentScreen::Biblia => {
                let p: Vec<_> = command_text.split_whitespace().collect();
                if p.get(0) == Some(&"ler") && p.len() == 3 {
                    let b = p[1];
                    if let Ok(c) = p[2].parse::<i32>() {
                        match db::ler_capitulo_biblia(b, c) {
                            Ok(v) if !v.is_empty() => {
                                self.biblia_versiculos = v;
                                self.biblia_referencia = format!("{} {}", b, c).to_uppercase();
                                self.status_message = (
                                    format!("Carregado: {}.", self.biblia_referencia),
                                    MessageType::Success,
                                );
                                self.biblia_scroll = 0;
                            }
                            Ok(_) => {
                                self.status_message = (
                                    format!("Nenhum resultado para '{} {}'.", b, c),
                                    MessageType::Info,
                                );
                            }
                            Err(_) => {
                                self.status_message = (
                                    format!("Erro: Livro '{}' não encontrado.", b),
                                    MessageType::Error,
                                );
                            }
                        }
                    } else {
                        self.status_message =
                            ("Erro: Capítulo inválido.".to_string(), MessageType::Error);
                    }
                } else {
                    self.status_message = ("Comando inválido.".to_string(), MessageType::Error);
                }
            }
            CurrentScreen::AcoesList => {
                if db::criar_acao(command_text).is_ok() {
                    self.refresh_acoes();
                    self.status_message = ("Ação criada.".to_string(), MessageType::Success);
                } else {
                    self.status_message = ("Erro ao criar ação.".to_string(), MessageType::Error);
                }
            }
            CurrentScreen::ResolucoesList => {
                if db::criar_resolucao(command_text).is_ok() {
                    self.refresh_resolucoes();
                    self.status_message = ("Resolução criada.".to_string(), MessageType::Success);
                } else {
                    self.status_message =
                        ("Erro ao criar resolução.".to_string(), MessageType::Error);
                }
            }
            _ => {}
        }
        self.input.clear();
        self.input_mode = InputMode::Normal;
    }
    pub fn quit(&mut self) {
        self.should_quit = true;
    }
    pub fn next(&mut self) {
        match self.current_screen {
            CurrentScreen::SalmoView => {
                self.salmo_scroll = self.salmo_scroll.saturating_add(1);
            }
            CurrentScreen::SalterioList => {
                let i = self.salmos_state.selected().unwrap_or(0);
                self.salmos_state
                    .select(Some(if i >= self.salmos.len() - 1 { 0 } else { i + 1 }));
            }
            CurrentScreen::AcoesList => {
                let i = self.acoes_list_state.selected().unwrap_or(0);
                self.acoes_list_state
                    .select(Some(if i >= self.acoes.len() - 1 { 0 } else { i + 1 }));
            }
            CurrentScreen::ResolucoesList => {
                let i = self.resolucoes_list_state.selected().unwrap_or(0);
                self.resolucoes_list_state
                    .select(Some(if i >= self.resolucoes.len() - 1 {
                        0
                    } else {
                        i + 1
                    }));
            }
            CurrentScreen::DiarioList => {
                let i = self.diario_list_state.selected().unwrap_or(0);
                self.diario_list_state
                    .select(Some(if i >= self.diario_entradas.len() - 1 {
                        0
                    } else {
                        i + 1
                    }));
            }
            CurrentScreen::CfwList => {
                let i = self.cfw_list_state.selected().unwrap_or(0);
                self.cfw_list_state
                    .select(Some(if i >= self.cfw_capitulos.len() - 1 {
                        0
                    } else {
                        i + 1
                    }));
            }
            CurrentScreen::CmwList => {
                let i = self.cmw_list_state.selected().unwrap_or(0);
                self.cmw_list_state
                    .select(Some(if i >= self.cmw_perguntas.len() - 1 {
                        0
                    } else {
                        i + 1
                    }));
            }
            CurrentScreen::BcwList => {
                let i = self.bcw_list_state.selected().unwrap_or(0);
                self.bcw_list_state
                    .select(Some(if i >= self.bcw_perguntas.len() - 1 {
                        0
                    } else {
                        i + 1
                    }));
            }
            CurrentScreen::Biblia => {
                self.biblia_scroll = self.biblia_scroll.saturating_add(1);
            }
            CurrentScreen::DiarioView => {
                self.diario_scroll = self.diario_scroll.saturating_add(1);
            }
            CurrentScreen::CfwSections => {
                self.cfw_scroll = self.cfw_scroll.saturating_add(1);
            }
            CurrentScreen::CmwAnswer => {
                self.cmw_scroll = self.cmw_scroll.saturating_add(1);
            }
            CurrentScreen::BcwAnswer => {
                self.bcw_scroll = self.bcw_scroll.saturating_add(1);
            }
            _ => {}
        }
    }
    pub fn previous(&mut self) {
        match self.current_screen {
            CurrentScreen::SalmoView => {
                self.salmo_scroll = self.salmo_scroll.saturating_sub(1);
            }
            CurrentScreen::SalterioList => {
                let i = self.salmos_state.selected().unwrap_or(0);
                self.salmos_state
                    .select(Some(if i == 0 { self.salmos.len() - 1 } else { i - 1 }));
            }
            CurrentScreen::AcoesList => {
                let i = self.acoes_list_state.selected().unwrap_or(0);
                self.acoes_list_state.select(Some(if i == 0 {
                    self.acoes.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::ResolucoesList => {
                let i = self.resolucoes_list_state.selected().unwrap_or(0);
                self.resolucoes_list_state.select(Some(if i == 0 {
                    self.resolucoes.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::DiarioList => {
                let i = self.diario_list_state.selected().unwrap_or(0);
                self.diario_list_state.select(Some(if i == 0 {
                    self.diario_entradas.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::CfwList => {
                let i = self.cfw_list_state.selected().unwrap_or(0);
                self.cfw_list_state.select(Some(if i == 0 {
                    self.cfw_capitulos.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::CmwList => {
                let i = self.cmw_list_state.selected().unwrap_or(0);
                self.cmw_list_state.select(Some(if i == 0 {
                    self.cmw_perguntas.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::BcwList => {
                let i = self.bcw_list_state.selected().unwrap_or(0);
                self.bcw_list_state.select(Some(if i == 0 {
                    self.bcw_perguntas.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::Biblia => {
                self.biblia_scroll = self.biblia_scroll.saturating_sub(1);
            }
            CurrentScreen::DiarioView => {
                self.diario_scroll = self.diario_scroll.saturating_sub(1);
            }
            CurrentScreen::CfwSections => {
                self.cfw_scroll = self.cfw_scroll.saturating_sub(1);
            }
            CurrentScreen::CmwAnswer => {
                self.cmw_scroll = self.cmw_scroll.saturating_sub(1);
            }
            CurrentScreen::BcwAnswer => {
                self.bcw_scroll = self.bcw_scroll.saturating_sub(1);
            }
            _ => {}
        }
    }
}
