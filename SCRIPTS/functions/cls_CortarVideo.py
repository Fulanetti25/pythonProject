import subprocess
import os
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados


def fnc_tempo_para_segundos(tempo_str):
    h, m, s = map(float, tempo_str.split(':')) if ':' in tempo_str else (0, 0, float(tempo_str))
    return h * 3600 + m * 60 + s


def fnc_cortar_video(video_path, tempo_inicial, tempo_final, output_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(tempo_inicial),  # Tempo inicial de corte
        '-to', str(tempo_final),  # Tempo final de corte
        '-c:v', 'libx264',  # Usando o codec de vídeo H.264
        '-c:a', 'aac',  # Usando o codec de áudio AAC
        '-strict', 'experimental',  # Permite a utilização de codecs experimentais
        '-y',  # Sobrescreve o arquivo de saída sem perguntar
        output_path
    ]
    subprocess.run(command, check=True)


def fnc_dividir_lista(video_path, lista):
    for i, item in enumerate(lista):
        tempo_str, descricao = item.split(" - ")
        tempo_inicial = fnc_tempo_para_segundos(tempo_str)

        tempo_inicial_corte = tempo_inicial - 10
        tempo_final_corte = tempo_inicial + 10

        output_path = f"corte_{descricao.replace(' ', '_').replace(':', '').replace('-', '')}.mp4"

        print(f"Cortando vídeo: {descricao} ({tempo_inicial_corte} até {tempo_final_corte})")
        fnc_cortar_video(video_path, tempo_inicial_corte, tempo_final_corte, output_path)


def fnc_dividir_fixo(video_path, output_path, segundos):
    command_duracao = [
        'ffmpeg', '-i', video_path,
        '-f', 'null', '-'
    ]
    result = subprocess.run(command_duracao, stderr=subprocess.PIPE, text=True)

    duracao_total = 0
    for line in result.stderr.split('\n'):
        if "Duration" in line:
            tempo_str = line.split(",")[0].split("Duration:")[1].strip()
            duracao_total = fnc_tempo_para_segundos(tempo_str)
            break

    if duracao_total == 0:
        print("Erro ao obter a duração do vídeo.")
        return

    for i in range(0, int(duracao_total), segundos):
        tempo_inicial_corte = i
        tempo_final_corte = min(i + segundos, duracao_total)
        saida = os.path.join(output_path, f"corte_{i // segundos + 1}.mp4")

        print(f"Cortando vídeo: Parte {i // segundos + 1} ({tempo_inicial_corte} até {tempo_final_corte})")
        fnc_cortar_video(video_path, tempo_inicial_corte, tempo_final_corte, saida)

def fnc_buscar_processar(diretorio):
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if "PROCESSAR_" in arquivo:
                return os.path.join(raiz, arquivo)
    return None

mapa_objetos = json_caminho('Json_VideosDrumeibes')
diretorio = os.path.join(mapa_objetos['Diretorio'])
arquivo_processar = fnc_buscar_processar(diretorio)
arquivo_caminho = os.path.dirname(arquivo_processar)

if arquivo_processar:
    fnc_dividir_fixo(os.path.join(mapa_objetos['Diretorio'], arquivo_processar),arquivo_caminho, 15)
    # Montar inicio, fim e Legendar Video
else:
    print(f"Arquivo NÃO encontrado: {arquivo_processar}")
