import os
import logging
import inspect
from SCRIPTS.functions.cls_CarregaJson import json_caminho


def log_execucao(var_modulo, var_funcao, var_status, var_detalhe):
    try:
        logging.info(f'{var_status},{var_modulo},{var_funcao},{var_detalhe}')
    except Exception as e:
        logging.error(f"Falha ao tentar registrar log: {e}")


def log_processo(var_modulo, var_funcao, var_detalhe, var_erro):
    log_execucao(var_modulo, var_funcao, "Falha" if var_erro else "Sucesso", var_detalhe)


def main(var_modulo = None, var_funcao = None, var_detalhe = None, var_erro = None):
    caminhos = json_caminho('Log_Acompanhamento')
    log_dir = caminhos['Diretorio']
    log_file = os.path.join(log_dir, caminhos['Arquivo'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if os.access(log_file, os.W_OK):
        logging.root.handlers = []
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s,%(levelname)s,%(module)s,%(message)s', filemode='a')
        logger = logging.getLogger()
        log_processo(var_modulo=var_modulo, var_funcao=var_funcao, var_detalhe=var_detalhe, var_erro=var_erro)
        logging.shutdown()


if __name__ == "__main__":
    main(__name__, inspect.currentframe().f_code.co_name, "teste_detalhe", False)