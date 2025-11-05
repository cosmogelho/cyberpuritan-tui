use rusqlite::{Connection, Result};

const DB_PATH: &str = "./data/dados.db";

fn main() -> Result<()> {
    let conn = Connection::open(DB_PATH)?;

    // --- 1. Lista os nomes dos livros ---
    println!("--- Livros Disponíveis no Banco de Dados ---");
    let mut stmt_books = conn.prepare("SELECT name FROM book ORDER BY id")?;
    let book_iter = stmt_books.query_map([], |row| row.get::<_, String>(0))?;

    for book in book_iter {
        println!("{}", book?);
    }

    // --- 2. Lista as versões da Bíblia ---
    println!("\n--- Versões da Bíblia Disponíveis ---");
    let mut stmt_versions = conn.prepare("SELECT DISTINCT version FROM verse")?;
    let version_iter = stmt_versions.query_map([], |row| row.get::<_, String>(0))?;

    for version in version_iter {
        println!("{}", version?);
    }

    Ok(())
}
