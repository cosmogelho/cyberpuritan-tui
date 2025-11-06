use crate::app::{App, CurrentScreen, InputMode, MessageType};
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::{Style, Stylize},
    text::{Line, Span},
    widgets::{Block, Borders, HighlightSpacing, Paragraph, Row, Table, Wrap},
    Frame,
};

pub fn render(app: &mut App, frame: &mut Frame) {
    frame.render_widget(Block::default().style(app.theme.base_style), frame.size());
    let main_layout = Layout::new(
        Direction::Vertical,
        [Constraint::Min(0), Constraint::Length(3)],
    )
    .split(frame.size());
    let top_layout = Layout::new(
        Direction::Horizontal,
        [Constraint::Percentage(30), Constraint::Percentage(70)],
    )
    .split(main_layout[0]);

    render_main_menu(app, frame, top_layout[0]);

    match app.current_screen {
        CurrentScreen::SalterioList => {
            render_salmos_table(app, frame, top_layout[1]);
            render_salmos_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::SalmoView => {
            render_salmo_view(app, frame, top_layout[1]);
            render_text_view_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::PiedadeMenu => {
            render_piedade_menu(app, frame, top_layout[1]);
            render_menu_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::AcoesList => {
            render_acoes_list(app, frame, top_layout[1]);
            render_acoes_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::ResolucoesList => {
            render_resolucoes_list(app, frame, top_layout[1]);
            render_resolucoes_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::EstudoMenu => {
            render_estudo_menu(app, frame, top_layout[1]);
            render_menu_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::DiarioList => {
            render_diario_list(app, frame, top_layout[1]);
            render_diario_list_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::DiarioView => {
            render_diario_view(app, frame, top_layout[1]);
            render_text_view_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::SymbolsMenu => {
            render_symbols_menu(app, frame, top_layout[1]);
            render_symbols_menu_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::CfwList | CurrentScreen::CmwList | CurrentScreen::BcwList => {
            if let CurrentScreen::CfwList = app.current_screen {
                render_cfw_table(app, frame, top_layout[1]);
            } else if let CurrentScreen::CmwList = app.current_screen {
                render_cmw_table(app, frame, top_layout[1]);
            } else {
                render_bcw_table(app, frame, top_layout[1]);
            }
            render_list_view_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::CfwSections | CurrentScreen::CmwAnswer | CurrentScreen::BcwAnswer => {
            if let CurrentScreen::CfwSections = app.current_screen {
                render_cfw_sections(app, frame, top_layout[1]);
            } else if let CurrentScreen::CmwAnswer = app.current_screen {
                render_cmw_answer(app, frame, top_layout[1]);
            } else {
                render_bcw_answer(app, frame, top_layout[1]);
            }
            render_text_view_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::Biblia => {
            render_biblia_view(app, frame, top_layout[1]);
            render_biblia_footer(app, frame, main_layout[1]);
        }
        CurrentScreen::DiarioNew => {}
    }

    if let InputMode::Editing = app.input_mode {
        frame.set_cursor(
            main_layout[1].x + app.input.len() as u16 + 1,
            main_layout[1].y + 1,
        );
    }
}

fn render_main_menu(app: &App, frame: &mut Frame, area: Rect) {
    let is_canto_active = matches!(
        app.current_screen,
        CurrentScreen::SalterioList | CurrentScreen::SalmoView
    );
    let is_piedade_active = matches!(
        app.current_screen,
        CurrentScreen::PiedadeMenu
            | CurrentScreen::DiarioList
            | CurrentScreen::DiarioView
            | CurrentScreen::DiarioNew
            | CurrentScreen::AcoesList
            | CurrentScreen::ResolucoesList
    );
    let is_estudo_active = matches!(
        app.current_screen,
        CurrentScreen::EstudoMenu
            | CurrentScreen::SymbolsMenu
            | CurrentScreen::CfwList
            | CurrentScreen::CfwSections
            | CurrentScreen::CmwList
            | CurrentScreen::CmwAnswer
            | CurrentScreen::BcwList
            | CurrentScreen::BcwAnswer
            | CurrentScreen::Biblia
    );

    let canto_style = if is_canto_active {
        app.theme.selected_style
    } else {
        app.theme.base_style
    };
    let piedade_style = if is_piedade_active {
        app.theme.selected_style
    } else {
        app.theme.base_style
    };
    let estudo_style = if is_estudo_active {
        app.theme.selected_style
    } else {
        app.theme.base_style
    };

    let audio_indicator = if app.audio_process.is_some() {
        "[♫]"
    } else {
        "   "
    };
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
        .style(app.theme.base_style);
    frame.render_widget(paragraph, area);
}

fn styled_block<'a>(title: &'a str, theme: &crate::theme::Theme) -> Block<'a> {
    Block::default()
        .title(Span::styled(title, Style::default().fg(theme.green).bold()))
        .borders(Borders::ALL)
        .border_style(Style::default().fg(theme.dim_fg))
}
fn render_piedade_menu(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("\n [1] Diário\n\n [2] Ações de Santificação\n\n [3] Resoluções")
            .block(styled_block("Piedade", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_estudo_menu(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("\n\n   [1] Símbolos de Fé\n\n   [2] Bíblia")
            .block(styled_block("Estudo", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_symbols_menu(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let menu_text = "\n   [1] Confissão de Fé\n\n   [2] Catecismo Maior\n\n   [3] Breve Catecismo";
    frame.render_widget(
        Paragraph::new(menu_text)
            .block(styled_block("Símbolos de Fé", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_acoes_list(app: &mut App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let h = Row::new(["", "ID", "Descrição"]).style(app.theme.header_style);
    let r = app.acoes.iter().map(|a| {
        let (icon, s) = if a.status == "completo" {
            ("[✓]", Style::default().fg(app.theme.green).dim())
        } else {
            ("[ ]", app.theme.base_style)
        };
        Row::new(vec![
            Span::styled(icon, s),
            Span::raw(a.id.to_string()),
            Span::raw(a.descricao.clone()),
        ])
        .style(s)
    });
    let t = Table::new(
        r,
        &[
            Constraint::Length(3),
            Constraint::Length(4),
            Constraint::Min(20),
        ],
    )
    .header(h)
    .block(styled_block("Ações de Santificação", &app.theme))
    .highlight_style(app.theme.selected_style)
    .highlight_spacing(HighlightSpacing::Always);
    frame.render_stateful_widget(t, area, &mut app.acoes_list_state);
}
fn render_resolucoes_list(app: &mut App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let h = Row::new(["ID", "Texto"]).style(app.theme.header_style);
    let r = app
        .resolucoes
        .iter()
        .map(|r| Row::new([r.id.to_string(), r.texto.clone()]));
    let t = Table::new(r, &[Constraint::Length(4), Constraint::Min(20)])
        .header(h)
        .block(styled_block("Minhas Resoluções", &app.theme))
        .highlight_style(app.theme.selected_style)
        .highlight_spacing(HighlightSpacing::Always);
    frame.render_stateful_widget(t, area, &mut app.resolucoes_list_state);
}
fn render_diario_list(app: &mut App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let h = Row::new(["Data", "Início da Entrada"]).style(app.theme.header_style);
    let r = app.diario_entradas.iter().map(|e| {
        let p = e.texto.chars().take(80).collect::<String>() + "...";
        Row::new([e.data.clone(), p])
    });
    let t = Table::new(r, &[Constraint::Length(20), Constraint::Min(20)])
        .header(h)
        .block(styled_block("Diário", &app.theme))
        .highlight_style(app.theme.selected_style)
        .highlight_spacing(HighlightSpacing::Always);
    frame.render_stateful_widget(t, area, &mut app.diario_list_state);
}
fn render_diario_view(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    if let Some(e) = app.selected_diario_entry() {
        let title = format!("Diário - {}", e.data);
        let p = Paragraph::new(e.texto.as_str())
            .wrap(Wrap { trim: true })
            .scroll((app.diario_scroll, 0))
            .block(styled_block(&title, &app.theme))
            .style(app.theme.base_style);
        frame.render_widget(p, area);
    }
}
fn render_salmo_view(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    if let Some(s) = app.selected_salmo() {
        let txt = s.letra.as_deref().unwrap_or("Letra não disponível.");
        let title = format!("Salmo - {}", s.referencia);
        let p = Paragraph::new(txt)
            .wrap(Wrap { trim: true })
            .scroll((app.salmo_scroll, 0))
            .block(styled_block(&title, &app.theme))
            .style(app.theme.base_style);
        frame.render_widget(p, area);
    }
}
fn render_salmos_table(app: &mut App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let h = Row::new(["Ref.", "Melodia"]).style(app.theme.header_style);
    let r = app
        .salmos
        .iter()
        .map(|s| Row::new([s.referencia.clone(), s.melodia.clone().unwrap_or_default()]));
    let t = Table::new(r, &[Constraint::Percentage(40), Constraint::Percentage(60)])
        .header(h)
        .block(styled_block("Saltério", &app.theme))
        .highlight_style(app.theme.selected_style)
        .highlight_spacing(HighlightSpacing::Always);
    frame.render_stateful_widget(t, area, &mut app.salmos_state);
}
fn render_cfw_table(app: &mut App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let h = Row::new(["Cap.", "Título"]).style(app.theme.header_style);
    let r = app
        .cfw_capitulos
        .iter()
        .map(|c| Row::new([c.chapter.to_string(), c.title.clone()]));
    let t = Table::new(r, &[Constraint::Length(5), Constraint::Min(20)])
        .header(h)
        .block(styled_block("Confissão de Fé", &app.theme))
        .highlight_style(app.theme.selected_style)
        .highlight_spacing(HighlightSpacing::Always);
    frame.render_stateful_widget(t, area, &mut app.cfw_list_state);
}
fn render_cfw_sections(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let text: String = app
        .cfw_secoes
        .iter()
        .map(|s| format!("{}. {}\n\n", s.section, s.text))
        .collect();
    let title = format!("CFW: {}", app.cfw_capitulo_titulo);
    let p = Paragraph::new(text)
        .wrap(Wrap { trim: false })
        .scroll((app.cfw_scroll, 0))
        .block(styled_block(&title, &app.theme))
        .style(app.theme.base_style);
    frame.render_widget(p, area);
}
fn render_biblia_view(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let txt = if app.biblia_versiculos.is_empty() {
        "\n\n\nUse [e] para buscar.".to_string()
    } else {
        app.biblia_versiculos
            .iter()
            .map(|v| format!("[{}] {}\n", v.verse, v.text))
            .collect()
    };
    let title = format!("Bíblia: {}", app.biblia_referencia);
    let p = Paragraph::new(txt)
        .wrap(Wrap { trim: false })
        .scroll((app.biblia_scroll, 0))
        .block(styled_block(&title, &app.theme))
        .style(app.theme.base_style);
    frame.render_widget(p, area);
}
fn render_cmw_table(app: &mut App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let h = Row::new(["Per.", "Pergunta"]).style(app.theme.header_style);
    let r = app
        .cmw_perguntas
        .iter()
        .map(|p| Row::new([p.id.to_string(), p.question.clone()]));
    let t = Table::new(r, &[Constraint::Length(5), Constraint::Min(20)])
        .header(h)
        .block(styled_block("Catecismo Maior", &app.theme))
        .highlight_style(app.theme.selected_style)
        .highlight_spacing(HighlightSpacing::Always);
    frame.render_stateful_widget(t, area, &mut app.cmw_list_state);
}
fn render_cmw_answer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    if let Some(p) = app.selected_cmw_question() {
        let title = format!("CMW Pergunta {}", p.id);
        let txt = vec![
            Line::from(vec![
                Span::styled("P: ", Style::default().bold().fg(app.theme.yellow)),
                Span::raw(&p.question),
            ]),
            Line::from(""),
            Line::from(vec![
                Span::styled("R: ", Style::default().bold().fg(app.theme.yellow)),
                Span::raw(&p.answer),
            ]),
        ];
        let par = Paragraph::new(txt)
            .wrap(Wrap { trim: true })
            .scroll((app.cmw_scroll, 0))
            .block(styled_block(&title, &app.theme))
            .style(app.theme.base_style);
        frame.render_widget(par, area);
    }
}
fn render_bcw_table(app: &mut App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let h = Row::new(["Per.", "Pergunta"]).style(app.theme.header_style);
    let r = app
        .bcw_perguntas
        .iter()
        .map(|p| Row::new([p.id.to_string(), p.question.clone()]));
    let t = Table::new(r, &[Constraint::Length(5), Constraint::Min(20)])
        .header(h)
        .block(styled_block("Breve Catecismo", &app.theme))
        .highlight_style(app.theme.selected_style)
        .highlight_spacing(HighlightSpacing::Always);
    frame.render_stateful_widget(t, area, &mut app.bcw_list_state);
}
fn render_bcw_answer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    if let Some(p) = app.selected_bcw_question() {
        let title = format!("BCW Pergunta {}", p.id);
        let txt = vec![
            Line::from(vec![
                Span::styled("P: ", Style::default().bold().fg(app.theme.yellow)),
                Span::raw(&p.question),
            ]),
            Line::from(""),
            Line::from(vec![
                Span::styled("R: ", Style::default().bold().fg(app.theme.yellow)),
                Span::raw(&p.answer),
            ]),
        ];
        let par = Paragraph::new(txt)
            .wrap(Wrap { trim: true })
            .scroll((app.cmw_scroll, 0))
            .block(styled_block(&title, &app.theme))
            .style(app.theme.base_style);
        frame.render_widget(par, area);
    }
}
fn render_menu_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("Use os números para selecionar ou [v] para voltar.")
            .block(styled_block("Ajuda", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_salmos_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("[Enter] Ver Letra | [t] Tocar | [c] Cantar | [s] Parar")
            .block(styled_block("Ajuda", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_acoes_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let text = match app.input_mode {
        InputMode::Normal => "[n] Nova | [c] Completar | [p] Pender | [d] Deletar | [v] Voltar",
        InputMode::Editing => "Nova Ação:",
    };
    frame.render_widget(
        Paragraph::new(text)
            .block(styled_block("Comandos", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_resolucoes_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let text = match app.input_mode {
        InputMode::Normal => "[n] Nova | [d] Deletar | [v] Voltar",
        InputMode::Editing => "Nova Resolução:",
    };
    frame.render_widget(
        Paragraph::new(text)
            .block(styled_block("Comandos", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_diario_list_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("[n] Nova Entrada | [Enter] Ver | [v] Voltar")
            .block(styled_block("Ajuda", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_symbols_menu_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("[1], [2], [3] Selecionar | [v] Voltar")
            .block(styled_block("Ajuda", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_list_view_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("[Enter] Ver | [v] Voltar")
            .block(styled_block("Ajuda", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}
fn render_text_view_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    frame.render_widget(
        Paragraph::new("[j/k] Rolar | [v] Voltar")
            .block(styled_block("Ajuda", &app.theme))
            .style(app.theme.base_style),
        area,
    );
}

fn render_biblia_footer(app: &App, frame: &mut Frame, area: ratatui::layout::Rect) {
    let block_title = if matches!(app.input_mode, InputMode::Editing) {
        "Comando"
    } else {
        "Status"
    };

    let (text, style) = match app.input_mode {
        InputMode::Editing => (app.input.as_str(), app.theme.base_style),
        InputMode::Normal => {
            let (status_text, msg_type) = &app.status_message;
            let fg_color = match msg_type {
                MessageType::Success => app.theme.green,
                MessageType::Error => app.theme.red,
                MessageType::Info => app.theme.fg,
            };
            (status_text.as_str(), app.theme.base_style.fg(fg_color))
        }
    };

    let paragraph = Paragraph::new(text)
        .style(style)
        .block(styled_block(block_title, &app.theme));
    frame.render_widget(paragraph, area);
}
