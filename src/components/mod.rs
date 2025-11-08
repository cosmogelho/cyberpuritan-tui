pub mod acoes_list;
pub mod bcw_list;
pub mod biblia;
pub mod catecismo_answer;
pub mod cfw_list;
pub mod cmw_list;
pub mod diario_list_unificado;
pub mod diario_view_unificado;
pub mod estudo_menu;
pub mod gerenciar_perguntas;
pub mod list_state;
pub mod main_menu;
pub mod nova_entrada_autoexame;
pub mod nova_entrada_evangelismo;
pub mod nova_entrada_jejum;
pub mod nova_entrada_leitura;
pub mod nova_entrada_menu;
pub mod nova_entrada_resolucao;
pub mod nova_entrada_sermao;
pub mod oracao_view;
pub mod oracoes_list;
pub mod piedade_dashboard;
pub mod resolucoes_list;
pub mod salmo_view;
pub mod salterio_list;
pub mod symbols_menu;
pub mod utils;

use crate::{app::App, theme::Theme};
use crossterm::event::KeyEvent;
use ratatui::Frame;

#[derive(Clone, Copy)]
pub enum Module {
    Canto,
    Piedade,
    Estudo,
}

pub enum Action {
    Quit,
    Pop,
    Navigate(Box<dyn Component>),
    LaunchEditor,
}

pub trait Component {
    fn get_module(&self) -> Module;
    fn handle_key_events(&mut self, key: KeyEvent, app: &mut App) -> Option<Action>;
    fn render(&mut self, frame: &mut Frame, theme: &Theme);
}
