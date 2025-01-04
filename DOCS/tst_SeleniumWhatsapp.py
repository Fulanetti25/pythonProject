from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import psutil
import os

#IMPLEMENTAR MODELO / TRATAMENTO DE ERRO / LOG PADRÃO

for proc in psutil.process_iter(attrs=['pid', 'name']):
    if 'chrome' in proc.info['name'].lower():
        os.kill(proc.info['pid'], 9)

numero = "+5511964821360"
mensagem = "Olá! Esta é uma mensagem automática."

user_data_dir = r"C:\Users\Paulo\AppData\Local\Google\Chrome\User Data"
profile_name = "Profile 1"

options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={user_data_dir}")
options.add_argument(f"profile-directory={profile_name}")

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")
time.sleep(5)

search_box  = driver.find_element("xpath", '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div/p')
search_box.click()  # Foca no campo de busca
search_box.send_keys(numero)
time.sleep(5)
search_box.send_keys(Keys.ENTER)

message_box = driver.find_element("xpath", '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p')
message_box.send_keys(mensagem)
message_box.send_keys(Keys.ENTER)
time.sleep(5)

driver.quit()

print('Mensagem enviada e navegador fechado!')