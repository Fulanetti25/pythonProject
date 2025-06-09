import os
import logging
import inspect
from functions.cls_Json.cls_Json import JsonHandler

class LogHandler:
    """
    Gerencia registro de logs.
    """
    def __init__(self, nome_config='Log_Acompanhamento', json_handler=None):
        # Injeta JsonHandler ou cria um novo
        self.json = json_handler or JsonHandler()
        self.nome_config = nome_config
        self._configurar_logging()

    def _configurar_logging(self):
        """
        Lê configurações de diretório e arquivo em JSON e inicializa o logging.
        """
        cfg = self.json.buscar_caminho(self.nome_config)
        log_dir = cfg.get('Diretorio')
        log_file_name = cfg.get('Arquivo', 'app.log')
        log_file = os.path.join(log_dir, log_file_name)

        # Garante que o diretório exista
        os.makedirs(log_dir, exist_ok=True)

        # Remove handlers antigos
        for h in logging.root.handlers[:]:
            logging.root.removeHandler(h)

        # Configura novo handler
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s,%(levelname)s,%(module)s,%(message)s',
            filemode='a'
        )

    def execucao(self, modulo, funcao, status, detalhe):
        """
        Registra uma entrada de log genérica.
        """
        try:
            logging.info(f'{status},{modulo},{funcao},{detalhe}')
        except Exception as e:
            logging.error(f"Falha ao registrar log: {e}")


    def processo(self, modulo, funcao, detalhe, erro=False):
        """
        Registra um log de processo, definindo status automático.
        """
        status = 'Falha' if erro else 'Sucesso'
        self.execucao(modulo, funcao, status, detalhe)


def main(var_modulo=None, var_funcao=None, var_detalhe=None, var_erro=None):
    """
    Exemplo de uso via linha de comando ou script.
    """
    logger = LogHandler()
    logger.processo(var_modulo, var_funcao, var_detalhe, var_erro)


if __name__ == "__main__":
    main(__name__, inspect.currentframe().f_code.co_name, "teste_detalhe", False)
