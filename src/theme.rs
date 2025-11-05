use ratatui::style::{Color, Style, Stylize};

pub struct Theme {
    pub bg: Color,
    pub fg: Color,
    pub highlight_bg: Color,
    pub yellow: Color,
    pub green: Color,
    pub blue: Color,
    pub red: Color,
    pub dim_fg: Color,
    
    pub base_style: Style,
    pub header_style: Style,
    pub selected_style: Style,
}

impl Theme {
    pub fn new() -> Self {
        let bg = Color::Rgb(40, 40, 40);
        let fg = Color::Rgb(235, 219, 178);
        let highlight_bg = Color::Rgb(60, 56, 54);
        let yellow = Color::Rgb(250, 189, 47);
        let green = Color::Rgb(184, 187, 38);
        let blue = Color::Rgb(131, 165, 152);
        let red = Color::Rgb(251, 73, 52);
        let dim_fg = Color::Rgb(146, 131, 116);

        Self {
            bg, fg, highlight_bg, yellow, green, blue, red, dim_fg,
            base_style: Style::default().bg(bg).fg(fg),
            header_style: Style::default().fg(blue).bold(),
            selected_style: Style::default().bg(highlight_bg).fg(fg),
        }
    }
}
