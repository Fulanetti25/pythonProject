import os, requests, time
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def obter_informacoes_sistema():
    nome_maquina = os.environ['COMPUTERNAME'] if 'COMPUTERNAME' in os.environ else os.environ['HOSTNAME']
    codigo_usuario = os.environ['USERNAME']

    return nome_maquina, codigo_usuario

def obter_localizacao_aproximada():
    try:
        # Faz uma solicitação à API ipinfo.io para obter informações de geolocalização
        resposta = requests.get('https://ipinfo.io')
        dados = resposta.json()

        # Extrai informações relevantes
        cidade = dados.get('city', 'Desconhecida')
        regiao = dados.get('region', 'Desconhecida')
        pais = dados.get('country', 'Desconhecido')
        localizacao = f"{cidade}, {regiao}, {pais}"

        return localizacao

    except Exception as e:
        print(f"Erro ao obter localização: {str(e)}")

        return None

#Inicio

#numero = int(input('Digite o telefone do safado (fula = 5511964821360 / renatogo = 5511973003602)'))
numero = 5511973003602
localizacao = obter_localizacao_aproximada()
nome_maquina, codigo_usuario = obter_informacoes_sistema()
mensagem = ("Olá Renatogo. Vamos jogar um jogo!\n"
#f"De minha infra {nome_maquina}, logado como: {codigo_usuario.upper()}. Situado em: {localizacao}\n\n"
"Você está convidado para a nossa confraternização em Araçoiaba da Serra em 02/12/2023 às 11:00.\n"
"Será um prazer contar com a sua presença e de sua família!\n\n"
"Atenção: o convite aqui foi limitado ao time de dados!\n"
"Organização nossa e Bagunça nossa também!!!\n"
"Atenciosamente. Time de DataScience."
)
texto = quote(mensagem)
link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"
print(link)

navegador = webdriver.Chrome()
navegador.maximize_window()
navegador.get("https://web.whatsapp.com/")
espera = WebDriverWait(navegador,30)
check_1 = espera.until(expected_conditions.visibility_of_element_located((By.XPATH,'//*[@id="side"]/div[1]/div/div[2]/button/div[2]/span')))

navegador.get(link)
espera = WebDriverWait(navegador,360)
check_2 = espera.until(expected_conditions.visibility_of_element_located((By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p/span')))
navegador.find_element(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p/span').send_keys(Keys.ENTER)
time.sleep(10)