import os
import traceback
import time
import psutil
import cv2
import pyautogui
import glob
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados, json_atualiza


def prc_executa_chrome():
	log_info = "F1"
	varl_detail = None
	conn_obj = None

	try:
		log_info = "F2"
		conexao = fnc_connect_chrome()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		fnc_navega_chrome(conn_obj)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_info = "F99"

	finally:
		fnc_close_chrome(conn_obj)

	return {"Resultado": "Executado", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_connect_chrome():
	log_info = "F1"
	varl_detail = None

	for proc in psutil.process_iter(attrs=['pid', 'name']):
		if 'chrome' in proc.info['name'].lower():
			proc.terminate()

	options = webdriver.ChromeOptions()
	caminho = json_caminho('Chrome_Profile')
	options.add_argument(f"user-data-dir={caminho['Diretorio']}")
	options.add_argument(f"profile-directory={caminho['Arquivo']}")
	options.add_argument("--disable-blink-features=AutomationControlled")  # Remove algumas proteções
	options.add_argument("--disable-infobars")  # Remove a barra de informações
	options.add_argument("--start-maximized")  # Abre em tela cheia
	options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove a flag de automação
	options.add_experimental_option("useAutomationExtension", False)  # Remove extensão de automação

	try:
		log_info = "F2"
		driver = webdriver.Chrome(options=options)
		driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": driver, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_close_chrome(driver):
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
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": "Conexão fechada", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_navega_chrome(driver):
	log_info = "F1"
	varl_detail = None

	driver.get("https://roobet.com/coinflip")
	driver.maximize_window()
	time.sleep(10)

	try:
		log_info = "F2"
		# Gravar Screenshot Inicial
		screenshot_path = "screenshot0.png"
		pyautogui.screenshot(screenshot_path)

		# Preparar laço de iteração nas imagens da pasta.
		ref_images_path = r"C:\ROOBET\GRUPO_1\*.JPG"  # Agora pega todas as imagens na pasta
		ref_images = glob.glob(ref_images_path)
		screenshot = cv2.imread(screenshot_path)
		if screenshot is None:
			print("Erro ao carregar a captura de tela!")
		else:
			print(f"Tamanho do Screenshot: {screenshot.shape}")

		log_info = "F3"
		objeto = 'GRUPO_SALDO'
		mapa_objetos = json_caminho('Json_Mapa_Objetos')
		dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
		xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto), None)
		if not xpath:
			raise ValueError(f"XPath não encontrado para o objeto: {objeto}")
		plus_button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
		plus_button.click()

		resultados = {}
		encontradas = 0  # Contador de imagens encontradas
		total_imagens = len(ref_images)  # Total de imagens na pasta

		for img_path in ref_images:
			nome_arquivo = os.path.basename(img_path)
			template = cv2.imread(img_path)
			if template is None:
				print(f"Erro ao carregar a imagem de referência: {img_path}")
				continue

			print(f"Tamanho do Template ({nome_arquivo}): {template.shape}")

			# Comparação de template
			result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
			min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

			# Verifica o valor máximo de correspondência
			print(f"Comparação {nome_arquivo}: max_val = {max_val}")

			# Se max_val for maior que um limiar, consideramos que a imagem foi encontrada
			limiar = 0.7  # Ajuste conforme necessário
			if max_val >= limiar:
				resultados[nome_arquivo] = f"Encontrado em {max_loc}"
				encontradas += 1  # Incrementa o contador

				# Pegar posição onde a imagem foi encontrada
				top_left = max_loc
				largura, altura = template.shape[1], template.shape[0]

				# Obter os elementos próximos e seus XPaths
				xpaths_encontrados = encontrar_elementos_proximos(driver, top_left[0], top_left[1], largura, altura)

				print("\nElementos encontrados na região:")
				for xpath in xpaths_encontrados:
					print(xpath)

				# Desenhar um retângulo no screenshot para indicar onde encontrou a imagem
				top_left = max_loc
				bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
				cv2.rectangle(screenshot, top_left, bottom_right, (0, 0, 255), 2)

			else:
				resultados[nome_arquivo] = "Não encontrado"

		# Mostrar o resultado com os retângulos desenhados
		cv2.imwrite("screenshot1.png", screenshot)

		# Exibir resumo final
		print("\nResumo:")
		print(f"Total de imagens verificadas: {total_imagens}")
		print(f"Total de imagens encontradas: {encontradas}")
		print(resultados)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_info = "F99"

	finally:
		pass

	return {"Resultado": 'Sucesso', 'Status_log': log_info, 'Detail_log': varl_detail}


def encontrar_elementos_proximos(driver, x, y, largura, altura):
	# Obter todos os elementos da página
	elementos = driver.find_elements(By.XPATH, "//*")

	elementos_proximos = []
	for elemento in elementos:
		try:
			# Obter posição e tamanho do elemento na página
			location = elemento.location
			size = elemento.size
			x_el, y_el = location["x"], location["y"]
			largura_el, altura_el = size["width"], size["height"]

			# Verificar se há interseção entre a região detectada e o elemento
			if not ((x + largura < x_el) or (x > x_el + largura_el) or
					(y + altura < y_el) or (y > y_el + altura_el)):
				elementos_proximos.append(elemento)

		except Exception:
			continue  # Ignora erros causados por elementos dinâmicos

	# Extrair XPath dos elementos encontrados
	elementos_xpath = []
	for el in elementos_proximos:
		xpath = driver.execute_script("""
			function getXPath(element) {
				if (element.id !== '')
					return 'id("' + element.id + '")';
				if (element === document.body)
					return element.tagName;

				var ix = 0;
				var siblings = element.parentNode.childNodes;
				for (var i=0; i<siblings.length; i++) {
					var sibling = siblings[i];
					if (sibling === element)
						return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix+1) + ']';
					if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
						ix++;
				}
			}
			return getXPath(arguments[0]);
		""", el)
		elementos_xpath.append(xpath)

	return elementos_xpath


def main():
	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = prc_executa_chrome()
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
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)