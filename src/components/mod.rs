pub mod acoes_list;
pub mod bcw_answer;
pub mod bcw_list;
pub mod biblia;
pub mod cfw_list;
pub mod cfw_sections;
pub mod cmw_answer;
pub mod cmw_list;
pub mod diario_list;
pub mod diario_view;
pub mod estudo_menu;
pub mod piedade_menu;
pub mod resolucoes_list;
pub mod salmo_view;
pub mod salterio_list;
pub mod symbols_menu;

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
