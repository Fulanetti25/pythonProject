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


def fnc_gerar_xpath(driver, x, y):
	try:
		# Marca o elemento temporariamente
		info_elemento = driver.execute_script(f"""
			var el = document.elementFromPoint({x}, {y});
			if (el) {{
				el.setAttribute('data-temp-id', 'fallback-element');
				return {{
					'tag': el.tagName,
					'id': el.id,
					'class': el.className,
					'outer': el.outerHTML.slice(0, 300)
				}};
			}} else {{
				return null;
			}}
		""")

		if not info_elemento:
			print(f"[ERRO] Nenhum elemento encontrado nas coordenadas ({x}, {y})")
			return None

		print(
			f"[DEBUG] Elemento capturado no ponto ({x},{y}): <{info_elemento['tag']}> id='{info_elemento['id']}' class='{info_elemento['class']}'")
		print(f"[DEBUG] HTML parcial: {info_elemento['outer']}")
		print(f"[DEBUG] Elemento visual identificado: <{info_elemento['tag']}>")

		xpath = driver.execute_script("""
			function getElementXPath(elt) {
				var path = "";
				for (; elt && elt.nodeType === 1; elt = elt.parentNode) {
					var index = 1;
					for (var sib = elt.previousSibling; sib; sib = sib.previousSibling) {
						if (sib.nodeType === 1 && sib.tagName === elt.tagName) index++;
					}
					var tagName = elt.tagName.toLowerCase();
					var segment = tagName + "[" + index + "]";
					path = "/" + segment + path;
				}
				return path;
			}
			var el = document.querySelector('[data-temp-id="fallback-element"]');
			if (el) {
				return getElementXPath(el);
			} else {
				return null;
			}
		""")

		if xpath:
			print(f"[DEBUG] XPath gerado por JavaScript: {xpath}")
			try:
				teste = driver.find_element(By.XPATH, xpath)
				if teste and teste.is_displayed():
					print(f"[DEBUG] XPath testado com sucesso: {xpath}")
					return xpath
			except:
				print(f"[ERRO] XPath gerado não encontrado ou não visível: {xpath}")
				return None
		else:
			print("[ERRO] JavaScript não conseguiu gerar o XPath.")
			return None

		# Monta XPath absoluto manualmente
		components = []
		current = elemento
		while current.tag_name.lower() != 'html':
			tag = current.tag_name.lower()
			parent = current.find_element(By.XPATH, "..")
			siblings = parent.find_elements(By.XPATH, f"./{tag}")
			if len(siblings) == 1:
				components.append(f"{tag}")
			else:
				index = 1
				for sib in siblings:
					if sib == current:
						break
					index += 1
				components.append(f"{tag}[{index}]")

			current = parent
		print(f"[DEBUG] Componentes capturados para o XPath: {components}")
		if components:
			components.append("html")
			components.reverse()
			xpath = "/" + "/".join(components)

			# Validação
			try:
				teste = driver.find_element(By.XPATH, xpath)
				if teste and teste.is_displayed():
					print(f"[DEBUG] XPath testado com sucesso: {xpath}")
					return xpath
				else:
					print(f"[ERRO] XPath gerado não corresponde a um elemento visível.")
					return None
			except Exception as e:
				print(f"[ERRO] XPath gerado não foi encontrado: {xpath}")
				return None
		else:
			print("[ERRO] XPath não pôde ser construído. Lista de componentes vazia.")
			return None

	except Exception as e:
		import traceback
		trace = traceback.format_exc()
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=trace, var_erro=True)
		return None

	finally:
		try:
			driver.execute_script("""
				var el = document.querySelector('[data-temp-id="fallback-element"]');
				if (el) el.removeAttribute('data-temp-id');
			""")
		except:
			pass


def fnc_localiza_objeto(driver, nome_objeto, timeout=30):
	import cv2
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC

	mapa_objetos = json_caminho('Json_Mapa_Objetos')
	mapa_imagens = json_caminho('Local_Asset')
	caminho_json = os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo'])
	dados_objetos = json_dados(caminho_json)

	xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == nome_objeto), None)
	# 1. Tenta localizar com XPath (caso exista)
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

	# 2. Fallback por imagem (sempre que XPath estiver vazio ou falhar)
	print(f"[INFO] Executando fallback visual para '{nome_objeto}'...")
	screenshot_path = os.path.join(mapa_imagens['Diretorio'], "tela_atual.png")
	time.sleep(5)
	pyautogui.screenshot(screenshot_path)
	screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)

	for nome_arquivo in os.listdir(mapa_imagens['Diretorio']):
		if nome_objeto.lower() in nome_arquivo.lower() and nome_arquivo.lower().endswith(('.png')):
			caminho_template = os.path.join(mapa_imagens['Diretorio'], nome_arquivo)
			local = pyautogui.locateOnScreen(caminho_template, confidence=0.85)
			if local:
				print(f"[INFO] Imagem localizada na tela para '{nome_objeto}' em: {local}")
				centro = pyautogui.center(local)
				try:
					# Converte coordenadas da tela para a viewport (ajuste conforme necessário)
					x_tela, y_tela = centro.x, centro.y
					el_tag = driver.execute_script(f"""
					    var el = document.elementFromPoint({x_tela}, {y_tela});
					    if (el) {{
					        el.setAttribute('data-temp-id', 'fallback-element');
					        return el.tagName;
					    }} else {{
					        return null;
					    }}
					""")
					print(f"[DEBUG] Tag HTML capturada no ponto ({x_tela},{y_tela}): {el_tag}")
					if not el_tag:
						print("[ERRO] Nenhum elemento encontrado visualmente.")
						return None
					novo_xpath = fnc_gerar_xpath(driver, x_tela, y_tela)

					print(f"[INFO] XPath gerado a partir da imagem de '{nome_objeto}': {novo_xpath}")
					breakpoint()
					# if novo_xpath:
					# 	prc_atualiza_xpath_json(nome_objeto, novo_xpath)
					# 	log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=f"XPath alternativo atualizado para '{nome_objeto}': {novo_xpath}")
					# 	elemento_novo = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, novo_xpath)))
					# 	return elemento_novo
				except:
					print(f"[ERRO] Falha ao localizar '{nome_objeto}' por XPath e imagem.")
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
					print(anexo)
					os.system(f'echo {anexo} | clip')
					pyautogui.hotkey('ctrl', 'v')
					pyautogui.press('enter')

				if anexo:
					log_info = "F6"
					nome_objeto = 'BIG_ARROW'
					print('Seta Grande')
				else:
					log_info = "F7"
					nome_objeto = 'SEND_ARROW'
				objeto = fnc_localiza_objeto(driver, nome_objeto, timeout=30)
				objeto.click()
				print('Enviou')
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