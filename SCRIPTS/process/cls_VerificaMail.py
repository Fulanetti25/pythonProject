import os
import re
import imaplib
import email
import chardet
import logging
import traceback
import inspect
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from email.header import decode_header
from datetime import datetime
from decouple import config
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_OutWhatsapp import enviar_whatsapp_anexo


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
		mail.select("inbox")
		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": mail, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_remove_html_tags(html_content):
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F3"
		soup = BeautifulSoup(html_content, "html.parser")
		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return soup.get_text(separator=" ").strip()


def fnc_decode_payload(payload):
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F3"
		result = payload.decode("utf-8")
		log_info = "F0"

	except (UnicodeDecodeError, AttributeError) as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		result = chardet.detect(payload)
		encoding = result.get("encoding", "utf-8")
		result = payload.decode(encoding)

	return {"Resultado": result, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_gerar_vcard(nome, email, telefone, mensagem, file_name):
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F3"
		vcard = f"""
BEGIN:VCARD
VERSION:3.0
FN:{nome}
TEL:{telefone}
EMAIL;TYPE=HOME:{email}
NOTE:{mensagem}
END:VCARD"""
		with open(file_name, "w") as arquivo:
			arquivo.write(vcard)
		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": file_name, 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_check_all_emails(mail):
	log_info = "F1"
	varl_detail = None
	try:
		status, messages = mail.search(None, 'ALL')
		log_info = "F3"
		email_ids = messages[0].split()
		emails = []
		for e_id in email_ids:
			_, msg = mail.fetch(e_id, "(RFC822)")
			for response in msg:
				if isinstance(response, tuple):
					msg = email.message_from_bytes(response[1])
					assunto, encoding = decode_header(msg["Subject"])[0]
					if isinstance(assunto, bytes):
						assunto = assunto.decode(encoding if encoding else "utf-8")
					from_email = msg.get("From")
					if msg.is_multipart():
						for part in msg.walk():
							content_type = part.get_content_type()
							if content_type == "text/plain":
								payload = part.get_payload(decode=True)
								body = fnc_decode_payload(payload)
								emails.append({"from": from_email, "assunto": assunto, "body": body})
								break
					else:
						payload = msg.get_payload(decode=True)
						body = fnc_decode_payload(payload)
						emails.append({"from": from_email, "assunto": assunto, "body": body})
		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		return {"Resultado": [], 'Status_log': log_info, 'Detail_log': varl_detail}
		raise

	return {"Resultado": emails, 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_process_email(msg_data):
	log_info = "F1"
	varl_detail = None
	nome = "Não identificado"
	email_match = None
	telefone_match = None
	mensagem = None

	try:
		log_info = "F3"
		assunto = msg_data['assunto']

		if msg_data.get("from"):
			sender = msg_data["from"]
			nome = sender.split("<")[0].strip() if "<" in sender else sender.strip()
			nome = nome.replace('"', '')
			nome = datetime.now().strftime("%Y%m%d") + " CLI " + nome

		body = msg_data["body"]["Resultado"]
		body = fnc_remove_html_tags(body)

		email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
		telefone_pattern = r"(\+?\d{1,3}[ \-]?)?(\(?\d{2}\)?[ \-]?)?(9\d{4}\-?\d{4}|\d{4}\-?\d{4})"
		email_match = re.search(email_pattern, body)
		telefone_match = re.search(telefone_pattern, body)
		print(telefone_pattern)
		print(telefone_match)

		mensagem = body
		if email_match:
			mensagem = mensagem.replace(email_match.group(0), "").strip()
		if telefone_match:
			mensagem = mensagem.replace(telefone_match.group(0), "").strip()
		mensagem = mensagem.replace("Contato:", "").strip()
		mensagem = mensagem.replace("E-mail:", "").strip()
		mensagem = mensagem.replace("Necessidade do Cliente:", "").strip()
		mensagem = " ".join(mensagem.splitlines()).strip()

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	return {"assunto": assunto, "nome": nome, "email": email_match.group(0) if email_match else "Não identificado",
			"telefone": telefone_match.group(0) if telefone_match else "Não identificado", "mensagem": mensagem,
			'Status_log': log_info, 'Detail_log': varl_detail}


def prc_reply_dados(destinatario, assunto, corpo_email):
	try:
		smtp_server = SMTP_SERVER
		smtp_port = 587
		smtp_user = IMAP_USER
		smtp_password = IMAP_PASS
		destinatario_copia = SMTP_CC

		msg = MIMEMultipart()
		msg['From'] = smtp_user
		msg['To'] = destinatario
		msg['Cc'] = destinatario_copia
		msg['Subject'] = assunto
		msg.attach(MIMEText(corpo_email, 'plain'))

		server = smtplib.SMTP(smtp_server, smtp_port)
		server.starttls()
		server.login(smtp_user, smtp_password)
		to_list = [destinatario] + [destinatario_copia]
		server.sendmail(smtp_user, to_list, msg.as_string())
		server.quit()

		return {"Resultado": "E-mail enviado com sucesso.", 'Status_log': "F0", 'Detail_log': "Email enviado."}

	except Exception as e:
		return {"Resultado": "Erro ao enviar o e-mail.", 'Status_log': "F99", 'Detail_log': f"Erro: {e}"}


def prc_reply_mail(processed_email):
	mail = json_caminho('Mail_ContatoInvalido')
	mensagem_json = json_dados(os.path.join(mail['Diretorio'], mail['Arquivo']))
	mensagem_padrao = mensagem_json.get("mensagem_padrao", "Mensagem padrão não encontrada.")

	corpo_email = mensagem_padrao.format(nome=processed_email["nome"], mensagem=processed_email["mensagem"], email=processed_email["email"])

	resultado_envio = prc_reply_dados(processed_email["email"], "Planilha sob Medida - Requisição de contato", corpo_email)

	return resultado_envio


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
	mail = prc_connect_email()

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"

	try:
		emails_data = prc_check_all_emails(mail['Resultado'])["Resultado"]
		if emails_data:
			for email_data in emails_data:
				processed_email = prc_process_email(email_data)
				print(processed_email)
				if processed_email["email"] != "Não identificado":
					caminho = json_caminho('Contato_VCard')
					file_dir = caminho['Diretorio']
					file_name = os.path.join(file_dir, processed_email["nome"] + '.vcf')
					fnc_gerar_vcard(processed_email["nome"],processed_email["email"],processed_email["telefone"],processed_email["mensagem"], file_name)
				else:
					file_name = None
				if processed_email["mensagem"] != "Não identificado":

					if processed_email["assunto"] == "Solicitacao de orcamento" and processed_email["telefone"] != "Não identificado":
						print('entrou')
						resultado = enviar_whatsapp_anexo("PSM - ADMINISTRAÇÃO", processed_email["mensagem"], file_name)
						exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
						exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
						exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"

					elif processed_email["assunto"] == "Extrato da sua conta PJ":
						pass

					else:
						pass

		exec_info += "\t\tMF\n"
		varg_erro = False

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