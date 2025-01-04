import tst_pywhatkit as kit
import datetime

# Enviar mensagem para um número específico
numero = "+5511964821360"  # Número no formato internacional
nome_grupo = "PSM - ADMINISTRAÇÃO"
mensagem = "Olá! Esta é uma mensagem automática."
#mensagem = "Olá, grupo! Esta é uma mensagem automática."
hora = datetime.datetime.now().hour
minuto = datetime.datetime.now().minute + 2
wait_time = 15
kit.sendwhatmsg(numero, mensagem, hora, minuto, wait_time)
#kit.sendwhats_image(numero, 'C:\\Users\\paulo\\OneDrive\\133754842702646474.jpg', mensagem)
#kit.sendwhatmsg_to_group(f"{nome_grupo}"
# , mensagem, hora, minuto)
