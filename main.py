#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada principal para a aplicação Cyber-Puritano.
Este script inicia a interface de linha de comando.
"""
import sys
import os

# Adiciona o diretório raiz do projeto ao path para que os imports funcionem
# e para que o `app` seja encontrado corretamente.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.cli import cli

if __name__ == '__main__':
    cli()
