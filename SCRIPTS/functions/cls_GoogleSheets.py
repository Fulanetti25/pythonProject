import logging
import traceback
import inspect
import gspread
import time
from decouple import config
from string import ascii_uppercase
from oauth2client.service_account import ServiceAccountCredentials
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


# VARIAVEIS GLOBAIS
json_gs = config('DRUMEIBES_GS_API')


def fnc_recupera_detalhes(video):
    log_info = "F1"
    varl_detail = None

    try:
        log_info = "F2"
        caminho_credencial = json_gs

        resultado = fnc_busca_video_detalhes(caminho_credencial, video)

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        pass

    return {"Resultado": resultado, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_busca_video_detalhes(caminho_credencial_json, titulo_video):
    log_info = "F1"
    nome_planilha = 'VIDEOS'
    nome_aba = 'DOC VIDEO'
    varl_detail = None
    inicio = time.time()
    dados = {}
    try:
        log_info = "F2"
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(caminho_credencial_json, scope)
        client = gspread.authorize(credentials)

        sheet = client.open(nome_planilha).worksheet(nome_aba)

        # Lê só a coluna B (onde estão os títulos dos vídeos)
        col_b = sheet.col_values(2)  # B = 2
        col_b_lower = [titulo.lower() for titulo in col_b]

        # Encontra a linha onde está o título buscado
        if titulo_video in col_b_lower:
            linha = col_b_lower.index(titulo_video) + 1  # índice começa do 0, linha começa do 1

            # Lê a linha inteira ou só colunas C:G (C=3, G=7)
            valores_linha = sheet.row_values(linha)
            dados = {
                "nome_artista": valores_linha[2] if len(valores_linha) > 2 else '',
                "idioma": valores_linha[3] if len(valores_linha) > 3 else '',
                "inicio_legenda": valores_linha[4] if len(valores_linha) > 4 else '',
                "credito_drums": valores_linha[5] if len(valores_linha) > 5 else '',
                "credito_bass": valores_linha[6] if len(valores_linha) > 6 else '',
                "credito_inferior": valores_linha[7] if len(valores_linha) > 7 else '',
            }

        else:
            varl_detail = f"Vídeo '{titulo_video}' não encontrado na coluna B."
            log_info = "F98"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        fim = time.time()
        print(f"[Tempo de execução] Leitura Google Sheets detalhes: {fim - inicio:.2f} segundos")

    return {"Resultado": dados, 'Status_log': log_info, 'Detail_log': varl_detail}


def main(video = 'Drumeibes - Pitty - Teto de Vidro'):
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        resultado = fnc_recupera_detalhes(video.lower())
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

    return resultado


if __name__ == "__main__":
    main()
    print(exec_info)