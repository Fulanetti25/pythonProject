import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from datetime import timedelta
from SCRIPTS.functions.cls_CarregaJson import json_caminho

def verificar_e_ordenar_videos(diretorio):
    # Extensões de vídeo suportadas
    extensoes_video = (".mp4", ".avi", ".mov", ".mkv")

    # Verificar se o diretório existe
    if not os.path.exists(diretorio):
        print(f"Diretório não encontrado: {diretorio}")
        return []

    # Inicializar lista para armazenar os vídeos encontrados
    arquivos_videos = []

    # Percorrer o diretório e as subpastas
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.lower().endswith(extensoes_video):
                arquivos_videos.append(os.path.join(raiz, arquivo))

    if not arquivos_videos:
        print(f"Nenhum arquivo de vídeo encontrado no diretório {diretorio} e suas subpastas.")
        return []

    # Ordenar os arquivos pelo caminho completo
    arquivos_videos.sort()

    print("Arquivos de vídeo encontrados e ordenados:")
    for arquivo in arquivos_videos:
        print(f"- {arquivo}")

    return arquivos_videos

def cortar_videos_em_segmentos(arquivos_videos, pasta_saida, duracao_segmento=600):
    """
    Corta vídeos em segmentos de duração fixa (em segundos) e salva na pasta de saída.

    :param arquivos_videos: Lista de caminhos dos vídeos a serem processados.
    :param pasta_saida: Diretório onde os segmentos serão salvos.
    :param duracao_segmento: Duração de cada segmento em segundos (padrão: 600 segundos = 10 minutos).
    """
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    tempo_acumulado = 0
    segmento_index = 1

    for arquivo in arquivos_videos:
        with VideoFileClip(arquivo) as video:
            duracao_video = int(video.duration)  # Duração do vídeo em segundos
            print(f"Processando {arquivo} com duração de {str(timedelta(seconds=duracao_video))}")

            inicio = 0
            while inicio < duracao_video:
                # Definir o final do segmento (não ultrapassar o final do vídeo)
                fim = min(inicio + duracao_segmento - tempo_acumulado, duracao_video)

                # Criar segmento
                segmento = video.subclip(inicio, fim)

                # Nome do segmento baseado no índice
                nome_segmento = os.path.join(
                    pasta_saida,
                    f"segmento_{segmento_index:03d}.mp4"
                )
                segmento.write_videofile(nome_segmento, codec="libx264", audio_codec="aac")

                # Atualizar tempos
                tempo_segmento = fim - inicio
                tempo_acumulado += tempo_segmento

                # Quando o tempo acumulado atingir o limite do segmento, reiniciar
                if tempo_acumulado >= duracao_segmento:
                    tempo_acumulado = 0
                    segmento_index += 1

                inicio = fim  # Avançar para o próximo intervalo

    print("Processamento concluído.")

# Caminhos de entrada
arquivos_videos = [
    r"C:\Users\paulo\Downloads\TEMP\20250119\GH010194.MP4",
    r"C:\Users\paulo\Downloads\TEMP\20250119\GH020194.MP4"
]

# Diretório de saída (por data)
pasta_saida = r"C:\Users\paulo\Downloads\TEMP\20250119\por_horario"

# Chamar a função para processar os vídeos
cortar_videos_em_segmentos(arquivos_videos, pasta_saida)
#
# diretorio = json_caminho('Entrada_GoPro')
#
# videos_ordenados = verificar_e_ordenar_videos(diretorio['Diretorio'])
