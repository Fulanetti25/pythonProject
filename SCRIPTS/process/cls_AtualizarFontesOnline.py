import logging
import traceback
import inspect
import numpy as np
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_DataBases import prc_executa_local, prc_executa_online


def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        consulta1 = "SELECT * FROM dbo.PRD_DEV"
        consulta2 = "SELECT * from vactions.PRD_DEV"
        resultado1 = prc_executa_local(consulta1, None, False)
        resultado2 = prc_executa_online(consulta2, None, False)
        qtd1 = int(resultado1['Resultado']['Resultado'])
        qtd2 = int(resultado2['Resultado']['Resultado'])
        diferenca = qtd1 - qtd2
        print(f"DIFFERENCE: {diferenca} linhas")

        # if diferenca > 0:
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