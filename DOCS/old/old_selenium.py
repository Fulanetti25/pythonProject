from old_selenium import webdriver
from old_selenium.webdriver.common.keys import Keys
driver_path = 'path/to/chromedriver' # Atualize para o caminho do seu WebDriver
driver = webdriver.Chrome(driver_path) # Iniciar o navegador
driver.get("https://web.whatsapp.com") # Navegar para o WhatsApp Web