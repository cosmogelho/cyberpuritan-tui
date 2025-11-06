use crate::db::schema::{Acoes, Diario, Resolucoes};
use crate::utils::error::AppError;
use chrono::Utc;
use rusqlite::Connection;

pub struct PietyRepo { pub conn: Connection }
impl PietyRepo {
    pub fn new() -> Result<Self, AppError> { Ok(Self { conn: Connection::open("./data/piety.db")? }) }
    pub fn get_all_acoes(&self) -> Result<Vec<Acoes>, AppError> { let mut s = self.conn.prepare("SELECT id, descricao, status, data_criacao FROM acoes")?; let i = s.query_map([], |r| Ok(Acoes{id:r.get(0)?,descricao:r.get(1)?,status:r.get(2)?,data_criacao:r.get(3)?}))?; i.collect::<Result<_,_>>().map_err(Into::into) }
    pub fn create_acao(&self, d: &str) -> Result<(), AppError> { self.conn.execute("INSERT INTO acoes (descricao, status, data_criacao) VALUES (?1, 'Pendente', ?2)", &[d, &Utc::now().to_string()])?; Ok(()) }
    pub fn update_acao(&self, id: i32, d: &str) -> Result<(), AppError> { self.conn.execute("UPDATE acoes SET descricao = ?1 WHERE id = ?2", &[d, &id.to_string()])?; Ok(()) }
    pub fn update_acao_status(&self, id: i32, s: &str) -> Result<(), AppError> { self.conn.execute("UPDATE acoes SET status = ?1 WHERE id = ?2", &[s, &id.to_string()])?; Ok(()) }
    pub fn delete_acao(&self, id: i32) -> Result<(), AppError> { self.conn.execute("DELETE FROM acoes WHERE id = ?1", &[&id])?; Ok(()) }
    pub fn get_all_resolucoes(&self) -> Result<Vec<Resolucoes>, AppError> { let mut s = self.conn.prepare("SELECT id, texto, data_criacao FROM resolucoes")?; let i = s.query_map([], |r| Ok(Resolucoes{id:r.get(0)?,texto:r.get(1)?,data_criacao:r.get(2)?}))?; i.collect::<Result<_,_>>().map_err(Into::into) }
    pub fn create_resolucao(&self, t: &str) -> Result<(), AppError> { self.conn.execute("INSERT INTO resolucoes (texto, data_criacao) VALUES (?1, ?2)", &[t, &Utc::now().to_string()])?; Ok(()) }
    pub fn update_resolucao(&self, id: i32, t: &str) -> Result<(), AppError> { self.conn.execute("UPDATE resolucoes SET texto = ?1 WHERE id = ?2", &[t, &id.to_string()])?; Ok(()) }
    pub fn delete_resolucao(&self, id: i32) -> Result<(), AppError> { self.conn.execute("DELETE FROM resolucoes WHERE id = ?1", &[&id])?; Ok(()) }
    pub fn get_all_diario(&self) -> Result<Vec<Diario>, AppError> { let mut s = self.conn.prepare("SELECT id, data, texto FROM diario")?; let i = s.query_map([], |r| Ok(Diario{id:r.get(0)?,data:r.get(1)?,texto:r.get(2)?}))?; i.collect::<Result<_,_>>().map_err(Into::into) }
    pub fn create_diario(&self, t: &str) -> Result<(), AppError> { self.conn.execute("INSERT INTO diario (data, texto) VALUES (?1, ?2)", &[&Utc::now().to_string(), t])?; Ok(()) }
    pub fn update_diario(&self, id: i32, t: &str) -> Result<(), AppError> { self.conn.execute("UPDATE diario SET texto = ?1 WHERE id = ?2", &[t, &id.to_string()])?; Ok(()) }
    pub fn delete_diario(&self, id: i32) -> Result<(), AppError> { self.conn.execute("DELETE FROM diario WHERE id = ?1", &[&id])?; Ok(()) }
}
