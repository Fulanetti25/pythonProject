import traceback
import inspect
import time
import psutil
import os
import logging
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados, json_registra, json_limpa, json_atualiza
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def prc_executa_whats(numero, mensagem, anexo):
	log_info = "F1"
	varl_detail = None
	conn_obj = None

	try:
		log_info = "F2"
		conexao = fnc_connect_whats()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		fnc_envia_whats(conn_obj, numero, mensagem, anexo)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		fnc_salvar_falha('WHATSAPP', conn_log, numero, {mensagem+anexo})
		log_info = "F99"

	finally:
		fnc_close_whats(conn_obj)

	return {"Resultado": "Executado", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_envia_whats(driver, numero, mensagem, anexo):
	log_info = "F1"
	varl_detail = None
	result = None
	objeto = None
	mapa_objetos = None
	xpath = None
	driver.get("https://web.whatsapp.com")
	time.sleep(10)

	try:
		log_info = "F2"
		objeto = 'SEARCH_BOX'
		mapa_objetos = json_caminho('Json_Mapa_Objetos')
		dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
		xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto),None)
		search_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
		search_box.click()
		search_box.send_keys(numero)
		search_box.send_keys(Keys.ENTER)

		log_info = "F3"
		objeto = 'MESSAGE_BOX'
		mapa_objetos = json_caminho('Json_Mapa_Objetos')
		dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
		xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto), None)
		message_box = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
		message_box.send_keys(mensagem)

		if anexo:
			log_info = "F4"
			objeto = 'PLUS_BUTTON'
			mapa_objetos = json_caminho('Json_Mapa_Objetos')
			dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
			xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto), None)
			plus_button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
			plus_button.click()

			nome, extensao = os.path.splitext(anexo)
			if extensao == '.vcf':
				log_info = "F5.1"
				objeto = 'DOC_OPTION'
				mapa_objetos = json_caminho('Json_Mapa_Objetos')
				dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
				xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto), None)
				doc_option = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
				doc_option.click()

			if extensao == '.png':
				log_info = "F5.2"
				objeto = 'IMG_OPTION'
				mapa_objetos = json_caminho('Json_Mapa_Objetos')
				dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
				xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto), None)
				img_option = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
				img_option.click()

			time.sleep(5)
			os.system(f'echo {anexo} | clip')  # Copia o caminho para o clipboard
			pyautogui.hotkey('ctrl', 'v')  # Cola o caminho
			pyautogui.press('enter')  # Confirma o envio

		if anexo:
			log_info = "F6"
			objeto = 'BIG_ARROW'
			mapa_objetos = json_caminho('Json_Mapa_Objetos')
			dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
			xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto), None)
			big_arrow = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
			big_arrow.click()
			time.sleep(5)
		else:
			log_info = "F7"
			objeto = 'SEND_ARROW'
			mapa_objetos = json_caminho('Json_Mapa_Objetos')
			dados_objetos = json_dados(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']))
			xpath = next((item["Xpath"] for item in dados_objetos["objetos"] if item["Nome"] == objeto), None)
			send_arrow = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
			send_arrow.click()
			time.sleep(5)

	except Exception as e:
		print(f"Elemento {objeto} com XPath '{xpath}' não encontrado!")
		novo_xpath = input("Digite o XPath manualmente: ").strip()
		json_atualiza(os.path.join(mapa_objetos['Diretorio'], mapa_objetos['Arquivo']), 'objetos', objeto, 'Xpath', novo_xpath)

		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail,var_erro=True)
		log_info = "F99"

		# RECURSO DE BUSCA DE POSSÍVEIS XPATH AUTOMATIZADO
		# resultado = fnc_mapear_elementos(driver)
		# lista = resultado['Resultado']
		# for item in lista:
		# 	if any('//*[@id="side"]/div[1]/div/div[2]/div/div/div[1]/p' in str(value) for value in item.values()):
		# 		print(item)

		log_info = "F0"

	finally:
		pass

	return {"Resultado": str(result) + " Mensagem " + 'anexo' if anexo else 'texto'  + " enviada para " + str(numero), 'Status_log': log_info, 'Detail_log': varl_detail}


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
		raise

	finally:
		pass

	return {"Resultado": "Conexão fechada", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_salvar_falha(server, conn_log, sql_query, params):
	log_info = "F1"
	varl_detail = None
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_dados = json_dados(os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

	try:
		log_info = "F2"
		pilha = falhas_dados if falhas_dados else []
		falha = {
			"server": server,
			"log": conn_log,
			"query": sql_query,
			"params": params,
		}

		if falha not in pilha:
			pilha.append(falha)
			json_registra(pilha, arquivo=os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": "Inserido na pilha", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_reprocessar_falha():
	log_info = "F1"
	varl_detail = None
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_path = os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo'])

	try:
		log_info = "F2"
		pilha = json_dados(falhas_path)

		log_info = "F3"
		for falha in pilha:
			query = falha["query"]
			params = falha["params"]
			prc_executa_db(query, params)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		if log_info == "F0":
			pass
			json_limpa(falhas_path)

	return {"Resultado": "Pilha Reprocessada", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_get_element_xpath(driver, element):
	xpath = driver.execute_script(
		"function absoluteXPath(element) {"
		"  var comp, comps = [];"
		"  var parent = null;"
		"  var xpath = '';"
		"  var getPos = function(element) {"
		"    var position = 1, curNode;"
		"    if (element.nodeType == Node.ATTRIBUTE_NODE) {"
		"      return null;"
		"    }"
		"    for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {"
		"      if (curNode.nodeName == element.nodeName) {"
		"        ++position;"
		"      }"
		"    }"
		"    return position;"
		"  };"
		"  if (element instanceof Document) {"
		"    return '/';"
		"  }"
		"  for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {"
		"    comp = comps[comps.length] = {};"
		"    comp.name = element.nodeName;"
		"    comp.position = getPos(element);"
		"  }"
		"  for (var i = comps.length - 1; i >= 0; i--) {"
		"    comp = comps[i];"
		"    xpath += '/' + comp.name.toLowerCase();"
		"    if (comp.position !== null && comp.position > 1) {"
		"      xpath += '[' + comp.position + ']';"
		"    }"
		"  }"
		"  return xpath;"
		"}"
		"return absoluteXPath(arguments[0]);", element)
	return xpath


def fnc_mapear_elementos(driver):
	log_info = "F1"
	varl_detail = None
	elements = driver.find_elements(By.XPATH, "//*")

	mapping = []
	for elem in elements:
		try:
			xpath = fnc_get_element_xpath(driver, elem)
			object_name = elem.get_attribute("name") or elem.tag_name
			object_type = 'NAME' if elem.get_attribute("name") else 'TAG'
			text = elem.text.strip()
			aria_label = elem.get_attribute("aria-label")
			classe = elem.get_attribute("class")
			placeholder = elem.get_attribute("placeholder")

			mapping.append({
				"object_name": object_name,
				"object_type": object_type,
				"xpath": xpath,
				"text": text,
				"aria_label": aria_label,
				"class": classe,
				"placeholder": placeholder
			})
		except Exception as e:
			continue

	return {"Resultado": mapping, 'Status_log': log_info, 'Detail_log': varl_detail}

def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	numero = "+5511964821360"
	mensagem = "Olá! Esta é uma mensagem automática."
	# anexo = r'G:\Meu Drive\PSM\01 - OPERACIONAL\00_FONTES\contatos\202412 CLI TEIXEIRA.vcf'
	anexo = r'G:\Meu Drive\PSM\01 - OPERACIONAL\00_FONTES\grafico_gantt.png'
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		# resultado = prc_executa_whats(numero, mensagem, None)
		resultado = prc_executa_whats(numero, mensagem, anexo)
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