use crate::utils::error::AppError;
use std::process::{Child, Command, Stdio};

pub fn play(path: &str) -> Result<Child, AppError> {
    // CORREÇÃO: Redireciona stdout e stderr para não sujar a UI
    let child = Command::new("mpv")
        .arg("--no-video")
        .arg(path)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()?;
    Ok(child)
}

pub fn stop(process: &mut Child) -> Result<(), AppError> {
    process.kill()?;
    Ok(())
}
