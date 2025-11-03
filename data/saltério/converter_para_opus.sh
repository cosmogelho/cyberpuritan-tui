#!/bin/bash

# Verifica se o ffmpeg está instalado
if ! command -v ffmpeg &> /dev/null
then
    echo "FFmpeg não encontrado. Por favor, instale com 'sudo pacman -S ffmpeg'"
    exit 1
fi

echo "Iniciando a conversão de todos os arquivos .mp3 para .opus a 64kbps..."

# Loop para encontrar todos os arquivos .mp3 no diretório atual
for arquivo_mp3 in *.mp3; do
  # Define o nome do novo arquivo, trocando a extensão
  arquivo_opus="${arquivo_mp3%.mp3}.opus"
  
  echo "Convertendo '$arquivo_mp3' para '$arquivo_opus'..."
  
  # O comando de conversão
  # -i: arquivo de entrada
  # -c:a libopus: usa o codec Opus
  # -b:a 64k: define o bitrate de áudio para 64 kbps
  # -v error: mostra apenas mensagens de erro para uma saída mais limpa
  ffmpeg -i "$arquivo_mp3" -c:a libopus -b:a 64k -v error "$arquivo_opus"
  
  # Se a conversão foi bem-sucedida, apaga o arquivo mp3 original
  if [ $? -eq 0 ]; then
    rm "$arquivo_mp3"
  else
    echo "  -> Falha ao converter '$arquivo_mp3'!"
  fi
done

echo "Conversão concluída!"
