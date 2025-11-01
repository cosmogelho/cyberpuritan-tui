#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada principal para a aplicação Cyber-Puritano.
Este script inicia a interface de texto do usuário (TUI).
"""
import sys
import os

# Adiciona o diretório raiz do projeto ao path para que os imports funcionem
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# MODIFICADO: Importa a nova função principal diretamente do módulo cli
from app.cli import run_interactive_mode

if __name__ == '__main__':
    # MODIFICADO: Chama a nova função principal que contém o loop da TUI
    run_interactive_mode()
