#[derive(Debug, Clone, Default)] pub struct Salterio { pub id: i32, pub referencia: String, pub metrica: Option<String>, pub melodia: Option<String>, pub compositor: Option<String>, pub harmonizacao: Option<String>, pub letra: String, pub instrumental: Option<String>, pub a_capela: Option<String>, pub tema: Option<String>, }
#[derive(Debug, Clone, Default)] pub struct Acoes { pub id: i32, pub descricao: String, pub status: String, pub data_criacao: String, }
#[derive(Debug, Clone, Default)] pub struct Resolucoes { pub id: i32, pub texto: String, pub data_criacao: String, }
#[derive(Debug, Clone, Default)] pub struct Diario { pub id: i32, pub data: String, pub texto: String, }
#[derive(Debug, Clone, Default)] pub struct Cfw { pub id: i32, pub chapter: i32, pub section: i32, pub title: String, pub text: String, }
#[derive(Debug, Clone, Default)] pub struct Cmw { pub id: i32, pub question: String, pub answer: String, }
#[derive(Debug, Clone, Default)] pub struct Bcw { pub id: i32, pub question: String, pub answer: String, }
#[derive(Debug, Clone, Default)] pub struct Book { pub id: i32, pub book_reference_id: i32, pub testament_reference_id: i32, pub name: String, }
#[derive(Debug, Clone, Default)] pub struct Verse { pub id: i32, pub book_id: i32, pub chapter: i32, pub verse: i32, pub text: String, pub version: String, }
