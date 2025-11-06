pub use crate::db::schema::{Acoes, Bcw, Book, Cfw, Cmw, Diario, Resolucoes, Salterio, Verse};
use crate::repository::{canon::CanonRepo, piety::PietyRepo};
use crate::utils::{audio, error::AppError};
use ratatui::widgets::{ListState, TableState};
use std::process::Child;

#[derive(Default, Copy, Clone, PartialEq, Eq, Debug)] pub enum Module { #[default] Canto, Piedade, Estudo }
#[derive(Clone, PartialEq, Eq, Debug)]
pub enum View {
    PsalmList, PsalmDetail, PietyMenu, ActionList, ResolutionList, DiarioList, StudyMenu,
    FaithSymbolsMenu, ConfessionView, ConfessionDetail,
    LargerCatechismView, LargerCatechismDetail, ShorterCatechismView, ShorterCatechismDetail,
    BibleView, ActionEdit{id: Option<i32>, text: String},
    ResolutionEdit{id: Option<i32>, text: String}, DiarioEdit{id: Option<i32>, text: String},
}
#[derive(Default, Copy, Clone, PartialEq, Eq)] pub enum BiblePane { #[default] Books, Chapters, Text }
#[derive(Default)]
pub struct BibleState { pub active_pane: BiblePane, pub book_list_state: ListState, pub chapter_list_state: ListState, pub chapters: Vec<i32>, pub verses: Vec<Verse>, pub text_scroll: u16, }

pub struct App {
    pub running: bool, pub active_module: Module, pub view_stack: Vec<View>, pub audio_process: Option<Child>,
    pub canon_repo: CanonRepo, pub piety_repo: PietyRepo,
    pub salmos: Vec<Salterio>, pub acoes: Vec<Acoes>, pub resolucoes: Vec<Resolucoes>, pub diario: Vec<Diario>,
    pub cfw: Vec<Cfw>, pub cmw: Vec<Cmw>, pub bcw: Vec<Bcw>, pub books: Vec<Book>,
    pub psalm_list_state: TableState, pub action_list_state: TableState, pub resolution_list_state: TableState, pub diario_list_state: TableState,
    pub cfw_list_state: TableState, pub cmw_list_state: TableState, pub bcw_list_state: TableState,
    pub bible_state: BibleState,
}
impl App {
    pub fn new() -> Result<Self, AppError> {
        let canon_repo = CanonRepo::new()?;
        let piety_repo = PietyRepo::new()?;
        Ok(Self {
            running: true, active_module: Module::Canto, view_stack: vec![View::PsalmList],
            audio_process: None,
            salmos: canon_repo.get_all_psalms()?,
            acoes: piety_repo.get_all_acoes()?,
            resolucoes: piety_repo.get_all_resolucoes()?,
            diario: piety_repo.get_all_diario()?,
            cfw: canon_repo.get_all_cfw()?, cmw: canon_repo.get_all_cmw()?, bcw: canon_repo.get_all_bcw()?, books: canon_repo.get_all_books()?,
            canon_repo, piety_repo,
            psalm_list_state: TableState::default(), action_list_state: TableState::default(),
            resolution_list_state: TableState::default(), diario_list_state: TableState::default(),
            cfw_list_state: TableState::default(), cmw_list_state: TableState::default(), bcw_list_state: TableState::default(),
            bible_state: BibleState::default(),
        })
    }
    pub fn push_view(&mut self, view: View) { self.view_stack.push(view); }
    pub fn pop_view(&mut self) { if self.view_stack.len() > 1 { self.view_stack.pop(); } else { self.active_module = Module::Canto; self.view_stack = vec![View::PsalmList]; } }
    pub fn start_playback(&mut self, is_acapella: bool) -> Result<(), AppError> { self.stop_playback()?; if let Some(sel) = self.psalm_list_state.selected() { let salmo = &self.salmos[sel]; let path = if is_acapella { salmo.a_capela.as_deref() } else { salmo.instrumental.as_deref() }; if let Some(p) = path { self.audio_process = Some(audio::play(&format!("./data/saltério/{}", p))?); } } Ok(()) }
    pub fn stop_playback(&mut self) -> Result<(), AppError> { if let Some(mut child) = self.audio_process.take() { audio::stop(&mut child)?; } Ok(()) }
    pub fn reload_piety_data(&mut self) -> Result<(), AppError> { self.acoes = self.piety_repo.get_all_acoes()?; self.resolucoes = self.piety_repo.get_all_resolucoes()?; self.diario = self.piety_repo.get_all_diario()?; Ok(()) }
    pub fn handle_input(&mut self, c: char) { if let Some(v) = self.view_stack.last_mut() { match v { View::ActionEdit{text,..} | View::ResolutionEdit{text,..} | View::DiarioEdit{text,..} => text.push(c), _ => {} } } }
    pub fn handle_backspace(&mut self) { if let Some(v) = self.view_stack.last_mut() { match v { View::ActionEdit{text,..} | View::ResolutionEdit{text,..} | View::DiarioEdit{text,..} => { text.pop(); }, _ => {} } } }
    pub fn select_book(&mut self) -> Result<(), AppError> { if let Some(sel) = self.bible_state.book_list_state.selected() { let book_id = self.books[sel].id; self.bible_state.chapters = self.canon_repo.get_chapters_by_book(book_id)?; self.bible_state.chapter_list_state.select(Some(0)); self.select_chapter()?; self.bible_state.active_pane = BiblePane::Chapters; } Ok(()) }
    pub fn select_chapter(&mut self) -> Result<(), AppError> { if let (Some(b_idx), Some(c_idx)) = (self.bible_state.book_list_state.selected(), self.bible_state.chapter_list_state.selected()) { let book_id = self.books[b_idx].id; let chapter = self.bible_state.chapters[c_idx]; self.bible_state.verses = self.canon_repo.get_verses_by_chapter(book_id, chapter)?; self.bible_state.text_scroll = 0; self.bible_state.active_pane = BiblePane::Text; } Ok(()) }
    pub fn next_bible_pane(&mut self) { self.bible_state.active_pane = match self.bible_state.active_pane { BiblePane::Books => BiblePane::Chapters, BiblePane::Chapters => BiblePane::Text, BiblePane::Text => BiblePane::Books, }; }
}
