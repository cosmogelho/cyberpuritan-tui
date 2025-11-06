use crate::db::schema::{Bcw, Book, Cfw, Cmw, Salterio, Verse};
use crate::utils::error::AppError;
use rusqlite::Connection;

pub struct CanonRepo { pub conn: Connection }
impl CanonRepo {
    pub fn new() -> Result<Self, AppError> { Ok(Self { conn: Connection::open("./data/canon.db")? }) }
    pub fn get_all_psalms(&self) -> Result<Vec<Salterio>, AppError> { let mut stmt = self.conn.prepare("SELECT id, referencia, metrica, melodia, compositor, harmonizacao, letra, instrumental, `à_capela`, tema FROM salterio ORDER BY CAST(referencia AS INTEGER)")?; let iter = stmt.query_map([], |r| Ok(Salterio { id: r.get(0)?, referencia: r.get(1)?, metrica: r.get(2)?, melodia: r.get(3)?, compositor: r.get(4)?, harmonizacao: r.get(5)?, letra: r.get(6)?, instrumental: r.get(7)?, a_capela: r.get(8)?, tema: r.get(9)? }))?; iter.collect::<Result<_, _>>().map_err(Into::into) }
    pub fn get_all_cfw(&self) -> Result<Vec<Cfw>, AppError> { let mut stmt = self.conn.prepare("SELECT id, chapter, section, title, text FROM cfw")?; let iter = stmt.query_map([], |r| Ok(Cfw { id: r.get(0)?, chapter: r.get(1)?, section: r.get(2)?, title: r.get(3)?, text: r.get(4)? }))?; iter.collect::<Result<_, _>>().map_err(Into::into) }
    pub fn get_all_cmw(&self) -> Result<Vec<Cmw>, AppError> { let mut stmt = self.conn.prepare("SELECT id, question, answer FROM cmw")?; let iter = stmt.query_map([], |r| Ok(Cmw { id: r.get(0)?, question: r.get(1)?, answer: r.get(2)? }))?; iter.collect::<Result<_, _>>().map_err(Into::into) }
    pub fn get_all_bcw(&self) -> Result<Vec<Bcw>, AppError> { let mut stmt = self.conn.prepare("SELECT id, question, answer FROM bcw")?; let iter = stmt.query_map([], |r| Ok(Bcw { id: r.get(0)?, question: r.get(1)?, answer: r.get(2)? }))?; iter.collect::<Result<_, _>>().map_err(Into::into) }
    pub fn get_all_books(&self) -> Result<Vec<Book>, AppError> { let mut stmt = self.conn.prepare("SELECT id, name FROM book")?; let iter = stmt.query_map([], |r| Ok(Book { id: r.get(0)?, name: r.get(1)?, ..Default::default() }))?; iter.collect::<Result<_, _>>().map_err(Into::into) }
    pub fn get_chapters_by_book(&self, book_id: i32) -> Result<Vec<i32>, AppError> { let mut stmt = self.conn.prepare("SELECT DISTINCT chapter FROM verse WHERE book_id = ?1 ORDER BY chapter")?; let iter = stmt.query_map([book_id], |r| r.get(0))?; iter.collect::<Result<Vec<i32>, _>>().map_err(Into::into) }
    pub fn get_verses_by_chapter(&self, book_id: i32, chapter: i32) -> Result<Vec<Verse>, AppError> { let mut stmt = self.conn.prepare("SELECT verse, text FROM verse WHERE book_id = ?1 AND chapter = ?2 ORDER BY verse")?; let iter = stmt.query_map([book_id, chapter], |r| Ok(Verse { verse: r.get(0)?, text: r.get(1)?, ..Default::default() }))?; iter.collect::<Result<_, _>>().map_err(Into::into) }
}
