import os
import time
import subprocess
from datetime import datetime
import itertools
import logging
import traceback
import inspect
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def etl_ExecutaProcesso(processo, horario):
    log_info = "F1"
    varl_detail = None
    minuto_1 = int(5)
    minuto_2 = int(15)
    minuto_3 = int(25)
    minuto_4 = int(35)
    minuto_5 = int(45)
    minuto_6 = int(55)
    minutos = [minuto_1, minuto_2, minuto_3, minuto_4, minuto_5, minuto_6]

    try:
        log_info = "F2"

        log_info = "F3"
        subprocess.call(processo)

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        pass

    return {"Resultado": str(processo), 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
    varg_modulo = fnc_NomeClasse (str(inspect.stack()[0].filename))

    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None

    processos = json_caminho('Json_Processos')
    file_dir = processos['Diretorio']
    file_name = os.path.join(file_dir, processos['Arquivo'])
    agenda = json_dados(file_name)
    lista_agenda = agenda["processos"]
    for lista in lista_agenda:
        print(lista)
    # file_dir = processos['Diretorio']
    # file_name = os.path.join(file_dir, processos['Arquivo'])


    # caminhos = json_caminho('Batch_Pesquisas_Google')
    # file_dir = caminhos['Diretorio']
    # file_name = [os.path.join(file_dir, caminhos['Arquivo'])]
    waiting_animation = itertools.cycle(["Aguardando.", "Aguardando..", "Aguardando...", "Aguardando....", "Aguardando....."])
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"

    try:
        pass
    #     while True:
    #         resultado = etl_ExecutaProcesso(file_name, int(datetime.now().strftime('%M')))
    #         print(next(waiting_animation), end='\r')
    #         time.sleep(60)
    #         exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
    #         exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
    #         exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
    #         exec_info += "\t\tMF\n"
    #         varg_erro = False

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