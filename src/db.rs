use crate::models::{
    Acao, CatecismoPergunta, CfwCapitulo, CfwSecao, EntradaDiario, Resolucao, Salmo, Versiculo,
};
use chrono::Local;
use rusqlite::{Connection, Result};
const DB_PATH: &str = "./data/dados.db";

pub fn listar_salmos() -> Result<Vec<Salmo>> {
    let conn = Connection::open(DB_PATH)?;
    // CORREÇÃO: Adiciona a coluna `letra` à consulta SQL.
    let mut stmt = conn.prepare("SELECT id, referencia, melodia, tema, letra, instrumental, \"à_capela\" FROM salterio ORDER BY CAST(referencia AS INTEGER)")?;
    let salmos_iter = stmt.query_map([], |row| {
        Ok(Salmo {
            id: row.get(0)?,
            referencia: row.get(1)?,
            melodia: row.get(2)?,
            tema: row.get(3)?,
            letra: row.get(4)?,
            instrumental: row.get(5)?,
            a_capela: row.get(6)?,
        })
    })?;
    Ok(salmos_iter.collect::<Result<Vec<Salmo>>>()?)
}
// ... resto do arquivo db.rs sem alterações ...
pub fn listar_capitulos_cfw() -> Result<Vec<CfwCapitulo>> {
    let conn = Connection::open(DB_PATH)?;
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
    let conn = Connection::open(DB_PATH)?;
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
    let conn = Connection::open(DB_PATH)?;
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
    let conn = Connection::open(DB_PATH)?;
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
    let conn = Connection::open(DB_PATH)?;
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
pub fn listar_entradas_diario() -> Result<Vec<EntradaDiario>> {
    let conn = Connection::open(DB_PATH)?;
    let mut stmt = conn.prepare("SELECT id, data, texto FROM diario ORDER BY data DESC")?;
    let iter = stmt.query_map([], |row| {
        Ok(EntradaDiario {
            id: row.get(0)?,
            data: row.get(1)?,
            texto: row.get(2)?,
        })
    })?;
    Ok(iter.collect::<Result<Vec<EntradaDiario>>>()?)
}
pub fn criar_entrada_diario(texto: &str) -> Result<()> {
    let conn = Connection::open(DB_PATH)?;
    let data_atual = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    conn.execute(
        "INSERT INTO diario (data, texto) VALUES (?1, ?2)",
        (data_atual, texto),
    )?;
    Ok(())
}
pub fn listar_acoes() -> Result<Vec<Acao>> {
    let conn = Connection::open(DB_PATH)?;
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
    let conn = Connection::open(DB_PATH)?;
    let data_atual = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    conn.execute(
        "INSERT INTO acoes (descricao, data_criacao) VALUES (?1, ?2)",
        (descricao, data_atual),
    )?;
    Ok(())
}
pub fn atualizar_status_acao(id: i32, status: &str) -> Result<()> {
    let conn = Connection::open(DB_PATH)?;
    conn.execute("UPDATE acoes SET status = ?1 WHERE id = ?2", (status, id))?;
    Ok(())
}
pub fn deletar_acao(id: i32) -> Result<()> {
    let conn = Connection::open(DB_PATH)?;
    conn.execute("DELETE FROM acoes WHERE id = ?1", [id])?;
    Ok(())
}
pub fn listar_resolucoes() -> Result<Vec<Resolucao>> {
    let conn = Connection::open(DB_PATH)?;
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
    let conn = Connection::open(DB_PATH)?;
    let data_atual = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    conn.execute(
        "INSERT INTO resolucoes (texto, data_criacao) VALUES (?1, ?2)",
        (texto, data_atual),
    )?;
    Ok(())
}
pub fn deletar_resolucao(id: i32) -> Result<()> {
    let conn = Connection::open(DB_PATH)?;
    conn.execute("DELETE FROM resolucoes WHERE id = ?1", [id])?;
    Ok(())
}
