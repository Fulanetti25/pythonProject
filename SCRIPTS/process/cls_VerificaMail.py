import os
import re
import imaplib
import email
import logging
import traceback
import inspect
import smtplib
import unicodedata
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import message_from_bytes, policy
from bs4 import BeautifulSoup
from imapclient import imap_utf7
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


def prc_check_all_emails(mail):
	log_info = "F1"
	varl_detail = None
	emails = []

	try:
		# Busca todos os e-mails
		status, messages = mail.search(None, 'ALL')
		log_info = "F3"

		# Verifica se retornou mensagens
		if status != "OK" or not messages[0]:
			varl_detail = "Nenhum e-mail encontrado."
			log_info = "F99"

		# Lista de IDs dos e-mails
		email_ids = messages[0].split()

		for e_id in email_ids:
			# Faz a busca do e-mail pelo UID
			_, msg = mail.fetch(e_id, "(RFC822)")
			for response in msg:
				if isinstance(response, tuple):
					msg = email.message_from_bytes(response[1])
					message_id = msg.get("Message-ID")

					assunto, encoding = decode_header(msg.get("Subject") or "")[0]
					if isinstance(assunto, bytes):
						encoding = encoding or "utf-8"
						assunto = assunto.decode(encoding, errors="ignore")
					else:
						assunto = assunto or "Assunto não definido"

					from_email = msg.get("From")

					body = None
					if msg.is_multipart():
						for part in msg.walk():
							content_type = part.get_content_type()
							content_disposition = str(part.get("Content-Disposition"))

							if content_type == "text/plain" and "attachment" not in content_disposition:
								payload = part.get_payload(decode=True)
								body = fnc_decode_payload(payload)
								break
							elif content_type == "text/html" and not body:
								payload = part.get_payload(decode=True)
								body = fnc_decode_payload(payload)  # HTML como fallback
					else:
						payload = msg.get_payload(decode=True)
						body = fnc_decode_payload(payload)

					emails.append({
						"from": from_email,
						"assunto": assunto,
						"body": body or "Corpo vazio",
						"message_id": message_id
					})

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__,var_funcao=inspect.currentframe().f_code.co_name,var_detalhe=varl_detail,var_erro=True)
		log_info = "F99"

	return {"Resultado": emails, 'Status_log': log_info, 'Detail_log': varl_detail}


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
		result = payload.decode("utf-8", errors="ignore")
		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		return payload.decode("latin1", errors="ignore")  # Fallback

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

		with open(file_name, "w", encoding="utf-8") as arquivo:
			arquivo.write(vcard)
		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": file_name, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_sanitize_filename(filename):
	# Normaliza o texto para remover acentos
	filename = unicodedata.normalize('NFKD', filename)
	filename = filename.encode('ascii', 'ignore').decode('ascii')
	# Remove caracteres especiais, mantendo letras, números, espaços, traços e underscores
	filename = re.sub(r'[^\w\s\-_.]', '', filename)
	# Substitui espaços por underscores
	filename = filename.replace(" ", "_")
	return filename


def prc_process_email(msg_data):
	log_info = "F1"
	varl_detail = None
	nome = None
	email_match = None
	telefone_match = None
	mensagem = None
	email_result = None  # Variável para armazenar o resultado final do e-mail

	try:
		log_info = "F3"
		assunto = msg_data.get('assunto', 'Assunto não identificado')

		# Decodificar o campo 'from' se necessário
		if msg_data.get("from"):
			from_field = msg_data["from"]
			if isinstance(from_field, email.header.Header):
				sender = str(from_field)
			else:
				sender = from_field
			nome = sender.split("<")[0].strip() if "<" in sender else sender.strip()
			nome = nome.replace('"', '')
			nome = datetime.now().strftime("%Y%m%d") + " CLI " + nome

		# Processar o corpo do e-mail
		body = msg_data.get("body", {}).get("Resultado", "")
		body = fnc_remove_html_tags(body)
		body = body.replace("<BR>", "").replace("\r\n", " ").strip()

		# Extração de padrões
		email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
		telefone_pattern = r"(\+?\d{1,3}[ \-]?)?(\(?\d{2}\)?[ \-]?)?(9\d{4}\-?\d{4}|\d{4}\-?\d{4})"
		email_match = re.search(email_pattern, body)
		telefone_match = re.search(telefone_pattern, body)

		# Limpeza do corpo e extração da mensagem
		mensagem = body
		if email_match:
			# Remove o e-mail da mensagem
			mensagem = mensagem.replace(email_match.group(0), "").strip()
			spam = json_caminho('Json_MailSpam')
			spam_json = json_dados(os.path.join(spam['Diretorio'], spam['Arquivo']))
			email_domain = email_match.group(0).split('@')[1]  # Pega o domínio do e-mail
			for entry in spam_json['mailspam']:
				if email_domain.startswith(entry['Domain'].replace('@', '')):
					email_result = f"SPAM, {email_match.group(0)}"  # Marca com SPAM
					break
			if not email_result:  # Caso não seja spam
				email_result = email_match.group(0)  # Mantém o e-mail original

		if telefone_match:
			mensagem = mensagem.replace(telefone_match.group(0), "").strip()
		mensagem = mensagem.replace("Contato:", "").strip()
		mensagem = mensagem.replace("E-mail:", "").strip()
		mensagem = mensagem.replace("Necessidade do Cliente:", "").strip()
		mensagem = " ".join(mensagem.split()).strip()

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {
		"assunto": assunto,
		"nome": nome,
		"email": email_result if email_result else "Não identificado",  # Retorna o email com "SPAM," se necessário
		"telefone": telefone_match.group(0) if telefone_match else "Não identificado",
		"mensagem": mensagem,
		'Status_log': log_info,
		'Detail_log': varl_detail
	}


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
	try:
		mail = json_caminho('Mail_ContatoInvalido')
		mensagem_json = json_dados(os.path.join(mail['Diretorio'], mail['Arquivo']))
		mensagem_padrao = mensagem_json.get("mensagem_padrao", "Mensagem padrão não encontrada.")

		corpo_email = mensagem_padrao.format(nome=processed_email["nome"],
											 mensagem=processed_email["mensagem"],
											 email=processed_email["email"])

		# Exibir mensagem para o usuário e solicitar confirmação
		print("\nPrévia do E-mail:")
		print(f"Para: {processed_email['email']}")
		print(f"Assunto: Planilha sob Medida - Requisição de contato")
		print("Mensagem:")
		print(corpo_email)
		confirmacao = input("\nDeseja enviar este e-mail? (s/n): ").strip().lower()

		if confirmacao != 's':
			return {"Resultado": "Envio cancelado pelo usuário.", 'Status_log': "F1", 'Detail_log': "Envio cancelado."}

		resultado_envio = prc_reply_dados(processed_email["email"],
										  "Planilha sob Medida - Requisição de contato",
										  corpo_email)
		return resultado_envio

	except Exception as e:
		varl_detail = f"Erro na etapa de confirmação ou envio do e-mail, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		return {"Resultado": "Erro ao processar o envio do e-mail.", 'Status_log': "F99", 'Detail_log': varl_detail}


def prc_salvar_anexos(email, assunto, diretorio_destino):
	# INCLUIR O MESSAGE ID COMO CHAVE DA LOCALIZAÇÃO
	try:
		status, messages = email.search(None, f'SUBJECT "{assunto}"')
		if status != "OK" or not messages[0]:
			return False

		# Localiza o ID da mensagem
		msg_ids = messages[0].split()
		if not msg_ids:
			return False

		# Faz o fetch da primeira mensagem encontrada
		status, msg_data = email.fetch(msg_ids[0], "(RFC822)")
		if status != "OK":
			return False

		# Lê os dados da mensagem
		raw_email = msg_data[0][1]
		msg = message_from_bytes(raw_email, policy=policy.default)
		arquivos_salvos = []
		for part in msg.iter_attachments():
			if part.get_content_disposition() == "attachment":
				file_name = part.get_filename()
				if file_name:
					file_path = os.path.join(diretorio_destino, file_name)
					arquivos_salvos.append(file_path)
					with open(file_path, 'wb') as file:
						file.write(part.get_payload(decode=True))
		return True

	except Exception as e:
		return False


def prc_move_email(mail, message_id, target_folder):
	try:
		# Garantir que a pasta de destino comece com "INBOX."
		if not target_folder.startswith("INBOX."):
			target_folder = "INBOX." + target_folder

		# Seleciona a pasta INBOX
		mail.select("inbox")

		# Pesquisa o e-mail pelo Message-ID usando HEADER
		query = f'HEADER Message-ID "{message_id}"'
		status, messages = mail.search(None, query)

		if status != "OK" or not messages[0]:
			raise Exception(f"E-mail com o Message-ID '{message_id}' não encontrado.")

		# Mover o e-mail para a pasta destino
		email_ids = messages[0].split()
		for email_id in email_ids:
			# Copia o e-mail para a pasta de destino
			status, _ = mail.copy(email_id, target_folder)
			if status != "OK":
				raise Exception(f"Erro ao copiar o e-mail ID {email_id} para '{target_folder}'.")

			# Marca o e-mail como excluído na pasta original
			status, _ = mail.store(email_id, '+FLAGS', '\\Deleted')
			if status != "OK":
				raise Exception(f"Erro ao marcar o e-mail ID {email_id} como excluído.")

		# Expunge para remover os e-mails marcados como excluídos
		mail.expunge()


	except Exception as e:
		return False

	return True


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
	connection_result = prc_connect_email()
	mail = connection_result['Resultado']

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"

	try:
		emails_data = prc_check_all_emails(connection_result['Resultado'])["Resultado"]
		if emails_data:
			for email_data in emails_data:
				if email_data['assunto'][:5].upper() in ["RES: ", "ENC: "]:
					print('+1 mail ENC/RES')

				elif email_data['assunto'].upper() == "EXTRATO DA SUA CONTA PJ":
					caminho = json_caminho('Extrato_PJ')
					file_dir = caminho['Diretorio']
					resultado = prc_salvar_anexos(mail, email_data['assunto'], file_dir)
					if resultado:
						pass
						prc_move_email(mail, email_data['assunto'], 'AUTO_EXTRATO')

				elif "SOLICITACAO DE ORCAMENTO" in email_data['assunto'].upper():
					processed_email = prc_process_email(email_data)
					if processed_email["email"].startswith('SPAM,'):
						prc_move_email(mail, email_data['message_id'], 'AUTO_SPAM')
					else:
						if processed_email["email"] != "Não identificado" or processed_email["telefone"] != "Não identificado":
							caminho = json_caminho('Contato_VCard')
							file_dir = caminho['Diretorio']
							file_name = fnc_sanitize_filename(processed_email["nome"])
							file_name = os.path.join(file_dir, file_name + '.vcf')
							fnc_gerar_vcard(processed_email["nome"], processed_email["email"],
											processed_email["telefone"], processed_email["mensagem"], file_name)
						else:
							file_name = None
						if processed_email["telefone"] != "Não identificado":
							resultado = enviar_whatsapp_anexo("PSM - ADMINISTRAÇÃO", processed_email["mensagem"], file_name)
							exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
							exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
							exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
							prc_move_email(mail, email_data['message_id'], 'AUTO_LEAD')
						elif processed_email["telefone"] == "Não identificado":
							pass
							# resultado = prc_reply_mail(processed_email)
							# exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
							# exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
							# exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"

				else:
					prc_move_email(mail, email_data['message_id'], 'AUTO_DELETE')
				# gravar linha no Db
		else:
			exec_info += "\t\tMF\n"
			varg_erro = False

	except Exception as e:
		exec_info += "\t\t\tM99\n"
		exec_info += f"Traceback: {traceback.format_exc()}"
		varg_erro = True
		raise

	finally:
		exec_info += "LF\n"
		mail.logout()
		log_registra(varg_modulo, inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)