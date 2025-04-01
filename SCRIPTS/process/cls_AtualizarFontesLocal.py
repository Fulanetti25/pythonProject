import logging
import traceback
import inspect
import subprocess
from decouple import config
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


server = config('SQL_SERVER')
database = config('SQL_DATABASE')


def fnc_rodar_cmd(linha):
    log_info = "F1"
    varl_detail = None
    comando = [
        "sqlcmd",
        "-S", server,  # Nome do servidor
        "-d", database,           # Nome do banco de dados
        "-Q", linha,  # Comando SQL
        "-E"  # Autenticação do Windows
    ]

    # Executa o comando e captura a saída
    try:
        log_info = "F2"
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        pass

    return {"Resultado": str(resultado.stdout), 'Status_log': log_info, 'Detail_log': varl_detail}

def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        resultado1 = fnc_rodar_cmd("EXEC dbo.PRC_TAB_DEV")
        exec_info += f"\t\t\t\tResultado: {resultado1['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado1['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado1['Detail_log']}\n"
        resultado2 = fnc_rodar_cmd("EXEC dbo.PRC_TAB_PESQ")
        exec_info += f"\t\t\t\tResultado: {resultado2['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado2['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado2['Detail_log']}\n"
        resultado3 = fnc_rodar_cmd("EXEC dbo.PRC_TAB_ANON")
        exec_info += f"\t\t\t\tResultado: {resultado3['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado3['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado3['Detail_log']}\n"
        resultado4 = fnc_rodar_cmd("EXEC dbo.PRC_TAB_PESQ_DEV")
        exec_info += f"\t\t\t\tResultado: {resultado4['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado4['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado4['Detail_log']}\n"
        exec_info += "\t\tMF\n"
        resultado5 = fnc_rodar_cmd("EXEC dbo.PRC_TAB_PROJETOS")
        exec_info += f"\t\t\t\tResultado: {resultado5['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado5['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado5['Detail_log']}\n"
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