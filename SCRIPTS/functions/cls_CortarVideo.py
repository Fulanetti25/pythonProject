import winsound
import traceback
import inspect
import logging
import shutil
import subprocess
import os
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


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
	arquivos = sorted(fnc_buscar_arquivos(diretorio, incluir_subpastas=True))
	print(arquivos)

	videos = [arquivo for arquivo in arquivos if arquivo.lower().endswith(".mp4")]

	if not videos:
		print("Nenhum vídeo encontrado no diretório.")
		return

	lista_txt = os.path.join(diretorio, "lista_videos.txt")
	with open(lista_txt, "w", encoding="utf-8") as f:
		for video in videos:
			# 🔹 Corrigido: Formato correto para FFmpeg
			f.write(f"file '{video.replace('\\', '/')}'\n")

	ultima_subpasta = max([os.path.join(diretorio, subpasta) for subpasta in os.listdir(diretorio)
						   if os.path.isdir(os.path.join(diretorio, subpasta))], key=os.path.getmtime)
	nome_pasta = os.path.basename(ultima_subpasta)
	arquivo_saida = os.path.join(diretorio, f"{nome_pasta}_bruto.mp4")

	comando = [
		"ffmpeg", "-f", "concat", "-safe", "0", "-i", lista_txt,
		"-c", "copy", arquivo_saida, "-y"
	]

	try:
		cwd = os.path.abspath(diretorio)  # 🔹 Corrigido: Define cwd antes de usá-lo
		subprocess.run(comando, check=True, cwd=cwd)
		print(f"Vídeo unificado criado: {arquivo_saida}")
	except subprocess.CalledProcessError as e:
		print(f"Erro ao unir os vídeos: {e}")

	os.remove(lista_txt)

	if os.path.exists(arquivo_saida):
		pass
		# shutil.rmtree(ultima_subpasta)  # Remove a última pasta e todo o seu conteúdo
		# print(f"Pasta {ultima_subpasta} removida.")


def fnc_cortes_preto(arquivo: str):
	# Definindo o nome do arquivo de saída
	diretorio = os.path.dirname(arquivo)
	arquivo_saida = os.path.join(diretorio, "20250302_highlights.mp4")

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


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	# processo = json_caminho('Json_VideosDrumeibes')
	processo = json_caminho('Json_VideosFute')
	diretorio = os.path.join(processo['Diretorio'])
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		# resultado = fnc_buscar_processar(diretorio)
		# fnc_dividir_fixo(os.path.join(mapa_objetos['Diretorio'], arquivo_processar),arquivo_caminho, 15)
		# Montar inicio, fim e Legendar Video
		# resultado = fnc_unificar_videos(diretorio)
		arquivo = os.path.join(diretorio, '20250302_bruto.mp4')
		resultado = fnc_cortes_preto(arquivo)
		if resultado:
			exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
			exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
			exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
			exec_info += "\t\tMF\n"
			varg_erro = False
		else:
			print(f"Processo não executado")


	except Exception as e:
		exec_info += "\t\t\tM99\n"
		exec_info += f"Traceback: {traceback.format_exc()}"
		varg_erro = True
		raise

	finally:
		exec_info += "LF\n"
		log_registra(varg_modulo, inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)
	winsound.Beep(1000, 500)  # Frequência de 1000 Hz por 500 ms
