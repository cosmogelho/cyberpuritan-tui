use crate::app::{App, BiblePane, CfwPane, View};
use crate::ui::theme::get_theme;
use ratatui::{prelude::*, widgets::*};

pub fn ui(f: &mut Frame, app: &mut App) {
    let theme = get_theme();
    let chunks_main = Layout::new(Direction::Vertical, [Constraint::Min(0), Constraint::Length(3)]).split(f.size());
    let chunks_content = Layout::new(Direction::Horizontal, [Constraint::Length(20), Constraint::Min(0)]).split(chunks_main[0]);
    f.render_widget(Block::default().style(theme), f.size());
    render_navigation_menu(f, theme, chunks_content[0]);
    if let Some(view) = app.view_stack.last() {
        let area = chunks_content[1];
        match view {
            View::PsalmList => { let r=app.salmos.iter().map(|s|Row::new(vec![s.referencia.clone(),s.melodia.clone().unwrap_or_default()])).collect::<Vec<_>>();render_table(f,theme,area,"Saltério",&["Ref.","Melodia"],&r,&mut app.psalm_list_state);},
            View::PsalmDetail => render_psalm_detail(f, app, theme, area),
            View::PietyMenu => render_menu(f, theme, area, "Piedade", &["[1] Ações", "[2] Resoluções", "[3] Diário"]),
            View::ActionList => { let r=app.acoes.iter().map(|a|Row::new(vec![a.descricao.clone(),a.status.clone()])).collect::<Vec<_>>();render_table(f,theme,area,"Ações",&["Desc.","Status"],&r,&mut app.action_list_state);},
            View::ResolutionList => { let r=app.resolucoes.iter().map(|res|Row::new(vec![res.texto.clone()])).collect::<Vec<_>>();render_table(f,theme,area,"Resoluções",&["Texto"],&r,&mut app.resolution_list_state);},
            View::DiarioList => { let r=app.diario.iter().map(|d|Row::new(vec![d.data.clone(),d.texto.clone()])).collect::<Vec<_>>();render_table(f,theme,area,"Diário",&["Data","Texto"],&r,&mut app.diario_list_state);},
            View::StudyMenu => render_menu(f, theme, area, "Estudo", &["[1] Símbolos", "[2] Bíblia"]),
            View::FaithSymbolsMenu => render_menu(f, theme, area, "Símbolos", &["[1] Confissão", "[2] Cat. Maior", "[3] Breve Cat."]),
            View::ConfessionView => render_cfw_view(f, app, theme, area),
            View::LargerCatechismView => { let r=app.cmw.iter().map(|c|Row::new(vec![c.id.to_string(),c.question.clone()])).collect::<Vec<_>>();render_table(f,theme,area,"Cat. Maior",&["ID","Pergunta"],&r,&mut app.cmw_list_state);},
            View::ShorterCatechismView => { let r=app.bcw.iter().map(|b|Row::new(vec![b.id.to_string(),b.question.clone()])).collect::<Vec<_>>();render_table(f,theme,area,"Breve Cat.",&["ID","Pergunta"],&r,&mut app.bcw_list_state);},
            View::ConfessionDetail => render_cfw_detail(f, app, theme, area),
            View::LargerCatechismDetail => render_cmw_detail(f, app, theme, area),
            View::ShorterCatechismDetail => render_bcw_detail(f, app, theme, area),
            View::BibleView => render_bible_view(f, app, theme, area),
            View::ActionEdit{text,..}|View::ResolutionEdit{text,..}|View::DiarioEdit{text,..} => render_input(f, theme, area, "Editar", text),
        }
    }
    render_footer(f, app, theme, chunks_main[1]);
}
fn render_input(f:&mut Frame,style:Style,area:Rect,title:&str,text:&str){let p=Paragraph::new(text).block(Block::default().borders(Borders::ALL).title(title).style(style));f.render_widget(p,area);f.set_cursor(area.x+text.len()as u16+1,area.y+1);}
fn render_navigation_menu(f:&mut Frame,style:Style,area:Rect){let i=vec!["[1] Canto","[2] Piedade","[3] Estudo"].into_iter().map(ListItem::new).collect::<Vec<_>>();f.render_widget(List::new(i).block(Block::default().borders(Borders::ALL).title("Menu").style(style)),area);}
fn render_menu(f:&mut Frame,style:Style,area:Rect,title:&str,items:&[&str]){f.render_widget(Paragraph::new(items.join("\n")).block(Block::default().borders(Borders::ALL).title(title).style(style)),area);}
fn render_table(f:&mut Frame,style:Style,area:Rect,title:&str,header:&[&str],rows:&[Row],state:&mut TableState){let w=(0..header.len()).map(|_|Constraint::Ratio(1,header.len()as u32)).collect::<Vec<_>>();f.render_stateful_widget(Table::new(rows.to_vec(),w).header(Row::new(header.to_vec()).style(Style::new().add_modifier(Modifier::BOLD))).block(Block::default().borders(Borders::ALL).title(title).style(style)).highlight_style(Style::new().add_modifier(Modifier::REVERSED)),area,state);}
fn render_psalm_detail(f:&mut Frame,app:&App,style:Style,area:Rect){let t=if let Some(s)=app.psalm_list_state.selected(){app.salmos[s].letra.clone()}else{String::new()};f.render_widget(Paragraph::new(t).wrap(Wrap{trim:true}).block(Block::default().borders(Borders::ALL).title("Letra").style(style)),area);}
fn render_cfw_detail(f: &mut Frame, app: &App, style: Style, area: Rect) {
    let text = if let Some(sel) = app.cfw_state.section_list_state.selected() {
        let section = &app.cfw_state.sections[sel];
        format!("[{}.{}] {}\n\n{}", section.chapter, section.section, section.title, section.text)
    } else { String::new() };
    f.render_widget(Paragraph::new(text).wrap(Wrap { trim: true }).block(Block::default().borders(Borders::ALL).title("Confissão de Fé").style(style)), area);
}
fn render_cmw_detail(f:&mut Frame,app:&App,style:Style,area:Rect){let t=if let Some(s)=app.cmw_list_state.selected(){format!("P: {}\n\nR: {}",app.cmw[s].question,app.cmw[s].answer)}else{String::new()};f.render_widget(Paragraph::new(t).wrap(Wrap{trim:true}).block(Block::default().borders(Borders::ALL).title("Cat. Maior").style(style)),area);}
fn render_bcw_detail(f:&mut Frame,app:&App,style:Style,area:Rect){let t=if let Some(s)=app.bcw_list_state.selected(){format!("P: {}\n\nR: {}",app.bcw[s].question,app.bcw[s].answer)}else{String::new()};f.render_widget(Paragraph::new(t).wrap(Wrap{trim:true}).block(Block::default().borders(Borders::ALL).title("Breve Cat.").style(style)),area);}
fn render_bible_view(f:&mut Frame,app:&mut App,style:Style,area:Rect){let chunks=Layout::new(Direction::Horizontal,[Constraint::Percentage(30),Constraint::Percentage(15),Constraint::Percentage(55)]).split(area);let active=Style::new().add_modifier(Modifier::REVERSED);let books:Vec<ListItem>=app.books.iter().map(|b|ListItem::new(b.name.clone())).collect();let mut book_b=Block::default().borders(Borders::ALL).title("Livros").style(style);if app.bible_state.active_pane==BiblePane::Books{book_b=book_b.border_style(active);}f.render_stateful_widget(List::new(books).block(book_b).highlight_style(active),chunks[0],&mut app.bible_state.book_list_state);let chaps:Vec<ListItem>=app.bible_state.chapters.iter().map(|c|ListItem::new(c.to_string())).collect();let mut chap_b=Block::default().borders(Borders::ALL).title("Cap.").style(style);if app.bible_state.active_pane==BiblePane::Chapters{chap_b=chap_b.border_style(active);}f.render_stateful_widget(List::new(chaps).block(chap_b).highlight_style(active),chunks[1],&mut app.bible_state.chapter_list_state);let verses:Vec<Line>=app.bible_state.verses.iter().map(|v|Line::from(format!("{} {}",v.verse,v.text))).collect();let mut text_b=Block::default().borders(Borders::ALL).title("Texto").style(style);if app.bible_state.active_pane==BiblePane::Text{text_b=text_b.border_style(active);}f.render_widget(Paragraph::new(Text::from(verses)).block(text_b).wrap(Wrap{trim:true}).scroll((app.bible_state.text_scroll,0)),chunks[2]);}
fn render_cfw_view(f: &mut Frame, app: &mut App, style: Style, area: Rect) {
    let chunks = Layout::new(Direction::Horizontal, [Constraint::Percentage(25), Constraint::Percentage(75)]).split(area);
    let active = Style::new().add_modifier(Modifier::REVERSED);

    let chapters: Vec<ListItem> = app.cfw_state.chapters.iter().map(|c| ListItem::new(format!("Cap. {}", c))).collect();
    let mut chap_block = Block::default().borders(Borders::ALL).title("Capítulos").style(style);
    if app.cfw_state.active_pane == CfwPane::Chapters { chap_block = chap_block.border_style(active); }
    f.render_stateful_widget(List::new(chapters).block(chap_block).highlight_style(active), chunks[0], &mut app.cfw_state.chapter_list_state);

    let sections: Vec<ListItem> = app.cfw_state.sections.iter().map(|s| ListItem::new(format!("{}. {}", s.section, s.title))).collect();
    let mut sec_block = Block::default().borders(Borders::ALL).title("Seções").style(style);
    if app.cfw_state.active_pane == CfwPane::Sections { sec_block = sec_block.border_style(active); }
    f.render_stateful_widget(List::new(sections).block(sec_block).highlight_style(active), chunks[1], &mut app.cfw_state.section_list_state);
}
fn render_footer(f:&mut Frame,app:&App,style:Style,area:Rect){let text=match app.view_stack.last(){Some(View::PsalmList)=>"[j/k] Mover | [Enter] Letra | [s] Parar | [t/c] Tocar | [1/2/3] Módulos",Some(View::PietyMenu)|Some(View::StudyMenu)|Some(View::FaithSymbolsMenu)=>"[1/2/3] Selecionar | [Esc] Voltar",Some(View::BibleView)|Some(View::ConfessionView)=> "[j/k] Mover/Scroll | [l/Tab] Painel | [Enter] Sel. | [Esc] Voltar",Some(View::ActionList)|Some(View::ResolutionList)|Some(View::DiarioList)=> "[n] Novo | [d] Del | [Enter] Editar | [j/k] Mover | [Esc] Voltar",Some(View::ActionEdit{..})|Some(View::ResolutionEdit{..})|Some(View::DiarioEdit{..})=>"[Enter] Salvar | [Esc] Cancelar",_=>"[j/k] Mover | [Enter] Detalhes | [Esc] Voltar | [q] Sair"};f.render_widget(Paragraph::new(text).block(Block::default().borders(Borders::ALL).title("Ajuda").style(style)),area);}
