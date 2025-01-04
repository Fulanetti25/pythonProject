
#import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from datetime import datetime
#from datetime import timedelta

# Navega até a página
driver = webdriver.Chrome(executable_path="C:\selenium browser drivers\chromedriver_win32\chromedriver.exe")
driver.get("https://www.natura.com.br/c/tudo-em-promocoes")

# Clica em Login
btnLogin = driver.find_element_by_class_name("btn")
btnLogin.click()

# Python espera o preenchimento do Token recebido por e-mail
chave_acesso = input(">>>>>>> Informe o token recebido por e-mail:")

# Preenche o Token no site
txtboxToken = driver.find_element_by_name("login_token")
txtboxToken.send_keys(chave_acesso)

# Clica em Login
btnLoginToken = driver.find_element_by_xpath("/html/body/div/form/div[2]/div/span/button")
btnLoginToken.click()

# Navega até a página de relatórios
driver.get("https://cielo360.meeta.com.br/reports/geral")

# Define o período da base para exportar
dataFim = datetime.now() - timedelta(days=1)
diaDaSemana = datetime.now().weekday()

if diaDaSemana == 0:
    dataInicio = datetime.now() - timedelta(days=3)
else:
    dataInicio = dataFim

# Preenche o período no site
txtboxPeriodo = driver.find_element_by_name("daterange")
txtboxPeriodo.click()

# Preenche a data inicial do período
txtboxPeriodoInicial = driver.find_element_by_name("daterangepicker_start")
txtboxPeriodoInicial.clear()
txtboxPeriodoInicial.send_keys(dataInicio.strftime("%Y-%m-%d") + " 00:00:00")

# Preenche a data final do período

txtboxPeriodoFim = driver.find_element_by_name("daterangepicker_end")
txtboxPeriodoFim.clear()
txtboxPeriodoFim.send_keys(dataFim.strftime("%Y-%m-%d") + " 23:59:59")

# Clica em aplicar datas
btnAplicarPeriodo = driver.find_element_by_xpath("/html/body/div[3]/div[3]/div/button[1]")
btnAplicarPeriodo.click()

# Mapeia os 7 relatórios que deve exportar
relatorios = [
    ("Manual", "/html/body/div[2]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[1]/div[1]/label"),
    ("Automaticas", "/html/body/div[2]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[1]/div[2]/label"),
    ("Não Tabuladas", "/html/body/div[2]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[1]/div[3]/label"),
    ("Eventos", "/html/body/div[2]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[4]/label"),
    ("Ofertas Exibidas", "/html/body/div[2]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[3]/label"),
    ("Ofertas Oferecidas", "/html/body/div[2]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/label"),
    ("Ofertas Consolidadas", "/html/body/div[2]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[1]/label")
]

idRelatorio = 0
btnExportar = driver.find_element_by_id("enviar")

while idRelatorio < 7:
    btnRelatorio = driver.find_element_by_xpath(relatorios[idRelatorio][1])
    btnRelatorio.click()
    btnExportar.click()
    # print(relatorios[idRelatorio][0])
    idRelatorio = idRelatorio + 1
time.sleep(60)
driver.close()
driver.quit()