use crate::{app::App, components::Module, db, theme::Theme};
use chrono::{Datelike, Local};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Style, Stylize},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
    Frame,
};

/// Retorna as áreas de layout principais: [painel_esquerdo, conteudo_principal, rodapé]
pub fn get_layout_chunks(area: Rect) -> Vec<Rect> {
    let layout_vertical = Layout::new(
        Direction::Vertical,
        [Constraint::Min(0), Constraint::Length(3)],
    )
    .split(area);

    let layout_horizontal = Layout::new(
        Direction::Horizontal,
        [Constraint::Percentage(30), Constraint::Percentage(70)],
    )
    .split(layout_vertical[0]);

    vec![layout_horizontal[0], layout_horizontal[1], layout_vertical[1]]
}

/// Função de renderização principal, chamada a cada ciclo do loop.
pub fn render(frame: &mut Frame, app: &mut App) {
    if let Some(mut component) = app.component_stack.pop() {
        let theme = &app.theme;
        let active_module = component.get_module();

        frame.render_widget(Block::default().style(theme.base_style), frame.size());
        let chunks = get_layout_chunks(frame.size());
        
        let left_chunks = Layout::new(
            Direction::Vertical,
            [Constraint::Length(7), Constraint::Min(0)],
        )
        .split(chunks[0]);

        render_main_menu(theme, &app.audio_process, frame, left_chunks[0], active_module);
        render_status_foco_panel(theme, frame, left_chunks[1]);

        component.render(frame, theme);
        app.component_stack.push(component);
    }
}

fn render_main_menu(
    theme: &Theme,
    audio_process: &Option<std::process::Child>,
    frame: &mut Frame,
    area: Rect,
    active_module: Module,
) {
    let canto_style = if matches!(active_module, Module::Canto) { theme.selected_style } else { theme.base_style };
    let piedade_style = if matches!(active_module, Module::Piedade) { theme.selected_style } else { theme.base_style };
    let estudo_style = if matches!(active_module, Module::Estudo) { theme.selected_style } else { theme.base_style };
    
    let audio_indicator = if audio_process.is_some() { "[♫]" } else { "   " };
    let canto_label = format!("{} [1] Canto  ", audio_indicator);

    let nav_text = vec![
        Line::from(""),
        Line::from(Span::styled(canto_label, canto_style)),
        Line::from(Span::styled("   [2] Piedade", piedade_style)),
        Line::from(Span::styled("   [3] Estudo ", estudo_style)),
    ];

    let paragraph = Paragraph::new(nav_text)
        .block(Block::default().title("Menu Principal").borders(Borders::ALL))
        .style(theme.base_style);
    frame.render_widget(paragraph, area);
}

fn render_status_foco_panel(theme: &Theme, frame: &mut Frame, area: Rect) {
    let today = Local::now().date_naive();
    let today_str = today.format("%Y-%m-%d").to_string();
    let entradas_hoje = db::get_entradas_diario_range(&today_str, &format!("{} 23:59:59", today_str)).unwrap_or_default();

    let weekday = today.weekday();
    let dia_do_senhor_msg = match weekday {
        chrono::Weekday::Sat => "Preparação: O Dia do Senhor é amanhã.".to_string(),
        chrono::Weekday::Sun => "Hoje é o Dia do Senhor.".to_string(),
        _ => format!("Próximo Culto: Domingo (em {} dias)", (7 - weekday.num_days_from_sunday()) % 7),
    };

    let is_fasting = entradas_hoje.iter().any(|e| e.tipo == "JEJUM");
    let estado_msg = if is_fasting { "Estado: Em Jejum" } else { "Estado: Normal" };

    let has_leitura = entradas_hoje.iter().any(|e| e.tipo == "LEITURA");
    let has_autoexame = entradas_hoje.iter().any(|e| e.tipo == "AUTO_EXAME");
    let has_sermao = entradas_hoje.iter().any(|e| e.tipo == "SERMAO");

    let mut rotina_items = vec![
        Line::from(format!("[{}] Leitura Bíblica", if has_leitura { 'X' } else { ' ' })),
        Line::from(format!("[{}] Autoexame", if has_autoexame { 'X' } else { ' ' })),
    ];
    if weekday == chrono::Weekday::Sun {
        rotina_items.push(Line::from(format!("[{}] Registrar Sermão", if has_sermao { 'X' } else { ' ' })));
    }
    
    let text = vec![
        Line::from(Span::styled(dia_do_senhor_msg, Style::default().fg(theme.yellow))),
        Line::from(estado_msg),
        Line::from(""),
        Line::from(Span::raw("Rotina de Hoje:")),
    ];

    let block = Block::default().title("Status & Foco").borders(Borders::ALL);
    let inner_area = block.inner(area);
    frame.render_widget(block, area);

    let content_chunks = Layout::new(Direction::Vertical, [Constraint::Length(5), Constraint::Min(0)]).split(inner_area);
    frame.render_widget(Paragraph::new(text), content_chunks[0]);
    frame.render_widget(Paragraph::new(rotina_items), content_chunks[1]);
}

pub fn styled_block<'a>(title: &'a str, theme: &Theme) -> Block<'a> {
    Block::default()
        .title(Span::styled(title, Style::default().fg(theme.green).bold()))
        .borders(Borders::ALL)
        .border_style(Style::default().fg(theme.dim_fg))
}

pub fn clear_area() -> ratatui::widgets::Clear { ratatui::widgets::Clear }

pub fn centered_rect(percent_x: u16, percent_y: u16, r: Rect) -> Rect {
    let popup_layout = Layout::new(Direction::Vertical, [
        Constraint::Percentage((100 - percent_y) / 2),
        Constraint::Percentage(percent_y),
        Constraint::Percentage((100 - percent_y) / 2),
    ]).split(r);
    Layout::new(Direction::Horizontal, [
        Constraint::Percentage((100 - percent_x) / 2),
        Constraint::Percentage(percent_x),
        Constraint::Percentage((100 - percent_x) / 2),
    ]).split(popup_layout[1])[1]
}
