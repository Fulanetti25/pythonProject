import logging
import traceback
import inspect
import os
import time
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def prc_listar_maiores_arquivos(drive, top_n):
    log_info = "F1"
    varl_detail = None
    arquivos = []
    contagem_por_pasta = {}

    try:
        log_info = "F2"
        for root, _, files in os.walk(drive):
            for file in files:
                if file.lower() != "desktop.ini":
                    caminho_completo = os.path.join(root, file)
                    tamanho = os.path.getsize(caminho_completo)
                    arquivos.append((tamanho, caminho_completo))

        # Seleciona os top_n arquivos maiores
        arquivos.sort(reverse=True, key=lambda x: x[0])
        arquivos = arquivos[:top_n]

        # Mapeia a contagem de arquivos no 4º nível
        for _, caminho in arquivos:
            partes = caminho[len(drive):].split(os.sep)
            if len(partes) >= 4:
                pasta_nivel_4 = os.path.join(drive, *partes[:4])
                contagem_por_pasta[pasta_nivel_4] = contagem_por_pasta.get(pasta_nivel_4, 0) + 1

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    return {"Resultado": contagem_por_pasta, 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_excluir_arquivos_antigos(drive):
    log_info = "F1"
    varl_detail = None
    agora = time.time()
    dois_anos = 2 * 365 * 24 * 60 * 60
    um_ano = 1 * 365 * 24 * 60 * 60
    tamanho_limite = 1 * 1024 * 1024 * 1024  # 1 GB
    extensoes_video = {".mp4", ".avi"}
    contagem_excluidos = 0

    try:
        log_info = "F2"
        for root, _, files in os.walk(drive):
            for file in files:
                caminho_completo = os.path.join(root, file)
                if file.lower().endswith(".lnk"):
                    continue
                if not os.path.exists(caminho_completo):
                    continue

                tamanho = os.path.getsize(caminho_completo)
                data_modificacao = os.path.getmtime(caminho_completo)
                idade_arquivo = agora - data_modificacao
                extensao = os.path.splitext(file)[1].lower()
                if idade_arquivo > dois_anos:
                    os.remove(caminho_completo)
                    contagem_excluidos += 1
                elif idade_arquivo > um_ano and tamanho > tamanho_limite and extensao in extensoes_video:
                    os.remove(caminho_completo)
                    contagem_excluidos += 1
        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    return {"Resultado": contagem_excluidos, 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_excluir_pastas_vazias(drive):
    log_info = "F1"
    varl_detail = None
    pastas_excluidas = 0

    try:
        log_info = "F2"
        for root, dirs, files in os.walk(drive, topdown=False):
            for dir_name in dirs:
                caminho_pasta = os.path.join(root, dir_name)
                if not os.listdir(caminho_pasta):
                    os.rmdir(caminho_pasta)
                    pastas_excluidas += 1
        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    return {"Resultado": pastas_excluidas, 'Status_log': log_info, 'Detail_log': varl_detail}


def exe_LimpaGoogleDrive():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        resultado1 = prc_excluir_arquivos_antigos('G:\\Meu Drive\\PSM\\03 - DESENVOLVIMENTO\\DEV\\')
        exec_info += f"\t\t\t\tResultado: {resultado1['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado1['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado1['Detail_log']}\n"

        resultado2 = prc_excluir_pastas_vazias('G:\\Meu Drive\\PSM\\03 - DESENVOLVIMENTO\\DEV\\')
        exec_info += f"\t\t\t\tResultado: {resultado2['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado2['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado2['Detail_log']}\n"

        resultado = prc_listar_maiores_arquivos('G:\\', 100)
        for pasta, qtd in resultado["Resultado"].items():
            exec_info += f"\t\t\t\t{pasta} = {qtd} arquivos\n"

        exec_info += "\t\tMF\n"

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