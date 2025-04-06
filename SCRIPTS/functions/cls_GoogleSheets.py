import logging
import traceback
import inspect
import gspread
from decouple import config
from oauth2client.service_account import ServiceAccountCredentials
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


# VARIAVEIS GLOBAIS
json_gs = config('DRUMEIBES_GS_API')


def fnc_teste(_):
    caminho_credencial = json_gs
    nome_planilha = 'VIDEOS'
    celulas = ['A1', 'B2', 'C3']  # pode ser qualquer lista que você quiser testar
    return gsheets_ler_dados_padrao(caminho_credencial, nome_planilha, celulas)


def gsheets_ler_dados_padrao(caminho_credencial_json, nome_planilha, celulas_interesse):
    log_info = "F1"
    varl_detail = None
    try:
        log_info = "F2"
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(caminho_credencial_json, scope)
        client = gspread.authorize(credentials)

        sheet = client.open(nome_planilha).worksheet("DEFAULT")

        dados = {}
        for celula in celulas_interesse:
            dados[celula] = sheet.acell(celula).value

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        pass

    return {"Resultado": dados, 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        resultado = fnc_teste('Teste')
        exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
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