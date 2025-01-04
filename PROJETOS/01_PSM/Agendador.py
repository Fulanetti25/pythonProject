import time
import subprocess
from datetime import datetime

minuto_1 = int(input("Digite a hora de intervalo de início no formato MM "))
if minuto_1 <= 29:
    minuto_2 = minuto_1 + 30
else:
    minuto_2 = minuto_1 - 30

while True:
    if int(datetime.now().strftime('%M')) == minuto_1 or int(datetime.now().strftime('%M')) == minuto_2:
        print('Iniciando Processo as !', datetime.now().strftime('%H:%M'))
        subprocess.call([r"C:\Users\paulo\OneDrive\Documentos\Processos\PSM VerificaSite.cmd"])
        print('Processo Finalizado as !', datetime.now().strftime('%H:%M'))
    else:
        print('Aguardando... Horarios previstos = :', minuto_1, ' e :', minuto_2, '   Agora :', datetime.now().strftime('%H:%M:%S'))
    time.sleep(60)