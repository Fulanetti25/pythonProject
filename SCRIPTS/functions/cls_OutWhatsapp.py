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


def fnc_gerar_xpath(driver, x, y, width, height):
	log_info = "F1"
	varl_detail = None
	try:
		log_info = "F2"
		script = """
		function getXPath(element) {
			if (element.id !== '') {
				return 'id(\"' + element.id + '\")';
			}
			if (element === document.body) {
				return element.tagName.toLowerCase();
			}
			var ix = 0;
			var siblings = element.parentNode.childNodes;
			for (var i=0; i<siblings.length; i++) {
				var sibling = siblings[i];
				if (sibling === element) {
					return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
				}
				if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
					ix++;
				}
			}
		}

		var areaX = arguments[0];
		var areaY = arguments[1];
		var areaW = arguments[2];
		var areaH = arguments[3];

		var elements = [];
		var allElements = document.querySelectorAll('*');

		function intersects(r1, r2) {
			return !(r2.left > r1.right ||
					 r2.right < r1.left ||
					 r2.top > r1.bottom ||
					 r2.bottom < r1.top);
		}

		var areaRect = {
			left: areaX,
			top: areaY,
			right: areaX + areaW,
			bottom: areaY + areaH
		};

		for (var i=0; i<allElements.length; i++) {
			var el = allElements[i];
			var rect = el.getBoundingClientRect();

			// ignorar elementos sem tamanho visível
			if (rect.width === 0 || rect.height === 0) continue;

			// checar intersecção da bounding box com a área da imagem
			if (intersects(areaRect, rect)) {
				elements.push({
					xpath: getXPath(el),
					tag: el.tagName.toLowerCase(),
					text: el.innerText ? el.innerText.trim() : ''
				});
			}
		}

		return elements;
		"""
		log_info = "F3"
		elementos = driver.execute_script(script, x, y, width, height)

		log_info = "F4"
		if not elementos:
			print(f"[WARN] Nenhum elemento encontrado na área ({x},{y},{width},{height})")
			return None

		print(f"[INFO] Elementos encontrados na área ({x},{y},{width},{height}):")
		for i, el in enumerate(elementos):
			print(f" {i+1}. XPath: {el['xpath']}")
			print(f"    Tipo: {el['tag']}")
			print(f"    Texto: {el['text'][:50]}")  # limitar texto para até 50 caracteres

		return elementos

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise


def fnc_fallback_imagem(driver, nome_objeto, caminho):
	import cv2

	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		screenshot_path = os.path.join(caminho, "tela_atual.png")
		time.sleep(5)
		pyautogui.screenshot(screenshot_path)
		screenshot = cv2.imread(screenshot_path)

		mapa_imagens = json_caminho('Local_Asset')

		log_info = "F3"
		for nome_arquivo in os.listdir(caminho):
			if nome_objeto.lower() in nome_arquivo.lower() and nome_arquivo.lower().endswith('.png'):
				caminho_template = os.path.join(mapa_imagens['Diretorio'], nome_arquivo)
				template = cv2.imread(caminho_template)

				if template is None or screenshot is None:
					print(f"[ERRO] Falha ao carregar imagens para '{nome_objeto}'")
					return None

				res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
				min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

				limiar = 0.85
				if max_val >= limiar:
					top_left = max_loc
					h, w = template.shape[:2]
					bottom_right = (top_left[0] + w, top_left[1] + h)
					cv2.rectangle(screenshot, top_left, bottom_right, (0, 0, 255), 2)
					cv2.imwrite(screenshot_path, screenshot)
					print(f"[INFO] Imagem localizada na screenshot para '{nome_objeto}' em: {top_left} com confiança {max_val:.2f}")
					fnc_gerar_xpath(driver, top_left[0], top_left[1], w, h)
				else:
					print(f"[WARN] Imagem '{nome_objeto}' não localizada na screenshot com confiança mínima {limiar}")
		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise


def fnc_localiza_objeto(driver, nome_objeto, timeout=30):
	log_info = "F1"
	varl_detail = None
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC

	try:
		log_info = "F2"
		mapa_objetos = json_caminho('Json_Mapa_Objetos')
		mapa_imagens = json_caminho('Local_Asset')
		caminho_json = os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo'])
		dados_objetos = json_dados(caminho_json)

		log_info = "F3"
		xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == nome_objeto), None)
		if xpath:
			try:
				elemento = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
				if elemento.is_displayed() and elemento.is_enabled():
					print(f"[INFO] Elemento localizado com XPath original para '{nome_objeto}'")
					return elemento
				else:
					print(f"[WARN] Elemento encontrado com XPath mas não está visível ou habilitado para '{nome_objeto}'")
					raise Exception("Elemento não interativo")
			except Exception:
				log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=f"XPath inválido ou elemento não interativo para '{nome_objeto}'", var_erro=True)
		else:
			print(f"[INFO] Executando fallback visual para '{nome_objeto}'...")
			fnc_fallback_imagem(driver, nome_objeto, mapa_imagens['Diretorio'])
		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise


def prc_atualiza_xpath_json(nome_objeto, novo_xpath):
	mapa_objetos = json_caminho('Json_Mapa_Objetos')
	caminho_json = os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo'])
	json_atualiza(caminho_json, 'objetos', nome_objeto, 'Xpath', novo_xpath)


def fnc_ReprocessarFalhaWA():
	log_info = "F1"
	varl_detail = None
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_path = os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo'])

	try:
		log_info = "F2"
		fila = json_dados(falhas_path)

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
			json_limpa(falhas_path, 'WHATSAPP')

	return {"Resultado": "Fila Reprocessada", 'Status_log': log_info, 'Detail_log': varl_detail}


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
			json_limpa(filas_path, 'WHATSAPP')

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
	options.add_argument("--start-maximized")

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