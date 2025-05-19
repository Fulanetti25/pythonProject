import inspect
import time
import psutil
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados


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
		print(f"{log_info}, {e}")

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
		print(f"{log_info}, {e}")

	finally:
		pass

	return {"Resultado": "Conexão fechada", 'Status_log': log_info, 'Detail_log': varl_detail}


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
		print(f"{log_info}, {e}")


def fnc_fallback_imagem(driver, nome_objeto, caminho):
	import cv2
	import pyautogui

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
				else:
					print(f"[WARN] Imagem '{nome_objeto}' não localizada na screenshot com confiança mínima {limiar}")
		log_info = "F0"

	except Exception as e:
		print(f"{log_info}, {e}")


if __name__ == '__main__':
	conn_obj = None
	conexao = fnc_connect_whats()
	conn_obj = conexao.get("Resultado")
	conn_log = conexao.get("Detail_log")

	try:
		conn_obj.get("https://web.whatsapp.com")
		time.sleep(10)

		numero = 'PSM - ADMINISTRAÇÃO'
		mensagem = 'teste2'

		nome_objeto = 'SEARCH_BOX'
		objeto = fnc_localiza_objeto(conn_obj, nome_objeto, timeout=30)
		objeto.click()
		objeto.send_keys(numero)
		objeto.send_keys(Keys.ENTER)

		nome_objeto = 'PLUS_BUTTON'
		objeto = fnc_localiza_objeto(conn_obj, nome_objeto, timeout=30)
		objeto.click()

		nome_objeto = 'TEST_BUTTON'
		objeto = fnc_localiza_objeto(conn_obj, nome_objeto, timeout=30)
		objeto.click()

	except Exception as e:
			print(f"{e}")

	finally:
		fnc_close_whats(conn_obj)