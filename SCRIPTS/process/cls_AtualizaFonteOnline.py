import logging
import traceback
import inspect
import numpy as np
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_DataBases import prc_executa_local, prc_executa_online


def fnc_calcula_diferenca(tabela1, tabela2):
    log_info = "F1"
    varl_detail = None

    try:
        log_info = "F2"
        contagem1 = prc_executa_local(tabela1, None, "COUNT")
        contagem2 = prc_executa_online(tabela2, None, "COUNT")
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
    consultas = [
        ("dbo.PRD_CAD_DEV", "vactions.PRD_CAD_DEV"),
        ("dbo.PRD_PESQ_CLI", "vactions.PRD_PESQ_CLI"),
        ("dbo.PRD_PESQ_ANON", "vactions.PRD_PESQ_ANON"),
        ("dbo.PRD_PESQ_DEV", "vactions.PRD_PESQ_DEV")
    ]
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        for consulta_origem, consulta_destino in consultas:
            resultado = fnc_calcula_diferenca(consulta_origem, consulta_destino)
            exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
            exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
            exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"

            if resultado['Resultado'] > 0:
                retorno = prc_executa_local(consulta_origem, None, 'SELECT')
                df = retorno['Resultado']['Resultado']
                if not df.empty:
                    diferenca = resultado['Resultado']
                    for index, linha in df.iloc[-diferenca:].iterrows():
                        colunas = list(df.columns)
                        valores = tuple(None if pd.isna(x) else int(x) if isinstance(x, (np.int64, np.int32)) else x for x in linha)
                        placeholders = ", ".join(["%s"] * len(colunas))
                        query_insert = f"INSERT INTO {consulta_destino} ({', '.join(colunas)}) VALUES ({placeholders})"
                        exec_info += prc_executa_online(query_insert, valores, 'INSERT')

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