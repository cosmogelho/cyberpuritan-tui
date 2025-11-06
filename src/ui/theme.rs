use ratatui::style::{Color, Style};

pub const GRUVBOX_BG: Color = Color::Rgb(40, 40, 40);
pub const GRUVBOX_FG: Color = Color::Rgb(235, 219, 178);

pub fn get_theme() -> Style {
    Style::default().fg(GRUVBOX_FG).bg(GRUVBOX_BG)
}
