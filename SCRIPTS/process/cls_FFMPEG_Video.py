import moviepy.config as mpy_config
import winsound
import traceback
import inspect
import logging
import shutil
import subprocess
import os
import re
import itertools
from moviepy.editor import VideoFileClip, CompositeVideoClip, clips_array, TextClip, ColorClip, concatenate_videoclips, ImageClip, vfx
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_GoogleSheets import main as fnc_RetornaDocGoogle
from SCRIPTS.functions.cls_APIGPT import main as prc_TraduzLetra


mpy_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})  # Ajuste o caminho conforme sua instalação


def fnc_tempo_para_segundos(tempo_str):
	h, m, s = map(float, tempo_str.split(':')) if ':' in tempo_str else (0, 0, float(tempo_str))
	return h * 3600 + m * 60 + s


def fnc_dividir_fixo(video_path, segundos=10):
	# Obtém duração do vídeo com ffmpeg
	command_duracao = ['ffmpeg', '-i', video_path, '-f', 'null', '-']
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

	# Divide o vídeo inteiro em blocos de "segundos", inclusive o final parcial
	parte = 1
	for i in range(0, int(duracao_total), segundos):
		tempo_inicial_corte = i
		tempo_final_corte = min(i + segundos, duracao_total)
		nome_base = os.path.basename(video_path)
		output_dir = os.path.dirname(video_path)
		saida = os.path.join(output_dir, f"{os.path.splitext(nome_base)[0]}_{parte:02d}_{int(tempo_inicial_corte):03d}-{int(tempo_final_corte):03d}.mp4")

		print(f"Cortando vídeo: Parte {parte} ({tempo_inicial_corte} até {tempo_final_corte})")
		fnc_cortar_video(video_path, tempo_inicial_corte, tempo_final_corte, saida)
		parte += 1


def fnc_cortar_video(video_path, tempo_inicial, tempo_final, output_path):
	command = [
		'ffmpeg',
		'-ss', str(tempo_inicial),
		'-i', video_path,
		'-t', str(tempo_final - tempo_inicial),
		'-c:v', 'libx264',
		'-c:a', 'aac',
		'-y',
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


def fnc_gerar_documento(arquivo, caminho, leg_detalhe, tags, prefixo_creditos, descricao_padrao):
	# Nome do vídeo no Youtube e TikTok
	nome_arquivo = f"{arquivo}".replace('.mp4','')

	# Descrição do vídeo com base no texto padrão e créditos
	descricao = (
		descricao_padrao.strip() + "\n\n"
		"🎧 Menções e agradecimentos aos mestres:\n"
		f"{prefixo_creditos}{leg_detalhe['credito_drums']}\n"
		f"{prefixo_creditos}{leg_detalhe['credito_bass']}\n"
		f"{prefixo_creditos}{leg_detalhe['credito_inferior']}"
	)

	# Tags do vídeo
	palavras_nome = [parte.strip().lower() for parte in os.path.splitext(arquivo.replace('-', '').replace('.mp4', ''))[0].split(' ') if parte.strip() != '']
	for combinacao in itertools.combinations(palavras_nome, 1):
		tags.append(' '.join(combinacao).replace('  ', ' '))
	tags = list(set(tags))  # Remove duplicatas
	tags_string = ' '.join([f'#{tag},' for tag in tags]) + ''

	# Criando o conteúdo do arquivo de texto
	texto = f"""
{nome_arquivo}\n
{descricao}\n
Link Original:


Tags do Video:
{tags_string}
	"""

	# Caminho para salvar o arquivo de texto
	caminho_txt = os.path.join(caminho, f"{os.path.splitext(arquivo)[0]}.txt")
	# Grava o conteúdo no arquivo de texto
	with open(caminho_txt, 'w', encoding='utf-8') as f:
		f.write(texto)
	print(f"Arquivo de texto gerado: {caminho_txt}")


def fnc_gerar_texto(texto, tamanho, cor, fonte, dimensao=(640, 50), alinhamento='center', tempo=10):
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


def fnc_gerar_saudacao(texto: str, inicio: int, altura: int, duracao_total: float, fonte: str) -> TextClip:
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


def fnc_carregar_legendas_lrc(caminho_arquivo_srt, delay, tamanho_video, duracao_maxima=None):
	inicio = float(delay)
	if "LEGENDA" in caminho_arquivo_srt.upper():
		flag = 1
	elif "TRADUCAO" in caminho_arquivo_srt.upper():
		flag = 2

	with open(caminho_arquivo_srt, encoding="utf-8") as f:
		linhas = f.readlines()

	padrao_linha = re.compile(r"\[(\d+):(\d+\.\d+)\](.*)")
	entradas = []

	for i, linha in enumerate(linhas):
		match = padrao_linha.match(linha.strip())
		if match:
			minuto, segundo, texto = match.groups()
			tempo = int(minuto) * 60 + float(segundo)
			entradas.append({
				"inicio": tempo,
				"texto": texto.strip()
			})

	clips = []
	for i, entrada in enumerate(entradas):
		start = entrada["inicio"] + inicio

		if i + 1 < len(entradas):
			end = entradas[i + 1]["inicio"] + inicio
		else:
			end = start + 3  # Última legenda dura 3 segundos

		# Corta legenda que ultrapassa o tempo do vídeo
		if duracao_maxima is not None and start >= duracao_maxima:
			continue
		if duracao_maxima is not None and end > duracao_maxima:
			end = duracao_maxima

		duracao = end - start
		if duracao <= 0:
			continue
		if duracao < 1:
			duracao = 1

		texto_legenda = entrada["texto"]
		if texto_legenda.strip() == "":
			continue
		texto_legenda = texto_legenda.replace("@", "")  # Proteção básica

		try:
			clip = TextClip(
				texto_legenda,
				fontsize=90,
				font='Arial',
				color= 'yellow' if flag == 1 else 'white',
				stroke_color='black',
				size=(tamanho_video[0] - 100, None),
				method='caption',
				align = 'center'
			).set_start(start).set_duration(duracao).set_position(("center", 900 if flag == 1 else 1200))

			clips.append(clip)
		except Exception as e:
			print(f"[Erro ao criar legenda]: '{texto_legenda}' em {start:.2f}s -> {e}")

	return clips


def fnc_montar_teste(caminho, arquivo, legenda, inferior, leg_detalhe):
	log_info = "F1"
	varl_detail = None
	pasta_destino = os.path.dirname(caminho)
	size = (1080, 810)

	try:
		log_info = "F2"
		# Composição PRINCIPAL
		video_sup= (VideoFileClip(os.path.join(caminho, arquivo)).resize(size))
		video_sup = video_sup.subclip(0, 60)  # Flag de testes rápidos
		video_inf = (VideoFileClip(os.path.join(caminho, inferior)).subclip(0, video_sup.duration).resize(size))

		log_info = "F3"
		compose_01 = clips_array([[video_sup], [video_inf]])
		compose_01 = compose_01.set_audio(video_sup.audio)

		log_info = "F4"
		for deslocamento in range(-2, 3):
			inicio_legenda = float(leg_detalhe['inicio_legenda']) + deslocamento
			legenda_clips = fnc_carregar_legendas_lrc(os.path.join(caminho, legenda), inicio_legenda, size, duracao_maxima=video_sup.duration)
			compose_teste = CompositeVideoClip([compose_01, *legenda_clips])
			nome_arquivo = os.path.join(pasta_destino, f"t_legenda {inicio_legenda} {arquivo}.mp4")
			compose_teste.write_videofile(nome_arquivo, codec="libx264", fps=6)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	finally:
		pass

	return {"Resultado": 'Arquivos gerados com sucesso', 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_montar_padrao(caminho, arquivo, legenda, inferior, intro, outro, leg_default, leg_detalhe):
	log_info = "F1"
	varl_detail = None
	pasta_destino = os.path.dirname(caminho)
	size = (1080, 810)
	parte_duracao = 10
	fonte_atma = leg_default['fonte_atma']
	fonte_unicode = leg_default['fonte_unicode']
	saudacoes = leg_default['saudacoes']
	agradece = leg_default['agradece']
	citacoes = [leg_detalhe['credito_drums'], leg_detalhe['credito_bass'], leg_detalhe['credito_inferior']]
	idioma = leg_detalhe['idioma']
	emoji_virado = leg_default['emoji_virado']
	emoji_timido = leg_default['emoji_timido']
	tags = list(leg_default['tags'])  # Faz uma cópia da lista original
	prefixo_creditos = leg_default['prefixo_creditos']
	descricao_padrao = leg_default['descricao_padrao']
	traducao = legenda.replace("LEGENDA", "TRADUCAO")

	try:
		log_info = "F3"
		# Composição INTRO
		video_intro = VideoFileClip(os.path.join(caminho, intro)).subclip(0, 15).resize(size)
		fundo = ColorClip(size=size, color=(0, 0, 0), duration=video_intro.duration)
		slogan_clip = fnc_gerar_texto(texto=leg_default['slogan'],tamanho=70,cor='yellow',fonte=fonte_atma,dimensao=(1080, 100),tempo=15).set_position(("center", "top"))
		emoji = ImageClip(emoji_virado).set_duration(video_intro.duration).set_position(("center", "bottom")).resize(0.5)

		salto = 3
		textos_saudacoes = []
		for i, texto in enumerate(saudacoes):
			inicio = (i + 1) * salto
			img = Image.new("RGBA", size=size, color=(0, 0, 0, 0))
			draw = ImageDraw.Draw(img)
			bbox = draw.textbbox((0, 0), texto, font=ImageFont.truetype(fonte_unicode, 70))
			text_x = (size[0] - (bbox[2] - bbox[0])) // 2
			text_y = (size[1] - (bbox[3] - bbox[1])) // 2 - 100
			draw.text((text_x, text_y), texto, font=ImageFont.truetype(fonte_unicode, 70), fill="white")
			img.save(f"temp_text.png")
			clip = (ImageClip(f"temp_text.png").set_duration(salto).set_position("center").fadein(1).set_start(inicio))
			textos_saudacoes.append(clip)
			os.remove(f"temp_text.png")

		inferior_intro = CompositeVideoClip([fundo, *textos_saudacoes, slogan_clip, emoji])
		compose_intro = clips_array([[video_intro], [inferior_intro]])
		compose_intro = compose_intro.set_audio(video_intro.audio)

		log_info = "F4"
		# Composição OUTRO
		video_outro = VideoFileClip(os.path.join(caminho, outro)).subclip(0, 10).resize(size)
		fundo = ColorClip(size=size, color=(0, 0, 0), duration=video_outro.duration)
		slogan_clip = fnc_gerar_texto(texto=leg_default['slogan'],tamanho=70,cor='yellow',fonte=fonte_atma,dimensao=(1080, 100),tempo = 10).set_position(("center", "top"))
		emoji = ImageClip(emoji_timido).set_duration(video_outro.duration).set_position(("center", "bottom")).resize(0.5)
		clip_sup = TextClip("Agradecimentos aos mestres:", fontsize=70,	font=fonte_atma, color='white',	size=size, method='caption').set_duration(video_outro.duration).set_position(("center",-300))

		textos_citacao = []
		for i, texto in enumerate(citacoes[:2]):
			clip = TextClip(texto, fontsize=70,	font=fonte_atma, color='white',	size=(size[0] - 40, None), method='caption').set_duration(video_outro.duration)
			y = size[1] - (len(citacoes) - i) * 100
			textos_citacao.append(clip.set_position(("center", y)))

		salto = 2
		textos_agradece = []
		for i, texto in enumerate(agradece):
			inicio = salto + i * salto
			fonte = ImageFont.truetype(fonte_unicode, 70)
			img = Image.new("RGBA", size=size, color=(0, 0, 0, 0))
			draw = ImageDraw.Draw(img)
			text_size = draw.textbbox((0, 0), texto, font=fonte)
			text_height = text_size[3] - text_size[1]
			text_y = (img.height - text_height) // 2 - 100
			text_width = text_size[2] - text_size[0]
			text_x = (img.width - text_width) // 2
			draw.text((text_x, text_y), texto, font=fonte, fill="white")
			img.save(f"temp_text.png")
			clip = ImageClip(f"temp_text.png").set_duration(salto)
			clip = clip.set_position("center").fadein(1)
			textos_agradece.append(clip.set_start(inicio))
			os.remove(f"temp_text.png")

		superior_outro = CompositeVideoClip([video_outro, clip_sup, *textos_citacao])
		inferior_outro = CompositeVideoClip([fundo, *textos_agradece, slogan_clip, emoji])
		compose_outro = clips_array([[superior_outro], [inferior_outro]])
		compose_outro = compose_outro.set_audio(video_outro.audio)

		log_info = "F5"
		# Composição PRINCIPAL
		video_sup= (VideoFileClip(os.path.join(caminho, arquivo)).resize(size))
		video_inf = (VideoFileClip(os.path.join(caminho, inferior)).subclip(0, video_sup.duration).resize(size))

		num_partes = int(video_sup.duration // parte_duracao) + 1
		textos_partes = []
		for i in range(num_partes):
			if i == num_partes - 1:
				texto_duracao = video_sup.duration - (i * parte_duracao)  # Duração restante no vídeo
			else:
				texto_duracao = parte_duracao
			texto_parte = TextClip(f'parte {i + 1}', color='yellow',stroke_color='black', fontsize=70, font='Arial')
			texto_parte = (texto_parte.set_duration(texto_duracao).set_position(('right', 'bottom')).set_start(i * parte_duracao).set_end(i * parte_duracao + texto_duracao))
			textos_partes.append(texto_parte)

		texto_inferior = TextClip(citacoes[-1], color='yellow',stroke_color='black', fontsize=70, font='Arial')
		texto_inferior = texto_inferior.set_duration(video_sup.duration).set_position((0, 800))

		log_info = "F6"
		compose_01 = clips_array([[video_sup], [video_inf]])

		log_info = "F7"
		if not os.path.exists(os.path.join(caminho,traducao)):
			prc_TraduzLetra(caminho, legenda, idioma)
		legendas_musica = fnc_carregar_legendas_lrc(os.path.join(caminho, legenda),	float(leg_detalhe['inicio_legenda']), size, duracao_maxima=video_sup.duration)
		traducao_musica = fnc_carregar_legendas_lrc(os.path.join(caminho, traducao), float(leg_detalhe['inicio_legenda']), size, duracao_maxima=video_sup.duration)
		compose_main = CompositeVideoClip([compose_01, *textos_partes, texto_inferior, *legendas_musica, *traducao_musica])
		compose_main = compose_main.set_audio(video_sup.audio)
		if compose_main.size != (1080, 1620):
			raise ValueError(f"Tamanho final incorreto: {compose_main.size}, esperado: (1080, 810 x 2)")

		log_info = "F8"
		compose_final = concatenate_videoclips([compose_intro, compose_main, compose_outro])

		log_info = "F9"
		texto_faixa = TextClip(arquivo.replace('.mp4', ''), color='white', stroke_color='white', fontsize=40, font='Arial', size=(1080, 300))
		texto_faixa = texto_faixa.set_duration(compose_final.duration)
		texto_faixa = texto_faixa.set_position(("left", "bottom"))
		compose_youtube = CompositeVideoClip([compose_final, texto_faixa], size=(1080, 1920))
		compose_tiktok = compose_youtube.fx(vfx.speedx, factor=2.0)
		compose_youtube.write_videofile(os.path.join(pasta_destino, 'YTB_' + arquivo), fps=24, threads=4)
		compose_tiktok.write_videofile(os.path.join(pasta_destino, 'TKT_' + arquivo), fps=24, threads=4)

		log_info = "F10"
		fnc_dividir_fixo(os.path.join(os.path.dirname(caminho), 'YTB_' + arquivo), 60)
		fnc_gerar_documento(arquivo, pasta_destino, leg_detalhe, tags, prefixo_creditos, descricao_padrao)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	finally:
		pass

	return {"Resultado": 'Arquivo gerado com sucesso', 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_teste_dmb():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	lista = []
	processo_banda = json_caminho('Json_VideosDrumeibes')
	diretorio_banda = os.path.join(processo_banda['Diretorio'])
	caminho_drumeibes = json_caminho('Json_Drumeibes')
	doc_default = json_dados(os.path.join(caminho_drumeibes['Diretorio'], caminho_drumeibes['Arquivo']))
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		lista = fnc_buscar_processar(diretorio_banda, 'Drumeibes')
		if lista["Resultado"]:
			exec_info += f"\t\t\t\tDRUMEIBES COM Arquivos a processar:\n"
			for caminho in lista["Resultado"]:
				caminho_arquivo = os.path.dirname(caminho)
				nome_arquivo = os.path.basename(caminho)
				nome_inferior = nome_arquivo.replace('Drumeibes','INFERIOR')
				nome_lrc = os.path.splitext(nome_arquivo.replace('Drumeibes','LEGENDA'))[0] + '.lrc'
				nome_intro = doc_default['template_intro']
				nome_final = doc_default['template_outro']
				if (    os.path.exists(os.path.join(caminho_arquivo, nome_arquivo))
					and os.path.exists(os.path.join(caminho_arquivo, nome_inferior))
					and os.path.exists(os.path.join(caminho_arquivo, nome_lrc))
					and os.path.exists(os.path.join(caminho_arquivo, nome_intro))
					and os.path.exists(os.path.join(caminho_arquivo, nome_final))
				):
					exec_info += f"\t\t\t\t{nome_arquivo} SEM ARQUIVOS PENDENTES.\n"
					doc_detalhe = fnc_RetornaDocGoogle(os.path.splitext(nome_arquivo)[0])
					winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms
					print('Iniciando: ', doc_detalhe)
					resultado = fnc_montar_teste(caminho_arquivo, nome_arquivo, nome_lrc, nome_inferior, doc_detalhe['Resultado']['Resultado'])
					winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms
					winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms
					exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
					exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
					exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
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


def prc_processa_dmb():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	lista = []

	processo_banda = json_caminho('Json_VideosDrumeibes')
	diretorio_banda = os.path.join(processo_banda['Diretorio'])
	caminho_drumeibes = json_caminho('Json_Drumeibes')
	doc_default = json_dados(os.path.join(caminho_drumeibes['Diretorio'], caminho_drumeibes['Arquivo']))
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		lista = fnc_buscar_processar(diretorio_banda, 'Drumeibes')
		if lista["Resultado"]:
			exec_info += f"\t\t\t\tDRUMEIBES COM Arquivos a processar:\n"
			for caminho in lista["Resultado"]:
				caminho_arquivo = os.path.dirname(caminho)
				nome_arquivo = os.path.basename(caminho)
				nome_inferior = nome_arquivo.replace('Drumeibes','INFERIOR')
				nome_lrc = os.path.splitext(nome_arquivo.replace('Drumeibes','LEGENDA'))[0] + '.lrc'
				nome_intro = doc_default['template_intro']
				nome_final = doc_default['template_outro']
				if (    os.path.exists(os.path.join(caminho_arquivo, nome_arquivo))
					and os.path.exists(os.path.join(caminho_arquivo, nome_inferior))
					and os.path.exists(os.path.join(caminho_arquivo, nome_lrc))
					and os.path.exists(os.path.join(caminho_arquivo, nome_intro))
					and os.path.exists(os.path.join(caminho_arquivo, nome_final))
				):
					exec_info += f"\t\t\t\t{nome_arquivo} SEM ARQUIVOS PENDENTES.\n"
					doc_detalhe = fnc_RetornaDocGoogle(os.path.splitext(nome_arquivo)[0])
					winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms
					print('Iniciando: ', doc_detalhe)
					resultado = fnc_montar_padrao(caminho_arquivo, nome_arquivo, nome_lrc, nome_inferior, nome_intro, nome_final, doc_default, doc_detalhe['Resultado']['Resultado'])
					winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms
					winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms
					exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
					exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
					exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
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


def prc_processa_fut():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	lista = []
	processo_futes = json_caminho('Json_VideosFute')
	diretorio_futes = os.path.join(processo_futes['Diretorio'])
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
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


def main():
	prc_processa_dmb()


if __name__ == "__main__":
	main()
	print(exec_info)