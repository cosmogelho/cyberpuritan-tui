use crate::{db, models::*, theme::Theme};
use ratatui::widgets::TableState;
use std::path::Path;
use std::process::{Child, Command};

// --- Enums de Estado ---
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

// --- Structs de Estado Específicos ---
pub struct SalterioState {
    pub items: Vec<Salmo>,
    pub list_state: TableState,
    pub scroll: u16,
}
pub struct DiarioState {
    pub entries: Vec<EntradaDiario>,
    pub list_state: TableState,
    pub scroll: u16,
}
pub struct AcoesState {
    pub items: Vec<Acao>,
    pub list_state: TableState,
}
pub struct ResolucoesState {
    pub items: Vec<Resolucao>,
    pub list_state: TableState,
}
pub struct CfwState {
    pub chapters: Vec<CfwCapitulo>,
    pub list_state: TableState,
    pub sections: Vec<CfwSecao>,
    pub current_chapter_title: String,
    pub scroll: u16,
}
pub struct CmwState {
    pub questions: Vec<CatecismoPergunta>,
    pub list_state: TableState,
    pub scroll: u16,
}
pub struct BcwState {
    pub questions: Vec<CatecismoPergunta>,
    pub list_state: TableState,
    pub scroll: u16,
}
pub struct BibliaState {
    pub verses: Vec<Versiculo>,
    pub reference: String,
    pub scroll: u16,
}

// --- Struct Principal da Aplicação ---
pub struct App {
    pub should_quit: bool,
    pub current_screen: CurrentScreen,
    pub input: String,
    pub input_mode: InputMode,
    pub status_message: (String, MessageType),
    pub theme: Theme,
    pub audio_process: Option<Child>,

    // Estados Modulares
    pub salterio: SalterioState,
    pub diario: DiarioState,
    pub acoes: AcoesState,
    pub resolucoes: ResolucoesState,
    pub cfw: CfwState,
    pub cmw: CmwState,
    pub bcw: BcwState,
    pub biblia: BibliaState,
}

impl App {
    pub fn new(
        s: Vec<Salmo>,
        cfw_items: Vec<CfwCapitulo>,
        cmw_items: Vec<CatecismoPergunta>,
        bcw_items: Vec<CatecismoPergunta>,
        diario_items: Vec<EntradaDiario>,
        acoes_items: Vec<Acao>,
        resolucoes_items: Vec<Resolucao>,
    ) -> Self {
        Self {
            should_quit: false,
            current_screen: CurrentScreen::SalterioList,
            input: String::new(),
            input_mode: InputMode::Normal,
            status_message: ("Bem-vindo!".to_string(), MessageType::Info),
            theme: Theme::new(),
            audio_process: None,

            salterio: SalterioState {
                items: s,
                list_state: TableState::default().with_selected(0),
                scroll: 0,
            },
            diario: DiarioState {
                entries: diario_items,
                list_state: TableState::default().with_selected(0),
                scroll: 0,
            },
            acoes: AcoesState {
                items: acoes_items,
                list_state: TableState::default().with_selected(0),
            },
            resolucoes: ResolucoesState {
                items: resolucoes_items,
                list_state: TableState::default().with_selected(0),
            },
            cfw: CfwState {
                chapters: cfw_items,
                list_state: TableState::default().with_selected(0),
                sections: Vec::new(),
                current_chapter_title: String::new(),
                scroll: 0,
            },
            cmw: CmwState {
                questions: cmw_items,
                list_state: TableState::default().with_selected(0),
                scroll: 0,
            },
            bcw: BcwState {
                questions: bcw_items,
                list_state: TableState::default().with_selected(0),
                scroll: 0,
            },
            biblia: BibliaState {
                verses: Vec::new(),
                reference: "Nenhuma passagem".to_string(),
                scroll: 0,
            },
        }
    }

    // --- Métodos de Atualização de Dados ---
    pub fn refresh_diario(&mut self) {
        if let Ok(e) = db::listar_entradas_diario() {
            self.diario.entries = e;
            self.diario.list_state.select(Some(0));
        }
    }
    pub fn refresh_acoes(&mut self) {
        if let Ok(a) = db::listar_acoes() {
            self.acoes.items = a;
            self.acoes.list_state.select(Some(0));
        }
    }
    pub fn refresh_resolucoes(&mut self) {
        if let Ok(r) = db::listar_resolucoes() {
            self.resolucoes.items = r;
            self.resolucoes.list_state.select(Some(0));
        }
    }

    // --- Métodos de Navegação ---
    pub fn enter_salmo_view(&mut self) {
        self.salterio.scroll = 0;
        self.current_screen = CurrentScreen::SalmoView;
    }
    pub fn enter_diario_view(&mut self) {
        self.diario.scroll = 0;
        self.current_screen = CurrentScreen::DiarioView;
    }
    pub fn enter_cfw_chapter_view(&mut self) {
        if let Some(i) = self.cfw.list_state.selected() {
            if let Some(c) = self.cfw.chapters.get(i) {
                if let Ok(s) = db::ler_secoes_cfw(c.chapter) {
                    self.cfw.sections = s;
                    self.cfw.current_chapter_title = c.title.clone();
                    self.cfw.scroll = 0;
                    self.current_screen = CurrentScreen::CfwSections;
                }
            }
        }
    }
    pub fn enter_cmw_answer_view(&mut self) {
        self.cmw.scroll = 0;
        self.current_screen = CurrentScreen::CmwAnswer;
    }
    pub fn enter_bcw_answer_view(&mut self) {
        self.bcw.scroll = 0;
        self.current_screen = CurrentScreen::BcwAnswer;
    }

    // --- Métodos de Seleção ---
    pub fn selected_diario_entry(&self) -> Option<&EntradaDiario> {
        self.diario
            .entries
            .get(self.diario.list_state.selected().unwrap_or(0))
    }
    pub fn selected_salmo(&self) -> Option<&Salmo> {
        self.salterio
            .items
            .get(self.salterio.list_state.selected().unwrap_or(0))
    }
    pub fn selected_cmw_question(&self) -> Option<&CatecismoPergunta> {
        self.cmw
            .questions
            .get(self.cmw.list_state.selected().unwrap_or(0))
    }
    pub fn selected_bcw_question(&self) -> Option<&CatecismoPergunta> {
        self.bcw
            .questions
            .get(self.bcw.list_state.selected().unwrap_or(0))
    }

    // --- Métodos de Áudio ---
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
                    self.status_message =
                        ("Erro: 'mpv' não encontrado.".to_string(), MessageType::Error);
                }
            } else {
                self.status_message =
                    ("Erro: Arquivo não encontrado.".to_string(), MessageType::Error);
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

    // --- Lógica de Comandos ---
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
                                self.biblia.verses = v;
                                self.biblia.reference = format!("{} {}", b, c).to_uppercase();
                                self.status_message = (
                                    format!("Carregado: {}.", self.biblia.reference),
                                    MessageType::Success,
                                );
                                self.biblia.scroll = 0;
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

    // --- Métodos de Navegação em Listas ---
    pub fn quit(&mut self) {
        self.should_quit = true;
    }
    pub fn next(&mut self) {
        match self.current_screen {
            CurrentScreen::SalmoView => self.salterio.scroll = self.salterio.scroll.saturating_add(1),
            CurrentScreen::SalterioList => {
                let i = self.salterio.list_state.selected().unwrap_or(0);
                self.salterio.list_state.select(Some(
                    if i >= self.salterio.items.len() - 1 { 0 } else { i + 1 },
                ));
            }
            CurrentScreen::AcoesList => {
                let i = self.acoes.list_state.selected().unwrap_or(0);
                self.acoes.list_state.select(Some(
                    if i >= self.acoes.items.len() - 1 { 0 } else { i + 1 },
                ));
            }
            CurrentScreen::ResolucoesList => {
                let i = self.resolucoes.list_state.selected().unwrap_or(0);
                self.resolucoes.list_state.select(Some(
                    if i >= self.resolucoes.items.len() - 1 { 0 } else { i + 1 },
                ));
            }
            CurrentScreen::DiarioList => {
                let i = self.diario.list_state.selected().unwrap_or(0);
                self.diario.list_state.select(Some(
                    if i >= self.diario.entries.len() - 1 { 0 } else { i + 1 },
                ));
            }
            CurrentScreen::CfwList => {
                let i = self.cfw.list_state.selected().unwrap_or(0);
                self.cfw.list_state.select(Some(
                    if i >= self.cfw.chapters.len() - 1 { 0 } else { i + 1 },
                ));
            }
            CurrentScreen::CmwList => {
                let i = self.cmw.list_state.selected().unwrap_or(0);
                self.cmw.list_state.select(Some(
                    if i >= self.cmw.questions.len() - 1 { 0 } else { i + 1 },
                ));
            }
            CurrentScreen::BcwList => {
                let i = self.bcw.list_state.selected().unwrap_or(0);
                self.bcw.list_state.select(Some(
                    if i >= self.bcw.questions.len() - 1 { 0 } else { i + 1 },
                ));
            }
            CurrentScreen::Biblia => self.biblia.scroll = self.biblia.scroll.saturating_add(1),
            CurrentScreen::DiarioView => self.diario.scroll = self.diario.scroll.saturating_add(1),
            CurrentScreen::CfwSections => self.cfw.scroll = self.cfw.scroll.saturating_add(1),
            CurrentScreen::CmwAnswer => self.cmw.scroll = self.cmw.scroll.saturating_add(1),
            CurrentScreen::BcwAnswer => self.bcw.scroll = self.bcw.scroll.saturating_add(1),
            _ => {}
        }
    }
    pub fn previous(&mut self) {
        match self.current_screen {
            CurrentScreen::SalmoView => self.salterio.scroll = self.salterio.scroll.saturating_sub(1),
            CurrentScreen::SalterioList => {
                let i = self.salterio.list_state.selected().unwrap_or(0);
                self.salterio.list_state.select(Some(if i == 0 {
                    self.salterio.items.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::AcoesList => {
                let i = self.acoes.list_state.selected().unwrap_or(0);
                self.acoes.list_state.select(Some(if i == 0 {
                    self.acoes.items.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::ResolucoesList => {
                let i = self.resolucoes.list_state.selected().unwrap_or(0);
                self.resolucoes.list_state.select(Some(if i == 0 {
                    self.resolucoes.items.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::DiarioList => {
                let i = self.diario.list_state.selected().unwrap_or(0);
                self.diario.list_state.select(Some(if i == 0 {
                    self.diario.entries.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::CfwList => {
                let i = self.cfw.list_state.selected().unwrap_or(0);
                self.cfw.list_state.select(Some(if i == 0 {
                    self.cfw.chapters.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::CmwList => {
                let i = self.cmw.list_state.selected().unwrap_or(0);
                self.cmw.list_state.select(Some(if i == 0 {
                    self.cmw.questions.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::BcwList => {
                let i = self.bcw.list_state.selected().unwrap_or(0);
                self.bcw.list_state.select(Some(if i == 0 {
                    self.bcw.questions.len() - 1
                } else {
                    i - 1
                }));
            }
            CurrentScreen::Biblia => self.biblia.scroll = self.biblia.scroll.saturating_sub(1),
            CurrentScreen::DiarioView => self.diario.scroll = self.diario.scroll.saturating_sub(1),
            CurrentScreen::CfwSections => self.cfw.scroll = self.cfw.scroll.saturating_sub(1),
            CurrentScreen::CmwAnswer => self.cmw.scroll = self.cmw.scroll.saturating_sub(1),
            CurrentScreen::BcwAnswer => self.bcw.scroll = self.bcw.scroll.saturating_sub(1),
            _ => {}
        }
    }
}
