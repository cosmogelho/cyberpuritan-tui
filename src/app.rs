use crate::{components::Component, models::Salmo, theme::Theme};
use std::{
    path::Path,
    process::{Child, Command},
};

pub struct App {
    pub should_quit: bool,
    pub theme: Theme,
    pub audio_process: Option<Child>,
    pub component_stack: Vec<Box<dyn Component>>,
}

impl App {
    pub fn new() -> Self {
        Self {
            should_quit: false,
            theme: Theme::new(),
            audio_process: None,
            component_stack: Vec::new(),
        }
    }

    pub fn push_component(&mut self, component: Box<dyn Component>) {
        self.component_stack.push(component);
    }

    pub fn pop_component(&mut self) {
        self.component_stack.pop();
    }

    pub fn quit(&mut self) {
        self.should_quit = true;
    }

    // --- Métodos de Áudio ---
    pub fn stop_audio(&mut self) {
        if let Some(mut child) = self.audio_process.take() {
            if child.kill().is_ok() {
                let _ = child.wait();
            }
        }
    }

    pub fn play_audio(&mut self, audio_type: &str, salmo: Option<&Salmo>) {
        self.stop_audio();
        let filename = salmo.and_then(|s| {
            match audio_type {
                "instrumental" => s.instrumental.as_ref(),
                "a_capela" => s.a_capela.as_ref(),
                _ => None,
            }
            .cloned()
        });
        if let Some(name) = filename {
            let path = Path::new("./data/saltério").join(&name);
            if path.exists() {
                if let Ok(child) = Command::new("mpv")
                    .args(["--no-video", "--really-quiet", path.to_str().unwrap()])
                    .spawn()
                {
                    self.audio_process = Some(child);
                }
            }
        }
    }

    pub fn check_audio_process(&mut self) {
        if let Some(child) = self.audio_process.as_mut() {
            if let Ok(Some(_)) = child.try_wait() {
                self.audio_process.take();
            }
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub enum MessageType {
    Info,
    Success,
    Error,
}
