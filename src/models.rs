/// Representa um único registro da tabela 'salterio'.
#[derive(Clone, Debug)]
pub struct Salmo {
    pub id: i32,
    pub referencia: String,
    pub melodia: Option<String>,
    pub tema: Option<String>,
    pub letra: Option<String>, // Campo para a letra completa
    pub instrumental: Option<String>,
    pub a_capela: Option<String>,
}

/// Representa uma ação de santificação.
#[derive(Clone, Debug)]
pub struct Acao {
    pub id: i32,
    pub descricao: String,
    pub status: String,
}

/// Representa uma resolução pessoal.
#[derive(Clone, Debug)]
pub struct Resolucao {
    pub id: i32,
    pub texto: String,
}

/// Representa uma entrada do diário.
#[derive(Clone, Debug)]
pub struct EntradaDiario {
    pub id: i32,
    pub data: String,
    pub texto: String,
}

/// Representa um capítulo da Confissão de Fé de Westminster.
#[derive(Clone, Debug)]
pub struct CfwCapitulo {
    pub chapter: i32,
    pub title: String,
}

/// Representa uma seção de um capítulo da CFW.
#[derive(Clone, Debug)]
pub struct CfwSecao {
    pub section: i32,
    pub text: String,
}

/// Representa uma pergunta e resposta de um catecismo.
#[derive(Clone, Debug)]
pub struct CatecismoPergunta {
    pub id: i32,
    pub question: String,
    pub answer: String,
}

/// Representa um único versículo da Bíblia.
#[derive(Clone, Debug)]
pub struct Versiculo {
    pub verse: i32,
    pub text: String,
}
