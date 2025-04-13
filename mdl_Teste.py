import moviepy.config as mpy_config
import winsound
import traceback
import inspect
import logging
import shutil
import subprocess
import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, clips_array, TextClip, ColorClip, concatenate_videoclips, ImageClip
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_GoogleSheets import main as fnc_RetornaDocGoogle

mpy_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})  # Ajuste o caminho conforme sua instalação


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

	return {"Resultado": arquivo_saida, 'Status_log': log_info, 'Detail_log': varl_detail}


def gerar_texto(texto, tamanho, cor, fonte, dimensao=(640, 50), alinhamento='center', tempo=10):
	img = Image.new("RGBA", dimensao, (0, 0, 0, 0))
	draw = ImageDraw.Draw(img)

	font = ImageFont.truetype(fonte, tamanho)

	# Compatível com novas versões da Pillow
	bbox = draw.textbbox((0, 0), texto, font=font)
	largura_texto = bbox[2] - bbox[0]
	altura_texto = bbox[3] - bbox[1]

	pos_x = (dimensao[0] - largura_texto) // 2 if alinhamento == 'center' else 0
	pos_y = (dimensao[1] - altura_texto) // 2

	draw.text((pos_x, pos_y), texto, font=font, fill=cor)

	return ImageClip(np.array(img)).set_duration(tempo)  # ajuste a duração conforme necessário


def gerar_saudacao(texto: str, inicio: int, altura: int, duracao_total: float, fonte: str) -> TextClip:
	return (TextClip(
		texto,
		fontsize=20,
		color='white',
		font=fonte,
		size=(640, 50),
		method='caption'
	).set_duration(duracao_total - inicio)
	 .set_start(inicio)
	 .set_position(("center", altura))
	 .fadein(1))


def fnc_montar_padrao(caminho, arquivo, legenda, inferior, intro, outro, leg_default, leg_detalhe, parte_duracao = 10):
	log_info = "F1"
	varl_detail = None
	arquivo_out = 'editado.mp4'
	size = (640, 360)
	fonte_atma = r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Artes\Atma\Atma-Bold.ttf'
	fonte_unicode = r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Artes\Arial Unicode MS\arial_unicode_ms.otf'
	saudacoes = [leg_default['saudacao_portugues'], leg_default['saudacao_ingles'], leg_default['saudacao_chines'],	leg_default['saudacao_coreano']]
	agradece = [leg_default['agradecimento_portugues'], leg_default['agradecimento_ingles'], leg_default['agradecimento_chines'], leg_default['agradecimento_coreano']]
	citacoes = [leg_detalhe['credito_drums'], leg_detalhe['credito_bass'], leg_detalhe['credito_inferior']]
	emoji_virado = r"C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Artes\emoji_inverso.png"
	emoji_timido = r"C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Artes\emoji_timido.png"

	try:
		log_info = "F3"
		# Composição INTRO
		video_intro = VideoFileClip(os.path.join(caminho, intro)).subclip(0, 15).resize(size)

		fundo = ColorClip(size=size, color=(0, 0, 0), duration=video_intro.duration)
		salto = 3
		slogan_clip = gerar_texto(
			texto=leg_default['slogan'],
			tamanho=30,
			cor='yellow',
			fonte=fonte_atma,
			dimensao=(640, 50),
			tempo=15
		).set_position(("center", "top")).fadein(salto)

		emoji = ImageClip(emoji_virado) \
			.set_duration(video_intro.duration) \
			.set_position(("center", "bottom")) \
			.fadein(salto) \
			.resize(0.25)

		textos_saudacoes = []
		for i, texto in enumerate(saudacoes):
			inicio = salto + i * salto
			fonte = ImageFont.truetype(fonte_unicode, 30)
			img = Image.new("RGBA", (640, 360), color=(0, 0, 0, 0))
			draw = ImageDraw.Draw(img)
			text_size = draw.textbbox((0, 0), texto, font=fonte)
			text_height = text_size[3] - text_size[1]
			text_y = (img.height - text_height) // 2 - 50
			text_width = text_size[2] - text_size[0]
			text_x = (img.width - text_width) // 2
			draw.text((text_x, text_y), texto, font=fonte, fill="white")
			img_path = f"temp_text_{i}.png"
			img.save(img_path)
			clip = ImageClip(img_path).set_duration(salto)
			clip = clip.set_position("center").fadein(1)
			textos_saudacoes.append(clip.set_start(inicio))

		inferior_intro = CompositeVideoClip([fundo, *textos_saudacoes, slogan_clip, emoji])
		compose_intro = clips_array([[video_intro], [inferior_intro]])
		compose_intro = compose_intro.set_audio(video_intro.audio)


		log_info = "F3"
		# Composição OUTRO
		video_outro = VideoFileClip(os.path.join(caminho, outro)).subclip(0, 10).resize(size)
		textos_citacao = []
		for i, texto in enumerate(citacoes):
			clip = TextClip(
				texto,
				fontsize=24,
				font=fonte_atma,
				color='white',
				size=(size[0] - 40, None),
				method='caption'
			).set_duration(video_outro.duration)
			y = size[1] - (len(citacoes) - i) * 30 - 10
			textos_citacao.append(clip.set_position(("center", y)))

		clip_sup = TextClip(
			"Agradecimentos aos canais do Youtube:",
			fontsize=24,
			font=fonte_atma,
			color='white',
			size=(size[0] - 40, None),
			method='caption'
		).set_duration(video_outro.duration)
		clip_sup = clip_sup.set_position(("top"))
		superior_outro = CompositeVideoClip([video_outro, clip_sup, *textos_citacao])

		fundo = ColorClip(size=size, color=(0, 0, 0), duration=video_outro.duration)
		fundo = fundo.set_audio(video_outro.audio)
		salto = 2
		slogan_clip = gerar_texto(
			texto=leg_default['slogan'],
			tamanho=30,
			cor='yellow',
			fonte=fonte_atma,
			dimensao=(640, 50),
			tempo = 10
		).set_position(("center", "top")).fadein(salto)

		emoji = ImageClip(emoji_timido) \
			.set_duration(video_outro.duration) \
			.set_position(("center", "bottom")) \
			.fadein(salto) \
			.resize(0.25)

		textos_agradece = []
		for i, texto in enumerate(agradece):
			inicio = salto + i * salto
			fonte = ImageFont.truetype(fonte_unicode, 30)
			img = Image.new("RGBA", (640, 360), color=(0, 0, 0, 0))
			draw = ImageDraw.Draw(img)
			text_size = draw.textbbox((0, 0), texto, font=fonte)
			text_height = text_size[3] - text_size[1]
			text_y = (img.height - text_height) // 2 - 50
			text_width = text_size[2] - text_size[0]
			text_x = (img.width - text_width) // 2
			draw.text((text_x, text_y), texto, font=fonte, fill="white")
			img_path = f"temp_text_{i}.png"
			img.save(img_path)
			clip = ImageClip(img_path).set_duration(salto)
			clip = clip.set_position("center").fadein(1)
			textos_agradece.append(clip.set_start(inicio))


		inferior_outro = CompositeVideoClip([fundo, *textos_agradece, slogan_clip, emoji])
		compose_outro = clips_array([[superior_outro], [inferior_outro]])
		compose_outro = compose_outro.set_audio(video_outro.audio)


		log_info = "F4"
		# Composição PRINCIPAL
		video_sup= (VideoFileClip(os.path.join(caminho, arquivo)).resize(size))
		video_sup = video_sup.subclip(0, 30)  # Flag de testes rápidos
		video_inf = (VideoFileClip(os.path.join(caminho, inferior)).subclip(0, video_sup.duration).resize(size))

		num_partes = int(video_sup.duration // parte_duracao) + 1
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

		log_info = "F5"
		compose_01 = clips_array([[video_sup], [video_inf]])
		compose_final = CompositeVideoClip([compose_01, *textos_partes])  # Adiciona o texto ao vídeo
		compose_final = compose_final.set_audio(video_sup.audio)  # Atribui o áudio ao final
		compose_final.preview()
		breakpoint()

		log_info = "F6"
		compose_final = compose_final.set_audio(video_sup.audio)  # Atribui o áudio ao final
		# compose_final.preview()  # Para visualizar o vídeo
		compose_final.write_videofile(os.path.join(caminho, arquivo_out), fps=24)

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
		if lista["Resultado"]:
			exec_info += f"\t\t\t\tFUTE COM Arquivos a processar:\n"
			for caminho in lista["Resultado"]:
				resultado = fnc_cortes_preto(caminho)
				exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
				exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
				exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
		else:
			exec_info += f"\t\t\t\tFUTE SEM Arquivos a processar.\n"

		# PROCESSOS DRUMEIBES
		lista = fnc_buscar_processar(diretorio_banda, 'Drumeibes')
		if lista["Resultado"]:
			exec_info += f"\t\t\t\tDRUMEIBES COM Arquivos a processar:\n"
			for caminho in lista["Resultado"]:
				caminho_arquivo = os.path.dirname(caminho)
				nome_arquivo = os.path.basename(caminho)
				nome_inferior = nome_arquivo.replace('Drumeibes','INFERIOR')
				nome_lrc = os.path.splitext(nome_arquivo.replace('Drumeibes','LEGENDA'))[0] + '.lrc'
				nome_intro = r"C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Intro.mp4"
				nome_final = r"C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Outro.mp4"
				if (    os.path.exists(os.path.join(caminho_arquivo, nome_arquivo))
					and os.path.exists(os.path.join(caminho_arquivo, nome_inferior))
					and os.path.exists(os.path.join(caminho_arquivo, nome_lrc))
					and os.path.exists(os.path.join(caminho_arquivo, nome_intro))
					and os.path.exists(os.path.join(caminho_arquivo, nome_final))
				):
					exec_info += f"\t\t\t\t{nome_arquivo} SEM ARQUIVOS PENDENTES.\n"
					resultado = fnc_RetornaDocGoogle(os.path.splitext(nome_arquivo)[0])
					print(resultado['default'])
					print(resultado['detalhe'])
					# doc_default = {'saudacao_portugues': 'Um olá da Drumeibes! \nSiga-nos! \nRegrave em cima do nosso video!', 'agradecimento_portugues': 'Agradecimentos', 'slogan': 'Drum + Beis = Bateria + Baixo', 'saudacao_ingles': 'Hello from Drumeibes! \nFollow us! \nRe-record over our video!', 'agradecimento_ingles': 'Thanks', 'creditos': 'Menções e agradecimentos aos mestres:', 'saudacao_chines': '来自 Drumeibes \n的问候！\n关注我们！重新录制我们的视频！', 'agradecimento_chines': '谢谢', 'saudacao_coreano': '안녕하세요 Drumeibes\n입니다! 우리를 따르세요! \n영상을 다시 녹화해 보세요!', 'agradecimento_coreano': '감사해요'}
					# doc_detalhe = {'nome_artista': 'The Scorpions', 'inicio_legenda': '15', 'credito_drums': 'https://www.youtube.com/@jeremyYanzi', 'credito_bass': 'https://www.youtube.com/@kashewsbasschannel3752', 'credito_inferior': 'https://www.youtube.com/@sycomgames'}
					# Inserir as legendas de @ nos videos, 2 superior para instrumentos, 1 inferior para video inf
					# Inserir as legendas da musica para cantar com os videos
					# resultado = fnc_montar_padrao(caminho_arquivo, nome_arquivo, nome_lrc, nome_inferior, nome_intro, nome_final, doc_default, doc_detalhe)
					# exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
					# exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
					# exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
					# resultado = fnc_dividir_fixo(os.path.join(os.path.dirname(caminho), 'editado.mp4'),os.path.dirname(caminho))
				else:
					pass
		else:
			exec_info += f"\t\t\t\tDRUMEIBES SEM Arquivos a processar:\n"

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