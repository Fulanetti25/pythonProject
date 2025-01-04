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
from SCRIPTS.functions.cls_CarregaJson import json_caminho
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def enviar_whatsapp_texto(numero, mensagem):
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
		driver.get("https://web.whatsapp.com")
		WebDriverWait(driver, 30).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="side"]'))
		)

		log_info = "F3"
		search_box = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div/p'))
		)
		search_box.click()
		search_box.send_keys(numero)
		search_box.send_keys(Keys.ENTER)
		WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="main"]'))
		)

		message_box = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p'))
		)
		message_box.send_keys(mensagem)

		log_info = "F5"
		time.sleep(5)
		send_arrow = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button/span'))
		)
		send_arrow.click()
		time.sleep(5)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		if 'driver' in locals():
			driver.quit()
		time.sleep(5)

	return {"Resultado": str(numero), 'Status_log': log_info, 'Detail_log': varl_detail}


def enviar_whatsapp_anexo(numero, mensagem, anexo):
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
		driver.get("https://web.whatsapp.com")
		WebDriverWait(driver, 30).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="side"]'))
		)

		log_info = "F3"
		search_box = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div/p'))
		)
		search_box.click()
		search_box.send_keys(numero)
		search_box.send_keys(Keys.ENTER)
		WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="main"]'))
		)

		message_box = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p'))
		)
		message_box.send_keys(mensagem)

		log_info = "F4"
		plus_button = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button/span'))
		)
		plus_button.click()

		doc_option = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/span[5]/div/ul/div/div/div[1]/li/div/span'))
		)
		doc_option.click()

		time.sleep(5)
		os.system(f'echo {anexo} | clip')  # Copia o caminho para o clipboard
		pyautogui.hotkey('ctrl', 'v')  # Cola o caminho
		pyautogui.press('enter')       # Confirma o envio

		log_info = "F5"
		time.sleep(5)
		send_arrow = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div'))
		)
		send_arrow.click()
		time.sleep(5)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		if 'driver' in locals():
			driver.quit()
		time.sleep(5)

	return {"Resultado": str(numero), 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	numero = "+5511964821360"
	mensagem = "Olá! Esta é uma mensagem automática."
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		#resultado = enviar_whatsapp_texto(numero, mensagem)
		resultado = enviar_whatsapp_anexo(numero, mensagem, r'G:\Meu Drive\PSM\01 - OPERACIONAL\00_FONTES\contatos\202412 CLI TEIXEIRA.vcf')
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