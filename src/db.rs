use crate::models::{
    Acao, CatecismoPergunta, CfwCapitulo, CfwSecao, DiarioEntrada, EntradaDiarioLegado, Livro,
    OracaoPuritana, PerguntaAutoExame, Resolucao, Salmo, Versiculo,
};
use chrono::Local;
use rusqlite::{Connection, OptionalExtension, Result};
use std::collections::HashMap;

const CANON_DB_PATH: &str = "./data/canon.db";
const PIETY_DB_PATH: &str = "./data/piety.db";

// ==== START PROTECTED BLOCK ====
pub fn listar_salmos() -> Result<Vec<Salmo>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, referencia, melodia, tema, letra, instrumental, \"à_capela\" FROM salterio ORDER BY CAST(referencia AS INTEGER)")?;
    let salmos_iter = stmt.query_map([], |row| {
        Ok(Salmo {
            _id: row.get(0)?,
            referencia: row.get(1)?,
            melodia: row.get(2)?,
            _tema: row.get(3)?,
            letra: row.get(4)?,
            instrumental: row.get(5)?,
            a_capela: row.get(6)?,
        })
    })?;
    Ok(salmos_iter.collect::<Result<Vec<Salmo>>>()?)
}

pub fn listar_capitulos_cfw() -> Result<Vec<CfwCapitulo>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT DISTINCT chapter, title FROM cfw ORDER BY chapter")?;
    let cap_iter = stmt.query_map([], |row| {
        Ok(CfwCapitulo {
            chapter: row.get(0)?,
            title: row.get(1)?,
        })
    })?;
    Ok(cap_iter.collect::<Result<Vec<CfwCapitulo>>>()?)
}

pub fn ler_capitulo_biblia(nome_livro: &str, capitulo: i32) -> Result<Vec<Versiculo>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let book_id: i32 = conn.query_row(
        "SELECT id FROM book WHERE lower(name) = lower(?1)",
        [nome_livro],
        |row| row.get(0),
    )?;
    let mut stmt = conn.prepare("SELECT verse, text FROM verse WHERE book_id = ?1 AND chapter = ?2 AND version = 'ARA' ORDER BY verse")?;
    let verse_iter = stmt.query_map([book_id, capitulo], |row| {
        Ok(Versiculo {
            verse: row.get(0)?,
            text: row.get(1)?,
        })
    })?;
    Ok(verse_iter.collect::<Result<Vec<Versiculo>>>()?)
}

pub fn ler_secoes_cfw(numero_capitulo: i32) -> Result<Vec<CfwSecao>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt =
        conn.prepare("SELECT section, text FROM cfw WHERE chapter = ? ORDER BY section")?;
    let secoes_iter = stmt.query_map([numero_capitulo], |row| {
        Ok(CfwSecao {
            section: row.get(0)?,
            text: row.get(1)?,
        })
    })?;
    Ok(secoes_iter.collect::<Result<Vec<CfwSecao>>>()?)
}

pub fn listar_perguntas_cmw() -> Result<Vec<CatecismoPergunta>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, question, answer FROM cmw ORDER BY id")?;
    let iter = stmt.query_map([], |row| {
        Ok(CatecismoPergunta {
            id: row.get(0)?,
            question: row.get(1)?,
            answer: row.get(2)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<CatecismoPergunta>>>()?)
}

pub fn listar_perguntas_bcw() -> Result<Vec<CatecismoPergunta>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, question, answer FROM bcw ORDER BY id")?;
    let iter = stmt.query_map([], |row| {
        Ok(CatecismoPergunta {
            id: row.get(0)?,
            question: row.get(1)?,
            answer: row.get(2)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<CatecismoPergunta>>>()?)
}

pub fn listar_entradas_diario() -> Result<Vec<EntradaDiarioLegado>> {
    // Esta função agora se refere ao sistema legado e pode ser removida futuramente.
    let conn = Connection::open(PIETY_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, data, texto FROM diario ORDER BY data DESC")?;
    let iter = stmt.query_map([], |row| {
        Ok(EntradaDiarioLegado {
            _id: row.get(0)?,
            data: row.get(1)?,
            texto: row.get(2)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<EntradaDiarioLegado>>>()?)
}

pub fn criar_entrada_diario(texto: &str) -> Result<()> {
    // Esta função agora se refere ao sistema legado e pode ser removida futuramente.
    let conn = Connection::open(PIETY_DB_PATH)?;
    let data_atual = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    conn.execute(
        "INSERT INTO diario (data, texto) VALUES (?1, ?2)",
        (data_atual, texto),
    )?;
    Ok(())
}

pub fn listar_acoes() -> Result<Vec<Acao>> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let mut stmt =
        conn.prepare("SELECT id, descricao, status FROM acoes ORDER BY status, id DESC")?;
    let iter = stmt.query_map([], |row| {
        Ok(Acao {
            id: row.get(0)?,
            descricao: row.get(1)?,
            status: row.get(2)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<Acao>>>()?)
}

pub fn criar_acao(descricao: &str) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let data_atual = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    conn.execute(
        "INSERT INTO acoes (descricao, data_criacao) VALUES (?1, ?2)",
        (descricao, data_atual),
    )?;
    Ok(())
}

pub fn atualizar_status_acao(id: i32, status: &str) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    conn.execute("UPDATE acoes SET status = ?1 WHERE id = ?2", (status, id))?;
    Ok(())
}

pub fn deletar_acao(id: i32) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    conn.execute("DELETE FROM acoes WHERE id = ?1", [id])?;
    Ok(())
}

pub fn listar_resolucoes() -> Result<Vec<Resolucao>> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, texto FROM resolucoes ORDER BY id DESC")?;
    let iter = stmt.query_map([], |row| {
        Ok(Resolucao {
            id: row.get(0)?,
            texto: row.get(1)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<Resolucao>>>()?)
}

pub fn criar_resolucao(texto: &str) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let data_atual = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    conn.execute(
        "INSERT INTO resolucoes (texto, data_criacao) VALUES (?1, ?2)",
        (texto, data_atual),
    )?;
    Ok(())
}

pub fn deletar_resolucao(id: i32) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    conn.execute("DELETE FROM resolucoes WHERE id = ?1", [id])?;
    Ok(())
}

pub fn listar_livros() -> Result<Vec<Livro>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, name FROM book ORDER BY id")?;
    let iter = stmt.query_map([], |row| {
        Ok(Livro {
            id: row.get(0)?,
            name: row.get(1)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<_>>>()?)
}

pub fn contar_capitulos(book_id: i32) -> Result<i32> {
    let conn = Connection::open(CANON_DB_PATH)?;
    conn.query_row(
        "SELECT MAX(chapter) FROM verse WHERE book_id = ?1",
        [book_id],
        |row| row.get(0),
    )
}
// ==== END PROTECTED BLOCK ====

pub fn listar_oracoes() -> Result<Vec<OracaoPuritana>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, titulo, texto_completo FROM oracoes_puritanas ORDER BY id")?;
    let iter = stmt.query_map([], |row| {
        Ok(OracaoPuritana {
            id: row.get(0)?,
            titulo: row.get(1)?,
            texto_completo: row.get(2)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<_>>>()?)
}

pub fn listar_perguntas_padrao(categoria: &str) -> Result<Vec<PerguntaAutoExame>> {
    let conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, categoria, texto_pergunta FROM perguntas_auto_exame WHERE categoria = ?1")?;
    let iter = stmt.query_map([categoria], |row| {
        Ok(PerguntaAutoExame {
            id: row.get(0)?,
            categoria: row.get(1)?,
            texto: row.get(2)?,
            is_user_defined: false,
            is_active: true,
        })
    })?;
    Ok(iter.collect::<Result<Vec<_>>>()?)
}

pub fn listar_perguntas_usuario(categoria: &str) -> Result<Vec<PerguntaAutoExame>> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, categoria, texto_pergunta, is_active FROM perguntas_usuario WHERE categoria = ?1")?;
    let iter = stmt.query_map([categoria], |row| {
        Ok(PerguntaAutoExame {
            id: row.get(0)?,
            categoria: row.get(1)?,
            texto: row.get(2)?,
            is_user_defined: true,
            is_active: row.get(3)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<_>>>()?)
}

pub fn criar_pergunta_usuario(categoria: &str, texto: &str) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    conn.execute(
        "INSERT INTO perguntas_usuario (categoria, texto_pergunta, is_active) VALUES (?1, ?2, 1)",
        (categoria, texto),
    )?;
    Ok(())
}

pub fn atualizar_pergunta_usuario(id: i32, texto: &str) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    conn.execute("UPDATE perguntas_usuario SET texto_pergunta = ?1 WHERE id = ?2", (texto, id))?;
    Ok(())
}

pub fn desativar_pergunta_padrao(categoria: &str, texto: &str) -> Result<()> {
    let mut conn = Connection::open(PIETY_DB_PATH)?;
    let tx = conn.transaction()?;
    tx.execute(
        "INSERT INTO perguntas_usuario (categoria, texto_pergunta, is_active) VALUES (?1, ?2, 0)",
        (categoria, texto),
    )?;
    tx.commit()
}

pub fn alternar_estado_pergunta_usuario(id: i32, is_active: bool) -> Result<()> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    conn.execute("UPDATE perguntas_usuario SET is_active = ?1 WHERE id = ?2", (is_active, id))?;
    Ok(())
}

pub fn obter_estado_pergunta_padrao(texto: &str) -> Result<Option<bool>> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    conn.query_row(
        "SELECT is_active FROM perguntas_usuario WHERE texto_pergunta = ?1",
        [texto],
        |row| row.get(0),
    ).optional()
}

pub fn get_pergunta_texto_por_id(id: i32) -> Result<String> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT texto_pergunta FROM perguntas_usuario WHERE id = ?1")?;
    if let Some(res) = stmt.query_map([id], |row| row.get(0))?.next() { return res; }
    
    let canon_conn = Connection::open(CANON_DB_PATH)?;
    let mut stmt = canon_conn.prepare("SELECT texto_pergunta FROM perguntas_auto_exame WHERE id = ?1")?;
    stmt.query_row([id], |row| row.get(0))
}

pub fn get_sermao_details(id: i32) -> Result<Option<crate::models::SermaoDetail>> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT pregador, titulo, passagens, pontos_chave, aplicacao_pessoal FROM entradas_sermoes WHERE id = ?1")?;
    /* `query_map` devolve um iterator; precisamos usar `?` antes de chamar `next()`. */
    let rows = stmt.query_map([id], |row| {
        Ok(crate::models::SermaoDetail {
            pregador: row.get(0)?,
            titulo: row.get(1)?,
            passagens: row.get(2)?,
            pontos_chave: row.get(3)?,
            aplicacao_pessoal: row.get(4)?,
        })
    })?;
    Ok(rows.next().transpose()?)
}
    }).next().transpose()
}

pub fn get_autoexame_details(id: i32) -> Result<Option<crate::models::AutoExameDetail>> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let passo_pratico: String = conn.query_row("SELECT passo_pratico FROM diario_entradas WHERE id = ?1", [id], |row| row.get(0))?;
    let respostas_json: String = conn.query_row("SELECT respostas FROM entradas_auto_exame WHERE id = ?1", [id], |row| row.get(0))?;
    let respostas_parsed: Vec<crate::models::RespostaJson> = serde_json::from_str(&respostas_json).unwrap_or_default();
    let mut respostas_details = Vec::new();
    for r in respostas_parsed {
        let texto = get_pergunta_texto_por_id(r.id).unwrap_or_else(|_| "Pergunta não encontrada".to_string());
        respostas_details.push(crate::models::RespostaDetail {
            pergunta_texto: texto,
            avaliacao: r.avaliacao,
        });
    }
    Ok(Some(crate::models::AutoExameDetail {
        respostas: respostas_details,
        passo_pratico,
    }))
}

pub fn get_entradas_diario_range(start_date: &str, end_date: &str) -> Result<Vec<DiarioEntrada>> {
    let conn = Connection::open(PIETY_DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, data, tipo, passo_pratico FROM diario_entradas WHERE data BETWEEN ?1 AND ?2 ORDER BY data DESC")?;
    let iter = stmt.query_map((start_date, end_date), |row| {
        let tipo: String = row.get(2)?;
        let resumo: String = match tipo.as_str() {
            "SERMAO" => "Nota de Sermão".to_string(),
            "AUTO_EXAME" => "Autoexame Realizado".to_string(),
            "JEJUM" => "Dia de Jejum".to_string(),
            _ => row.get::<_, Option<String>>(3)?.unwrap_or_else(|| tipo.clone()),
        };
        Ok(DiarioEntrada {
            id: row.get(0)?,
            data: row.get(1)?,
            tipo,
            resumo,
        })
    })?;
    iter.collect::<Result<Vec<_>>>()
}

// --- Funções de Criação de Entradas do Diário ---
fn criar_entrada_base(conn: &Connection, tipo: &str, passo_pratico: Option<&str>, tags: Option<&str>) -> Result<i64> {
    let data_atual = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    let mut stmt = conn.prepare("INSERT INTO diario_entradas (data, tipo, passo_pratico, tags) VALUES (?1, ?2, ?3, ?4)")?;
    stmt.insert((data_atual, tipo, passo_pratico, tags))
}

pub fn criar_entrada_auto_exame(respostas_json: &str, passo_pratico: &str) -> Result<()> {
    let mut conn = Connection::open(PIETY_DB_PATH)?;
    let tx = conn.transaction()?;
    let entrada_id = criar_entrada_base(&tx, "AUTO_EXAME", Some(passo_pratico), None)?;
    tx.execute("INSERT INTO entradas_auto_exame (id, respostas) VALUES (?1, ?2)",
        rusqlite::params![entrada_id, respostas_json])?;
    tx.commit()
}

pub fn criar_entrada_sermao(pregador: &str, titulo: &str, passagens: &str, pontos_chave: &str, aplicacao: &str) -> Result<()> {
    let mut conn = Connection::open(PIETY_DB_PATH)?;
    let tx = conn.transaction()?;
    let entrada_id = criar_entrada_base(&tx, "SERMAO", None, None)?;
    tx.execute("INSERT INTO entradas_sermoes (id, pregador, titulo, passagens, pontos_chave, aplicacao_pessoal) VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        (entrada_id, pregador, titulo, passagens, pontos_chave, aplicacao))?;
    tx.commit()
}

pub fn criar_entrada_resolucao(texto: &str, objetivo: &str, metrica: &str) -> Result<()> {
    let mut conn = Connection::open(PIETY_DB_PATH)?;
    let tx = conn.transaction()?;
    let entrada_id = criar_entrada_base(&tx, "RESOLUCAO", Some(objetivo), None)?;
    tx.execute("INSERT INTO entradas_resolucoes (id, texto_resolucao, objetivo_concreto, metrica) VALUES (?1, ?2, ?3, ?4)",
        (entrada_id, texto, objetivo, metrica))?;
    tx.commit()
}

pub fn criar_entrada_jejum(tipo: &str, proposito: &str, observacoes: &str) -> Result<()> {
    let mut conn = Connection::open(PIETY_DB_PATH)?;
    let tx = conn.transaction()?;
    let entrada_id = criar_entrada_base(&tx, "JEJUM", None, None)?;
    tx.execute("INSERT INTO entradas_jejum (id, tipo_jejum, proposito, observacoes) VALUES (?1, ?2, ?3, ?4)",
        (entrada_id, tipo, proposito, observacoes))?;
    tx.commit()
}

pub fn criar_entrada_leitura(tema: &str, passagens: &str, salmo: &str, aplicacao: &str) -> Result<()> {
    let mut conn = Connection::open(PIETY_DB_PATH)?;
    let tx = conn.transaction()?;
    let entrada_id = criar_entrada_base(&tx, "LEITURA", Some(aplicacao), None)?;
    tx.execute("INSERT INTO entradas_leitura_biblica (id, tema_semanal, passagens_lidas, salmo_do_dia, aplicacao) VALUES (?1, ?2, ?3, ?4, ?5)",
        (entrada_id, tema, passagens, salmo, aplicacao))?;
    tx.commit()
}

pub fn criar_entrada_evangelismo(tipo_contato: &str, resultado: &str, observacao: &str) -> Result<()> {
    let mut conn = Connection::open(PIETY_DB_PATH)?;
    let tx = conn.transaction()?;
    let entrada_id = criar_entrada_base(&tx, "EVANGELISMO", None, None)?;
    tx.execute("INSERT INTO entradas_evangelismo (id, tipo_contato, resultado, observacao) VALUES (?1, ?2, ?3, ?4)",
        (entrada_id, tipo_contato, resultado, observacao))?;
    tx.commit()
}
