import numpy as np
from PIL import Image
from blessed import Terminal

term = Terminal()

# Abrir e redimensionar a imagem
img = Image.open(r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\FILES\PlanilhaSobMedida.jpg")
img = img.resize((80, 40))  # Ajuste o tamanho
img = img.convert("RGB")

# Converter para numpy array
pixels = np.array(img, dtype=int)  # Converter para tipo int

# Exibir a imagem no terminal com blocos coloridos
print(term.clear)
for row in pixels:
    for r, g, b in row:
        print(term.on_rgb(int(r), int(g), int(b)) + "  ", end="")  # Converter valores para int
    print(term.normal)  # Reset de cor no final da linha

import os
import numpy as np
from pydub import AudioSegment, silence
import ffmpeg


def detectar_inicio_audio(video_path):
    # Extrai o áudio do vídeo
    audio_path = video_path.replace(".mp4", ".wav")
    ffmpeg.input(video_path).output(audio_path, format="wav").run(overwrite_output=True)

    # Carrega o áudio e detecta silêncio
    audio = AudioSegment.from_wav(audio_path)
    non_silent_chunks = silence.detect_nonsilent(audio, min_silence_len=500, silence_thresh=-40)

    if not non_silent_chunks:
        return 0  # Caso não encontre som, assume início como 0

    return non_silent_chunks[0][0] / 1000  # Converte milissegundos para segundos


def cortar_video(video_path, output_dir):
    inicio_audio = detectar_inicio_audio(video_path)

    # Garante que o diretório de saída existe
    os.makedirs(output_dir, exist_ok=True)

    # Obtém a duração total do vídeo
    probe = ffmpeg.probe(video_path)
    duracao = float(next((stream['duration'] for stream in probe['streams'] if stream['codec_type'] == 'video'), 0))

    # Gera cortes de 15 em 15 segundos
    i = 0
    while inicio_audio + i * 15 < duracao:
        output_file = os.path.join(output_dir, f"clip_{i + 1}.mp4")
        ffmpeg.input(video_path, ss=inicio_audio + i * 15, t=15).output(output_file).run(overwrite_output=True)
        i += 1

    print(f"Cortes salvos em: {output_dir}")


# Exemplo de uso
video_path = "video.mp4"
output_dir = "clips"
cortar_video(video_path, output_dir)
