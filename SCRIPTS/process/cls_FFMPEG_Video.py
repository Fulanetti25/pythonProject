import moviepy.config as mpy_config
import winsound
import traceback
import inspect
import logging
import shutil
import subprocess
import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, clips_array, TextClip
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


# CONFIGURACOES E GLOBAIS
mpy_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})  # Ajuste o caminho conforme sua instalação


#     # IMAGENS
# image = (
#     ImageClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\i1.png', duration = 15)
#     # .resize(.5)
# )
#     # AUDIOS
# audio_intro = (
#     AudioFileClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\a1.mp3')
#     .subclip(8,18)
# )
# audio_credito = (
#     AudioFileClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\a1.mp3')
#     .subclip(38,48)
# )
#
# # PADRONIZAÇÃO DE FORMATOS
# audio_v1 = video_1.audio
# audio_v2 = video_2.audio
# audio_videos = concatenate_audioclips([audio_v1, audio_v2])
# audio_concatenado = concatenate_audioclips([audio_intro, audio_videos, audio_credito])
# color_0 = ColorClip(size=texto_intro.size, color=(0, 255, 0), duration=3).set_start(0).set_fps(24)
# color_1 = ColorClip(size=texto_intro.size, color=(0, 150, 150), duration=3).set_start(3).set_fps(24)
# color_2 = ColorClip(size=texto_intro.size, color=(0, 0, 255), duration=3).set_start(6).set_fps(24)
#
# # COMPOSIÇÕES DE FASES
# compose_intro = CompositeVideoClip([color_2, color_1, color_0, texto_intro]).set_fps(24)
# compose_credito = CompositeVideoClip([color_0, color_1, color_2, texto_credito]).set_fps(24)
#
# # COMPOSIÇÕES FINAIS
# compose1 = concatenate_videoclips([video_1,video_2])
# compose2 = CompositeVideoClip([compose1,image])
# compose3 = clips_array([[compose2],[video_inferior]])
# compose4 = concatenate_videoclips([compose_intro,compose3])
# compose5 = concatenate_videoclips([compose4,compose_credito])


def fnc_tempo_para_segundos(tempo_str):
	h, m, s = map(float, tempo_str.split(':')) if ':' in tempo_str else (0, 0, float(tempo_str))
	return h * 3600 + m * 60 + s


def fnc_dividir_lista(video_path, lista):
	for i, item in enumerate(lista):
		tempo_str, descricao = item.split(" - ")
		tempo_inicial = fnc_tempo_para_segundos(tempo_str)

		tempo_inicial_corte = tempo_inicial - 10
		tempo_final_corte = tempo_inicial + 10

		output_path = f"corte_{descricao.replace(' ', '_').replace(':', '').replace('-', '')}.mp4"

		print(f"Cortando vídeo: {descricao} ({tempo_inicial_corte} até {tempo_final_corte})")
		fnc_cortar_video(video_path, tempo_inicial_corte, tempo_final_corte, output_path)


def fnc_dividir_fixo(video_path, output_path, segundos= 10):
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


def fnc_buscar_processar(diretorio, palavra):
	log_info = "F1"
	varl_detail = None
	lista = []

	try:
		log_info = "F2"
		for raiz, _, arquivos in os.walk(diretorio):
			for arquivo in arquivos:
				if palavra in arquivo:
					lista.append(os.path.join(raiz, arquivo))

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": lista, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_buscar_arquivos(diretorio: str, incluir_subpastas: bool = True) -> list:
	arquivos_encontrados = []

	if incluir_subpastas:
		for root, _, files in os.walk(diretorio):
			for file in files:
				arquivos_encontrados.append(os.path.join(root, file))
	else:
		arquivos_encontrados = [os.path.join(diretorio, file) for file in os.listdir(diretorio) if os.path.isfile(os.path.join(diretorio, file))]

	return arquivos_encontrados


def fnc_unificar_videos(diretorio: str):
	subpastas = [pasta.path for pasta in os.scandir(diretorio) if pasta.is_dir()]
	for subpasta in subpastas:
		arquivos = sorted(fnc_buscar_arquivos(subpasta, incluir_subpastas=False))
		videos = [arquivo for arquivo in arquivos if arquivo.lower().endswith(".mp4")]
		if not videos:
			print(f"Nenhum vídeo encontrado na subpasta: {subpasta}")
			continue

		lista_txt = os.path.join(subpasta, "lista_videos.txt")
		with open(lista_txt, "w", encoding="utf-8") as f:
			for video in videos:
				f.write(f"file '{video.replace('\\', '/')}'\n")

		nome_pasta = os.path.basename(subpasta)
		arquivo_saida = os.path.join(diretorio, f"{nome_pasta}_BRUTO.mp4")

		comando = [
			"ffmpeg", "-f", "concat", "-safe", "0", "-i", lista_txt,
			"-c", "copy", arquivo_saida, "-y"
		]

		try:
			subprocess.run(comando, check=True, cwd=os.path.abspath(subpasta))
			print(f"Vídeo unificado criado: {arquivo_saida}")
		except subprocess.CalledProcessError as e:
			print(f"Erro ao unir os vídeos na pasta {subpasta}: {e}")
		finally:
			if os.path.exists(lista_txt):
				os.remove(lista_txt)
			if os.path.exists(arquivo_saida):
				shutil.rmtree(subpasta)
				print(f"Pasta {subpasta} removida.")


def fnc_cortes_preto(arquivo: str):
	# Definindo o nome do arquivo de saída
	diretorio = os.path.dirname(arquivo)
	nome_base = os.path.basename(arquivo)[:8]
	arquivo_saida = os.path.join(diretorio, f"{nome_base}_Highlights Sub99.mp4")

	# Passo 1: Detectar os quadros pretos no vídeo
	comando = [
		"ffmpeg", "-i", arquivo, "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-"
	]

	# Executando o comando e pegando a saída
	process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()

	# Depuração: Exibir a saída completa para verificar se há informações úteis
	print(stderr.decode())

	# Passo 2: Processar os tempos de corte
	cortes = []
	for line in stderr.decode().split("\n"):
		if "black_start" in line:
			try:
				time = float(line.split("black_start:")[1].split()[0])
				start_time = max(0, time - 15)  # -15 segundos antes do preto
				end_time = time
				cortes.append((start_time, end_time))
			except ValueError:
				continue

	if not cortes:
		print("Nenhum quadro preto encontrado no vídeo.")
		return None

	# Passo 3: Criar os cortes no vídeo
	lista_cortes = []
	for i, (start_time, end_time) in enumerate(cortes):
		comando_corte = [
			"ffmpeg", "-i", arquivo, "-ss", str(start_time), "-to", str(end_time),
			"-c:v", "copy", "-c:a", "copy", "-y", f"{diretorio}/corte_{i}.mp4"
		]

		try:
			subprocess.run(comando_corte, check=True)
			lista_cortes.append(f"{diretorio}/corte_{i}.mp4")
		except subprocess.CalledProcessError as e:
			print(f"Erro ao cortar o vídeo: {e}")

	if not lista_cortes:
		print("Nenhum corte válido foi gerado.")
		return None

	# Passo 4: Unificar os cortes em um único arquivo de saída
	lista_cortes_txt = os.path.join(diretorio, "lista_cortes.txt")
	with open(lista_cortes_txt, "w") as f:
		for corte in lista_cortes:
			f.write(f"file '{corte}'\n")

	# Comando para unir os vídeos cortados
	comando_unir = [
		"ffmpeg", "-f", "concat", "-safe", "0", "-i", lista_cortes_txt,
		"-c:v", "copy", "-c:a", "copy", "-y", arquivo_saida
	]

	try:
		subprocess.run(comando_unir, check=True)
		print(f"Arquivo final criado: {arquivo_saida}")
	except subprocess.CalledProcessError as e:
		print(f"Erro ao unir os cortes: {e}")
		return None

	# Passo 5: Limpar os arquivos temporários (cortes individuais)
	for corte in lista_cortes:
		os.remove(corte)
	os.remove(lista_cortes_txt)
	print("Arquivos temporários removidos.")

	return arquivo_saida


def fnc_montar_padrao(caminho, arquivo, parte_duracao = 10):
	log_info = "F1"
	varl_detail = None
	arquivo_out = None

	try:
		log_info = "F2"
		arquivo_inferior = arquivo.replace('PROCESSAR_', 'INFERIOR_')
		if not os.path.exists(os.path.join(caminho, arquivo_inferior)):
			raise FileNotFoundError(f"Arquivo inferior não encontrado: {arquivo_inferior}")

		log_info = "F3"
		size = (640, 360)
		video_sup = (VideoFileClip(os.path.join(caminho, arquivo)).resize(size))
		# video_sup = video_sup.subclip(0, 30)  # Flag de testes rápidos
		num_partes = int(video_sup.duration // parte_duracao) + 1
		video_inf = (VideoFileClip(os.path.join(caminho, arquivo_inferior)).subclip(0, video_sup.duration).resize(size))

		log_info = "F5"
		textos_partes = []

		for i in range(num_partes):
			if i == num_partes - 1:
				texto_duracao = video_sup.duration - (i * parte_duracao)  # Duração restante no vídeo
			else:
				texto_duracao = parte_duracao
			texto_parte = TextClip(f'parte {i + 1}', color='yellow', fontsize=50, font='Arial', size=(640, 720))
			texto_parte = (texto_parte.set_duration(texto_duracao)
						   .set_position(('center', 360 - 50))
						   .set_start(i * parte_duracao)
						   .set_end(i * parte_duracao + texto_duracao))
			textos_partes.append(texto_parte)  # Adiciona o objeto à lista

		log_info = "F6"
		# Criar o vídeo composto com o vídeo e os textos
		compose_01 = clips_array([[video_sup], [video_inf]])
		compose_02 = CompositeVideoClip([compose_01, *textos_partes])  # Adiciona o texto ao vídeo

		log_info = "F7"
		arquivo_out = 'editado.mp4'
		compose_02 = compose_02.set_audio(video_sup.audio)  # Atribui o áudio ao final
		# compose_02.preview()  # Para visualizar o vídeo
		compose_02.write_videofile(os.path.join(caminho, arquivo_out), fps=24)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	finally:
		pass
		# os.remove(file_name)

	return {"Resultado": arquivo_out, 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	lista = []
	processo_banda = json_caminho('Json_VideosDrumeibes')
	processo_futes = json_caminho('Json_VideosFute')
	diretorio_banda = os.path.join(processo_banda['Diretorio'])
	diretorio_futes = os.path.join(processo_futes['Diretorio'])
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		# PROCESSOS FUTE
		resultado = fnc_unificar_videos(diretorio_futes)
		lista = fnc_buscar_processar(diretorio_futes, '_BRUTO')
		for caminho in lista["Resultado"]:
			resultado = fnc_cortes_preto(caminho)
			exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
			exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
			exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"

		# lista = fnc_buscar_processar(diretorio_banda, 'PROCESSAR_')
		# for caminho in lista["Resultado"]:
		# 	pass
		# 	# PROCESSOS DRUMEIBES
		# 	# Montar inicio (3 segundos, apresentação)
		# 	# Montar final (3 segundos, creditos)
		# 	# Inserir as legendas de @ nos videos, 2 superior para instrumentos, 1 inferior para video inf
		# 	# resultado = fnc_montar_padrao(os.path.dirname(caminho), os.path.basename(caminho))
		# 	# resultado = fnc_dividir_fixo(os.path.join(os.path.dirname(caminho), 'editado.mp4'),os.path.dirname(caminho))

		exec_info += "\t\tMF\n"
		varg_erro = False

	except Exception as e:
		exec_info += "\t\t\tM99\n"
		exec_info += f"Traceback: {traceback.format_exc()}"
		varg_erro = True

	finally:
		exec_info += "LF\n"
		log_registra(varg_modulo, inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)
	winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms