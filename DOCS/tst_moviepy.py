import moviepy.editor
print("MoviePy instalado com sucesso!")

import os
from moviepy.editor import VideoFileClip

def rotate_videos(input_folder, output_folder, rotation=180):
    # Cria a pasta de saída se não existir
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        # Filtra arquivos de vídeo
        if file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)

            try:
                print(f"Processando: {file_name}")
                with VideoFileClip(input_path) as clip:
                    # Gira o vídeo
                    rotated_clip = clip.rotate(rotation)
                    rotated_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            except Exception as e:
                print(f"Erro ao processar {file_name}: {e}")

# Configurações
input_folder = r"C:\Users\paulo\Downloads\TEMP\Bike Flex"  # Substitua pelo caminho da pasta com os vídeos
output_folder = r"C:\Users\paulo\Downloads\TEMP\Bike Flex\saida"   # Substitua pelo caminho da pasta para salvar os vídeos

# Executa o script
rotate_videos(input_folder, output_folder)
