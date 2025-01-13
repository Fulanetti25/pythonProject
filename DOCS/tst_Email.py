import imaplib
import inspect
from decouple import config
from SCRIPTS.functions.cls_Logging import main as log_registra

IMAP_SERVER = config('IMAP_SERVER')
IMAP_USER = config('IMAP_USER')
IMAP_PASS = config('IMAP_PASS')
SMTP_SERVER = config('SMTP_SERVER')
SMTP_CC = config('SMTP_CC')


def prc_connect_email():
    log_info = "F1"
    varl_detail = None
    username = IMAP_USER
    password = IMAP_PASS
    imap_server = IMAP_SERVER

    try:
        log_info = "F3"
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    return {"Resultado": mail, 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_list_folders(mail):
    log_info = "F1"
    varl_detail = None
    folders = []

    try:
        log_info = "F3"
        status, folders_data = mail.list()
        if status != "OK":
            raise Exception("Não foi possível obter a lista de pastas.")

        for folder in folders_data:
            decoded_folder = folder.decode('utf-8').split(' "/" ')[-1]
            folders.append(decoded_folder)

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    return {"Resultado": folders, 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
    try:
        # Conectar ao e-mail
        mail_result = prc_connect_email()
        mail = mail_result["Resultado"]

        # Listar pastas
        folders_result = prc_list_folders(mail)
        folders = folders_result["Resultado"]

        print("Pastas disponíveis no IMAP:")
        for folder in folders:
            print(f"- {folder}")

    except Exception as e:
        print(f"Erro durante o processo: {e}")

    finally:
        # Fechar a conexão com o IMAP
        if 'mail' in locals():
            mail.logout()


if __name__ == "__main__":
    main()
