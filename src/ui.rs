use crate::{app::App, components::Module, theme::Theme};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::{Style, Stylize},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
    Frame,
};
use std::process::Child;

/// Retorna as áreas de layout principais: [menu, conteúdo, rodapé]
pub fn get_layout_chunks(area: Rect) -> Vec<Rect> {
    let layout = Layout::new(
        Direction::Vertical,
        [Constraint::Min(0), Constraint::Length(3)],
    )
    .split(area);

    let top_layout = Layout::new(
        Direction::Horizontal,
        [Constraint::Percentage(30), Constraint::Percentage(70)],
    )
    .split(layout[0]);

    vec![top_layout[0], top_layout[1], layout[1]]
}

/// Função de renderização principal, chamada a cada ciclo do loop.
pub fn render(frame: &mut Frame, app: &mut App) {
    if let Some(mut component) = app.component_stack.pop() {
        let theme = &app.theme;
        let audio_process = &app.audio_process;
        let active_module = component.get_module();

        // Renderiza o layout base
        frame.render_widget(Block::default().style(theme.base_style), frame.size());
        let chunks = get_layout_chunks(frame.size());
        render_main_menu(theme, audio_process, frame, chunks[0], active_module);

        // Delega a renderização do conteúdo ao componente
        component.render(frame, theme);

        // Coloca o componente de volta
        app.component_stack.push(component);
    }
}

/// Renderiza o painel de navegação esquerdo, destacando o módulo ativo.
fn render_main_menu(
    theme: &Theme,
    audio_process: &Option<Child>,
    frame: &mut Frame,
    area: Rect,
    active_module: Module,
) {
    let canto_style = if matches!(active_module, Module::Canto) {
        theme.selected_style
    } else {
        theme.base_style
    };
    let piedade_style = if matches!(active_module, Module::Piedade) {
        theme.selected_style
    } else {
        theme.base_style
    };
    let estudo_style = if matches!(active_module, Module::Estudo) {
        theme.selected_style
    } else {
        theme.base_style
    };

    let audio_indicator = if audio_process.is_some() { "[♫]" } else { "   " };
    let canto_label = format!("{} [1] Canto  ", audio_indicator);

    let nav_text = vec![
        Line::from("Navegação:"),
        Line::from(""),
        Line::from(Span::styled(canto_label, canto_style)),
        Line::from(Span::styled("   [2] Piedade", piedade_style)),
        Line::from(Span::styled("   [3] Estudo ", estudo_style)),
    ];

    let paragraph = Paragraph::new(nav_text)
        .block(
            Block::default()
                .title("Menu Principal")
                .borders(Borders::ALL),
        )
        .style(theme.base_style);
    frame.render_widget(paragraph, area);
}

/// Helper para criar um bloco estilizado padrão.
pub fn styled_block<'a>(title: &'a str, theme: &Theme) -> Block<'a> {
    Block::default()
        .title(Span::styled(title, Style::default().fg(theme.green).bold()))
        .borders(Borders::ALL)
        .border_style(Style::default().fg(theme.dim_fg))
}
