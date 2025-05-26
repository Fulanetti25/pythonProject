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


def fnc_crop_template(template, margem):
	h, w = template.shape[:2]
	if h <= 2 * margem or w <= 2 * margem:
		return None  # Muito pequeno
	return template[margem:h - margem, margem:w - margem]


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
				pass
		else:
			print(f"[INFO] Executando fallback visual para '{nome_objeto}'...")
			fnc_fallback_imagem(driver, nome_objeto, mapa_imagens['Diretorio'])

		print(f"[ERRO] Objeto '{nome_objeto}' não localizado. Tentando limpar MESSAGE_BOX antes de abortar...")
		try:
			search_xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == 'MESSAGE_BOX'),None)
			if search_xpath:
				search_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
				search_box.click()
				search_box.send_keys(Keys.CONTROL + "a")
				search_box.send_keys(Keys.DELETE)
				print("[INFO] SEARCH_BOX limpa com sucesso.")
			else:
				print("[WARN] XPath de SEARCH_BOX não encontrado no JSON.")
		except Exception as e:
			print(f"[ERRO] Falha ao tentar limpar SEARCH_BOX: {e}")

		breakpoint()
		return None

		log_info = "F0"

	except Exception as e:
		print(f"{log_info}, {e}")


def fnc_gerar_xpath(driver, top_left, bottom_right):
	from selenium.webdriver.common.by import By

	print("\n[INFO] Iniciando varredura de XPaths visíveis na região localizada...")

	x1, y1 = top_left
	x2, y2 = bottom_right

	elementos = driver.find_elements(By.XPATH, "//*")
	print(f"[INFO] Total de elementos na página: {len(elementos)}")

	elementos_na_area = []
	for el in elementos:
		try:
			local = el.location
			size = el.size

			el_x = local['x']
			el_y = local['y']
			el_w = size['width']
			el_h = size['height']

			el_x2 = el_x + el_w
			el_y2 = el_y + el_h

			# Teste de interseção simples entre áreas
			if not (el_x2 < x1 or el_x > x2 or el_y2 < y1 or el_y > y2):
				elementos_na_area.append(el)

		except:
			continue

	if not elementos_na_area:
		print("[AVISO] Nenhum elemento detectado visualmente nessa área de tela.")
		return

	print(f"[INFO] {len(elementos_na_area)} elemento(s) dentro da área localizada:")

	for i, el in enumerate(elementos_na_area, start=1):
		try:
			xpath = driver.execute_script("""
				function getElementXPath(elt) {
					var path = "";
					for (; elt && elt.nodeType == 1; elt = elt.parentNode) {
						idx = getElementIdx(elt);
						xname = elt.tagName.toLowerCase();
						if (idx > 1) xname += "[" + idx + "]";
						path = "/" + xname + path;
					}
					return path;
					function getElementIdx(elt) {
						var count = 1;
						for (var sib = elt.previousSibling; sib; sib = sib.previousSibling) {
							if (sib.nodeType == 1 && sib.tagName == elt.tagName) count++;
						}
						return count;
					}
				}
				return getElementXPath(arguments[0]);
			""", el)
			print(f"{i:02d} → {xpath}")
		except Exception as e:
			print(f"[ERRO] Falha ao obter XPath de um elemento: {e}")

	print("\n[INFO] Testando se os elementos são interativos (filtrando por texto = 'Documento'):")
	for i, el in enumerate(elementos_na_area, start=1):
		try:
			driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
			time.sleep(0.3)

			texto = el.text.strip()
			if not "documento" in texto.lower():
				continue  # Ignora elementos que não são exatamente 'Documento'

			tag = el.tag_name
			visivel = el.is_displayed()
			onclick = el.get_attribute("onclick")
			role = el.get_attribute("role")
			classes = el.get_attribute("class")
			id_attr = el.get_attribute("id")
			title = el.get_attribute("title")
			aria = el.get_attribute("aria-label")

			print(f"\n--- Elemento {i:02d} ---")
			print(f"Tag        : <{tag}>")
			print(f"Visível    : {visivel}")
			print(f"Texto      : {texto}")
			print(f"ID         : {id_attr}")
			print(f"Classe     : {classes}")
			print(f"Role       : {role}")
			print(f"onclick    : {onclick}")
			print(f"title      : {title}")
			print(f"aria-label : {aria}")
		except Exception as e:
			print(f"[ERRO] Elemento {i:02d}: {e.__class__.__name__}")

	print("\n[DEBUG] Análise de interatividade completa. Digite 'c' no console para continuar.")
	breakpoint()

def fnc_fallback_imagem(driver, nome_objeto, caminho):
	import cv2
	import pyautogui

	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		screenshot_path = os.path.join(caminho, "tela_atual.png")
		time.sleep(2)
		pyautogui.moveTo(10, 10)  # Tira o mouse de cima de elementos interativos
		time.sleep(2)
		pyautogui.screenshot(screenshot_path)
		screenshot = cv2.imread(screenshot_path)

		if screenshot is None or screenshot.shape[0] < 10:
			print("[ERRO] Screenshot inválida. Verifique se há tela visível.")
			return None

		mapa_imagens = json_caminho('Local_Asset')

		log_info = "F3"
		for nome_arquivo in os.listdir(caminho):
			if nome_objeto.lower() in nome_arquivo.lower() and nome_arquivo.lower().endswith('.png'):
				caminho_template = os.path.join(mapa_imagens['Diretorio'], nome_arquivo)
				template = cv2.imread(caminho_template)

				if template is None or screenshot is None:
					print(f"[ERRO] Falha ao carregar imagens para '{nome_objeto}'")
					return None

				limiar = 0.85
				encontrado = False

				margem_max = 20  # pixels
				for margem in range(0, margem_max + 1):
					template_crop = fnc_crop_template(template, margem)
					if template_crop is None:
						break
					template_gray = cv2.cvtColor(template_crop, cv2.COLOR_BGR2GRAY)
					screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
					res = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
					min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
					print(f"[DEBUG] Margem {margem}px → confiança: {max_val:.3f}")
					if max_val >= limiar:
						top_left = max_loc
						h, w = template_crop.shape[:2]
						bottom_right = (top_left[0] + w, top_left[1] + h)
						cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
						cv2.imwrite(screenshot_path, screenshot)
						print(f"[INFO] Template encontrado com margem {margem}px")
						fnc_gerar_xpath(driver, top_left, bottom_right)
						return
				if not encontrado:
					print(f"[WARN] Imagem '{nome_objeto}' não localizada em nenhuma escala entre 100% e 50%")

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