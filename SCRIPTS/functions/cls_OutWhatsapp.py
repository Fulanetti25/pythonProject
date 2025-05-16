import traceback
import inspect
import time
import psutil
import os
import logging
import pyautogui
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados, json_registra, json_limpa, json_atualiza
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def fnc_gerar_xpath(elemento):
	try:
		components = []
		current = elemento
		while current is not None:
			parent = current.find_element("xpath", "..")
			siblings = parent.find_elements("xpath", f"./{current.tag_name}")
			if len(siblings) == 1:
				components.append(f"{current.tag_name}")
			else:
				index = siblings.index(current) + 1
				components.append(f"{current.tag_name}[{index}]")
			if current.tag_name.lower() == "html":
				break
			current = parent
		components.reverse()
		xpath = "/" + "/".join(components)
		return xpath
	except Exception as e:
		print(f"[ERRO] Falha ao gerar XPath: {e}")
		return None


def fnc_localiza_objeto(driver, nome_objeto, timeout=30):
	import pyautogui
	import cv2
	import numpy as np
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC

	log_info = "F1"
	varl_detail = None

	log_info = "F2"
	mapa_objetos = json_caminho('Json_Mapa_Objetos')
	mapa_imagens = json_caminho('Asset_Images')
	caminho_json = os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo'])
	dados_objetos = json_dados(caminho_json)

	# Busca XPath no JSON pelo nome do objeto
	xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == nome_objeto), None)
	if not xpath:
		print(f"[ERRO] XPath não encontrado no JSON para o objeto '{nome_objeto}'")
		return None

	while True:
		try:
			# Tenta encontrar elemento pelo XPath salvo
			elemento = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
			if elemento.is_displayed() and elemento.is_enabled():
				return elemento
			raise Exception("Elemento localizado, mas não visível ou habilitado")
		except Exception:
			detalhe_erro = f"XPath inválido ou elemento não interativo para '{nome_objeto}'"
			log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=detalhe_erro, var_erro=True)

			screenshot_path = os.path.join(mapa_imagens['Diretorio'], "tela_atual.png")
			pyautogui.screenshot(screenshot_path)

			for nome_arquivo in os.listdir(mapa_imagens['Diretorio']):
				if nome_objeto.lower() in nome_arquivo.lower() and nome_arquivo.lower().endswith(('.png', '.jpg')):
					imagem_modelo_path = os.path.join(mapa_imagens['Diretorio'], nome_arquivo)
					local = pyautogui.locateOnScreen(imagem_modelo_path, confidence=0.85)
					if local:
						centro = pyautogui.center(local)
						pyautogui.moveTo(centro.x, centro.y)
						pyautogui.click()
						try:
							js_code = f"return document.elementFromPoint({centro.x}, {centro.y}).outerHTML"
							html = driver.execute_script(js_code)
							elemento_html = driver.execute_script(f"return document.elementFromPoint({centro.x}, {centro.y})")
							novo_xpath = fnc_gerar_xpath(elemento_html)
							prc_atualiza_xpath_json(nome_objeto, novo_xpath)
							detalhe_log = f"XPath alternativo atualizado para '{nome_objeto}': {novo_xpath}"
							log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=detalhe_log)
							elemento_novo = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, novo_xpath)))
							return elemento_novo
						except Exception as e:
							log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=f"Erro no fallback visual: {e}", var_erro=True)
							pass

			# 3b) Se nenhuma imagem servir
			log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=f"Nenhuma imagem corresponde ao objeto '{nome_objeto}'", var_erro=True)
			return None


def prc_atualiza_xpath_json(nome_objeto, novo_xpath):
	mapa_objetos = json_caminho('Json_Mapa_Objetos')
	caminho_json = os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo'])
	json_atualiza(caminho_json, 'objetos', nome_objeto, 'Xpath', novo_xpath)


def fnc_ProcessarFila():
	log_info = "F1"
	varl_detail = None
	filas_sql = json_caminho('Json_Fila_WA')
	filas_path = os.path.join(filas_sql['Diretorio'], filas_sql['Arquivo'])

	try:
		log_info = "F2"
		fila = json_dados(filas_path)

		log_info = "F3"
		if fila:
			prc_executa_fila(fila)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		if log_info == "F0":
			pass
			# json_limpa(filas_path)

	return {"Resultado": "Fila Reprocessada", 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_executa_fila(fila):
	log_info = "F1"
	varl_detail = None
	conn_obj = None

	try:
		log_info = "F2"
		conexao = fnc_connect_whats()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		fnc_envia_fila(conn_obj, fila)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		fnc_close_whats(conn_obj)

	return {"Resultado": "Executado", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_envia_fila(driver, fila):
	log_info = "F1"
	varl_detail = None
	result = []
	xpath = None
	driver.get("https://web.whatsapp.com")
	time.sleep(10)

	try:
		for item in fila:
			try:
				numero = item['numero']
				mensagem = item['mensagem']
				anexo = item['anexo']

				log_info = "F2"
				nome_objeto = 'SEARCH_BOX'
				objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
				objeto.click()
				objeto.send_keys(numero)
				objeto.send_keys(Keys.ENTER)

				log_info = "F3"
				nome_objeto = 'MESSAGE_BOX'
				objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
				for linha in mensagem.split('\n'):
					objeto.send_keys(linha)
					objeto.send_keys(Keys.SHIFT, Keys.ENTER)

				if anexo:
					log_info = "F4"
					nome_objeto = 'PLUS_BUTTON'
					objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
					objeto.click()

					nome, extensao = os.path.splitext(anexo)
					if extensao == '.vcf':
						log_info = "F5.1"
						nome_objeto = 'DOC_OPTION'
					elif extensao == '.png':
						log_info = "F5.2"
						nome_objeto = 'IMG_OPTION'
					objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
					objeto.click()

					time.sleep(5)
					os.system(f'echo {anexo} | clip')
					pyautogui.hotkey('ctrl', 'v')
					pyautogui.press('enter')

				if anexo:
					log_info = "F6"
					nome_objeto = 'BIG_ARROW'
				else:
					log_info = "F7"
					nome_objeto = 'SEND_ARROW'
				objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
				objeto.click()
				time.sleep(10)

				result.append({'numero': numero, 'status': 'OK'})

			except Exception as e_item:
				varl_detail = f"{log_info}, {e_item}"
				log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
				fnc_SalvarFalha('WHATSAPP', varl_detail, numero, mensagem, anexo)
				result.append({'numero': numero, 'status': 'FALHA'})
				continue  # segue com o próximo item da fila

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F0"
		raise

	finally:
		pass

	return {"Resultado": result, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_connect_whats():
	log_info = "F1"
	varl_detail = None

	for proc in psutil.process_iter(attrs=['pid', 'name']):
		if 'chrome' in proc.info['name'].lower():
			os.kill(proc.info['pid'], 9)

	options = webdriver.ChromeOptions()
	caminho = json_caminho('Chrome_Profile')
	options.add_argument(f"user-data-dir={caminho['Diretorio']}")
	options.add_argument(f"profile-directory={caminho['Arquivo']}")

	try:
		log_info = "F2"
		driver = webdriver.Chrome(options=options)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail,
					 var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": driver, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_close_whats(driver):
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		if driver:
			driver.quit()
		time.sleep(5)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	finally:
		pass

	return {"Resultado": "Conexão fechada", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_SalvarFalha(server, varl_detail, numero, mensagem, anexo):
	log_info = "F1"
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_dados = json_dados(os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

	try:
		log_info = "F2"
		pilha = falhas_dados if falhas_dados else []
		falha = {
			"server": server,
			"log": varl_detail,
			"numero": numero,
			"mensagem": mensagem,
			"anexo": anexo,
		}

		if falha not in pilha:
			pilha.append(falha)
			json_registra(pilha, arquivo=os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	finally:
		pass

	return {"Resultado": "Inserido na pilha", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_SalvarFila(numero, mensagem, anexo):
	log_info = "F1"
	varl_detail = None
	falhas_sql = json_caminho('Json_Fila_WA')
	falhas_dados = json_dados(os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

	try:
		log_info = "F2"
		pilha = falhas_dados if falhas_dados else []
		fila = {
			"Data": datetime.now().isoformat(),
			"numero": numero,
			"mensagem": mensagem,
			"anexo": anexo,
		}

		if fila not in pilha:
			pilha.append(fila)
			json_registra(pilha, arquivo=os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": "Inserido na fila", 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = fnc_ProcessarFila()
		exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
		exec_info += "\t\tMF\n"
		varg_erro = False

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