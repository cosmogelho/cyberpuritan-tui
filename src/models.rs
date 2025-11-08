use serde::{Deserialize, Serialize};

/// Estruturas para a visualização detalhada de cada tipo de entrada.
#[derive(Debug)]
pub struct SermaoDetail {
    pub pregador: String,
    pub titulo: String,
    pub passagens: String,
    pub pontos_chave: String,
    pub aplicacao_pessoal: String,
}
#[derive(Debug, Deserialize, Serialize)]
pub struct RespostaJson {
    pub id: i32,
    #[serde(rename = "eval")]
    pub avaliacao: String,
}
#[derive(Debug)]
pub struct RespostaDetail {
    pub pergunta_texto: String,
    pub avaliacao: String,
}
#[derive(Debug)]
pub struct AutoExameDetail {
    pub respostas: Vec<RespostaDetail>,
    pub passo_pratico: String,
}

/// Representa uma entrada genérica na lista do diário.
#[derive(Clone, Debug)]
pub struct DiarioEntrada {
    pub id: i32,
    pub data: String,
    pub tipo: String,
    pub resumo: String,
}

/// Representa uma pergunta de autoexame (padrão ou do usuário).
#[derive(Clone, Debug, Default)]
pub struct PerguntaAutoExame {
    pub id: i32,
    pub categoria: String,
    pub texto: String,
    pub is_user_defined: bool,
    pub is_active: bool,
}

/// Representa uma oração puritana.
#[derive(Clone, Debug)]
pub struct OracaoPuritana {
    pub id: i32,
    pub titulo: String,
    pub texto_completo: String,
}

/// Representa um único registro da tabela 'salterio'.
#[derive(Clone, Debug)]
pub struct Salmo {
    pub _id: i32,
    pub referencia: String,
    pub melodia: Option<String>,
    pub _tema: Option<String>,
    pub letra: Option<String>,
    pub instrumental: Option<String>,
    pub a_capela: Option<String>,
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

/// Representa um livro da Bíblia.
#[derive(Clone, Debug)]
pub struct Livro {
    pub id: i32,
    pub name: String,
}
