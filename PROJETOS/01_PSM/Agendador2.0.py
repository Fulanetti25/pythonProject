import time
import subprocess
from datetime import datetime
import csv
import itertools

# Função para registrar o log no arquivo .csv
def log_execution(processo, detalhe):
    # file_path = f"G:\\Meu Drive\\PSM\\01 - OPERACIONAL\\00_FONTES\\log.csv"  # Substitua pelo caminho correto
    timestamp = datetime.now().isoformat()
    status = "Executado com sucesso"

    # with open(file_path, mode='a', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow([timestamp, status, processo, detalhe])
    # print("Log atualizado com sucesso.")

# Define os minutos de execução
minuto_1 = int(5)
minuto_2 = int(15)
minuto_3 = int(25)
minuto_4 = int(35)
minuto_5 = int(45)
minuto_6 = int(55)
minutos = [minuto_1, minuto_2, minuto_3, minuto_4, minuto_5, minuto_6]

# Sequência para a animação de espera
waiting_animation = itertools.cycle(["Aguardando.", "Aguardando..", "Aguardando...", "Aguardando....", "Aguardando....."])

# Loop principal
while True:
    current_minute = int(datetime.now().strftime('%M'))
    if current_minute in minutos:
        print('Iniciando Processo às', datetime.now().strftime('%H:%M'))
        subprocess.call([r"C:\Users\paulo\OneDrive\Documentos\Processos\PSM VerificaSite.cmd"])
        # Registrar log de execução
        log_execution("VerificaSite", "Processo completado")
    else:
        # Mostrar animação de espera
        print(next(waiting_animation), end='\r')
    time.sleep(60)