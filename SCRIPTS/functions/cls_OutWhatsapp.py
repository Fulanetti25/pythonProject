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
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados, json_registra, json_deleta, json_atualiza
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def fnc_limpa_campos(driver, nome_objeto, timeout=10):
	try:
		elemento = fnc_localiza_objeto(driver, nome_objeto, timeout)
		if not elemento:
			raise Exception("Elemento não encontrado.")
		tag = elemento.tag_name.lower()
		if tag in ['input', 'textarea']:
			elemento.clear()
		else:
			elemento.send_keys(Keys.CONTROL + "a")
			elemento.send_keys(Keys.DELETE)

		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=f"Campo '{nome_objeto}' limpo com sucesso.", var_erro=False)

	except Exception as e:
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=f"Erro ao limpar o campo '{nome_objeto}': {e}", var_erro=True)


def fnc_gerar_xpath(driver, x, y, width, height, filtro_texto=None):
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
		if filtro_texto:
			elementos_filtrados = [el for el in elementos if filtro_texto.lower() in el['text'].lower()]
		else:
			elementos_filtrados = elementos
		if not elementos_filtrados:
			print(f"[WARN] Nenhum elemento encontrado com o texto '{filtro_texto}' na área ({x},{y},{width},{height})")
			return None
		print(f"[INFO] Elementos filtrados na área ({x},{y},{width},{height}):")
		for i, el in enumerate(elementos_filtrados):
			print(f" {i+1}. XPath: {el['xpath']}")
			print(f"    Tipo: {el['tag']}")
			print(f"    Texto: {el['text'][:50]}")

		return elementos_filtrados


	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise


def fnc_fallback_imagem(driver, nome_objeto, caminho_asset, arquivo_dict):
	import cv2
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		screenshot_path = os.path.join(caminho_asset, "tela_atual.png")
		time.sleep(5)
		pyautogui.screenshot(screenshot_path)
		screenshot = cv2.imread(screenshot_path)

		log_info = "F3"
		for nome_arquivo in os.listdir(caminho_asset):
			if nome_objeto.lower() in nome_arquivo.lower() and nome_arquivo.lower().endswith('.png'):
				caminho_template = os.path.join(caminho_asset, nome_arquivo)
				template = cv2.imread(caminho_template)

				if template is None or screenshot is None:
					raise Exception(f"Erro ao carregar imagens para '{nome_objeto}'")

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

					# buscar texto associado ao nome do objeto
					texto_referencia = None
					dados_dict = json_dados(arquivo_dict)['objetos']
					for item in dados_dict:
						if item['Nome'] == nome_objeto:
							texto_referencia = item.get('Texto', None)
							break
					print('Buscando: ', texto_referencia)
					elementos = fnc_gerar_xpath(driver, top_left[0], top_left[1], w, h, texto_referencia)
					if elementos:
						print("[INFO] Elementos HTML detectados visualmente na região da imagem:")
						for idx, el in enumerate(elementos, start=1):
							print(f" {idx:02d}) XPath: {el['xpath']}")
							if 'texto' in el and el['texto']:
								print(f"     Texto: {el['texto']}")
							if 'tag' in el:
								print(f"     Tag: {el['tag']}")
						print("[INFO] Selecione e edite o JSON manualmente se necessário.")
					return elementos
				else:
					print(f"[WARN] Imagem '{nome_objeto}' não localizada com confiança mínima de {limiar}")
		raise Exception(f"Nenhum arquivo de imagem encontrado para '{nome_objeto}' no diretório '{caminho_asset}'.")

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
		arquivo_dict = os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo'])
		dados_objetos = json_dados(arquivo_dict)

		log_info = "F3"
		xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == nome_objeto), None)
		if xpath:
			try:
				elemento = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
				if elemento.is_displayed() and elemento.is_enabled():
					print(f"[INFO] Elemento localizado com XPath original para '{nome_objeto}'")
					return elemento
				else:
					print(f"[WARN] XPath encontrado, mas elemento não está visível ou habilitado: '{nome_objeto}'")
			except Exception as e:
				print(f"[ERRO] Falha ao localizar XPath '{xpath}' para '{nome_objeto}': {e}")

		log_info = "F99"
		print(f"[INFO] Executando fallback visual para '{nome_objeto}'...")
		elementos = fnc_fallback_imagem(driver, nome_objeto, mapa_imagens['Diretorio'], arquivo_dict)

		if not elementos or not isinstance(elementos, list) or len(elementos) == 0:
			raise Exception(f"Falha crítica: elemento '{nome_objeto}' não encontrado nem por XPath nem por imagem.")

		elemento_xpath = elementos[0].get('xpath')
		if not elemento_xpath:
			raise Exception(f"Falha crítica: fallback retornou estrutura inválida para '{nome_objeto}'.")

		try:
			print(f"[DEBUG] Tentando localizar XPath gerado: {elemento_xpath}")
			elemento = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, elemento_xpath)))
			if elemento.is_displayed() and elemento.is_enabled():
				print(f"[INFO] Elemento recuperado via fallback pelo XPath gerado.")
				return elemento
			else:
				raise Exception(f"Elemento localizado visualmente mas não está acessível.")
		except Exception as e:
			raise Exception(f"XPath localizado visualmente, mas elemento não acessível: {e}")

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name,	var_detalhe=varl_detail, var_erro=True)
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
			prc_executa_fila(falhas_path)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

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
			prc_executa_fila(filas_path)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

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


def fnc_envia_fila(driver, fila_path):
	log_info = "F1"
	varl_detail = None
	result = []
	driver.get("https://web.whatsapp.com")
	time.sleep(10)
	fila = json_dados(fila_path)

	try:
		for idx, item in enumerate(fila):
			try:
				data = item['data']
				server = item['server']
				numero = item['numero']
				mensagem = item['mensagem']
				anexo = item['anexo']

				log_info = "F2"
				nome_objeto = 'SEARCH_BOX'
				limpeza = fnc_limpa_campos(driver, nome_objeto)
				objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
				objeto.click()
				objeto.send_keys(numero)
				objeto.send_keys(Keys.ENTER)

				log_info = "F3"
				nome_objeto = 'MESSAGE_BOX'
				limpeza = fnc_limpa_campos(driver, nome_objeto)
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
					log_info = "F6.1"
					nome_objeto = 'BIG_ARROW'
				else:
					log_info = "F6.2"
					nome_objeto = 'SEND_ARROW'
				objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
				objeto.click()
				time.sleep(10)

				log_info = "F0"
				result.append({'numero': numero, 'status': log_info})
				json_deleta(fila_path, server, data)

			except Exception as e_item:
				varl_detail = f"{log_info}, {e_item}"
				log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
				json_deleta(fila_path, server, data)
				fnc_SalvarFalha(server, data, varl_detail, numero, mensagem, anexo)
				result.append({'numero': numero, 'status': 'FALHA'})
				continue

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


def fnc_SalvarFalha(server, data, varl_detail, numero, mensagem, anexo):
	log_info = "F1"
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_dados = json_dados(os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

	try:
		log_info = "F2"
		pilha = falhas_dados if falhas_dados else []
		falha = {
			"server": server,
			"data": data,
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
			"server": "WHATSAPP",
			"data": datetime.now().isoformat(),
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


def exe_OutWhatsapp():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = fnc_ProcessarFila()
		# resultado = fnc_ReprocessarFalhaWA()
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