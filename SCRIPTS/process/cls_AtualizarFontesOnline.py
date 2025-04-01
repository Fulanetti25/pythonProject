import logging
import traceback
import inspect
import numpy as np
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_DataBases import prc_executa_local, prc_executa_online


def fnc_calcula_diferenca(consulta1, consulta2):
    log_info = "F1"
    varl_detail = None

    try:
        log_info = "F2"
        contagem1 = prc_executa_local(consulta1, None, False)
        contagem2 = prc_executa_online(consulta2, None, False)
        qtd1 = int(contagem1['Resultado']['Resultado'])
        qtd2 = int(contagem2['Resultado']['Resultado'])
        diferenca = qtd1 - qtd2

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        pass

    return {"Resultado": diferenca, 'Status_log': log_info, 'Detail_log': varl_detail}

def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        # resultado = fnc_calcula_diferenca("SELECT * FROM dbo.PRD_CAD_DEV","SELECT * from vactions.PRD_DEV")
        resultado = fnc_calcula_diferenca("SELECT * FROM dbo.PRD_PESQ_CLI", "SELECT * from vactions.PRD_PESQ_CLI")
        exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"

        # if {resultado['Resultado'] > 0:
        #     retorno1 = prc_executa_local(consulta1, None, True)
        #     df1 = retorno1['Resultado']['Resultado']
        #
        #     if not df1.empty:
        #         for index, linha in df1.iloc[0:364].iterrows():
        #             colunas = list(df1.columns)
        #             valores = tuple(None if pd.isna(x) else int(x) if isinstance(x, (np.int64, np.int32)) else x for x in linha)
        #
        #             placeholders = ", ".join(["%s"] * len(colunas))
        #             query_insert = f"INSERT INTO vactions.PRD_DEV ({', '.join(colunas)}) VALUES ({placeholders})"
        #
        #             resultado_insert = prc_executa_online(query_insert, valores, False)
        #             print(resultado_insert['Resultado']['Resultado'])

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