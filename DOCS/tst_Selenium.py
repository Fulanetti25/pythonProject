from selenium import webdriver
# Configuração do Chrome WebDriver automático
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Abre o navegador maximizado
# Inicializa o driver
driver = webdriver.Chrome(options=options)
# Teste - Acessar um site
driver.get("https://www.planilhasobmedida.com.br")
print(driver.title)
input()
# Fecha o navegador
driver.quit()
