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


def get_email_uid_by_assunto(assunto):
	try:
		# Conectar ao servidor IMAP (ajuste conforme o seu servidor)
		mail = imaplib.IMAP4_SSL("imap.seuservidor.com")
		mail.login("seu_email@example.com", "sua_senha")

		# Selecionar a caixa de entrada
		mail.select("inbox")

		# Buscar e-mails com o assunto especificado
		status, messages = mail.search(None, f'BODY "{assunto}"')

		if status != "OK":
			raise Exception(f"Erro ao buscar e-mails com o assunto {assunto}")

		# Verificar se algum e-mail foi encontrado
		email_ids = messages[0].split()
		if not email_ids:
			return None

		# Pegar o primeiro e-mail encontrado
		email_id = email_ids[0]

		# Obter o UID do e-mail
		status, email_data = mail.fetch(email_id, "(BODY[HEADER.FIELDS (UID)])")
		if status != "OK":
			raise Exception(f"Erro ao obter UID para o e-mail com assunto {assunto}")

		# Extração do UID
		uid = None
		for response_part in email_data:
			if isinstance(response_part, tuple):
				# Buscar o UID no corpo da resposta
				if "UID" in str(response_part):
					uid = str(response_part).split('UID ')[1].split()[0]

		return uid

	except Exception as e:
		print(f"Erro ao buscar UID do e-mail: {e}")
		return None
	finally:
		mail.logout()


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
			raise Exception(varl_detail)

		# Lista de IDs dos e-mails
		email_ids = messages[0].split()

		for e_id in email_ids:
			# Faz a busca do e-mail pelo UID
			_, msg = mail.fetch(e_id, "(RFC822)")
			for response in msg:
				if isinstance(response, tuple):
					msg = email.message_from_bytes(response[1])

					# Decodifica o assunto
					assunto, encoding = decode_header(msg.get("Subject") or "")[0]
					if isinstance(assunto, bytes):
						encoding = encoding or "utf-8"
						assunto = assunto.decode(encoding, errors="ignore")
					else:
						assunto = assunto or "Assunto não definido"

					# Remetente
					from_email = msg.get("From")

					# Processa o corpo do e-mail
					body = None
					if msg.is_multipart():
						for part in msg.walk():
							content_type = part.get_content_type()
							content_disposition = str(part.get("Content-Disposition"))

							# Processa somente partes legíveis
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

					# Adiciona à lista de e-mails
					emails.append({
						"from": from_email,
						"assunto": assunto,
						"body": body or "Corpo vazio",
						"uid": e_id.decode("utf-8")
					})

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(
			var_modulo=__name__,
			var_funcao=inspect.currentframe().f_code.co_name,
			var_detalhe=varl_detail,
			var_erro=True
		)
		log_info = "F99"
		raise

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
	uid = None
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

		uid = msg_data.get('uid', 'UID não identificado')

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
		"uid": uid,
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


def prc_move_email(assunto, target_folder):
	log_info = "F1"
	varl_detail = None
	try:
		# Ajuste do nome da pasta de destino
		if not target_folder.startswith("INBOX."):
			target_folder = "INBOX." + target_folder

		print(f"Tentando mover para a pasta: {target_folder}")

		# Obter o UID ou número de sequência do e-mail usando o assunto
		email_uid = get_email_uid_by_assunto(assunto)
		if not email_uid:
			raise Exception(f"UID do e-mail não encontrado para o assunto {assunto}")

		print(f"UID encontrado: {email_uid}")

		# Conectar ao servidor IMAP e mover o e-mail
		mail = imaplib.IMAP4_SSL("imap.seuservidor.com")
		mail.login("seu_email@example.com", "sua_senha")
		mail.select("inbox")

		# Realiza o comando COPY para copiar o e-mail para a pasta de destino
		print(f"Executando comando COPY para UID {email_uid} na pasta {target_folder}")
		status, messages = mail.copy(email_uid, target_folder)
		print(f"Resposta do comando COPY: Status = {status}, Mensagens = {messages}")
		if status != 'OK':
			varl_detail = f"Erro ao copiar o e-mail UID {email_uid} para {target_folder}, Status: {status}, Mensagem: {messages}"
			raise Exception(varl_detail)  # Gera um erro se falhar

		# Marca o e-mail como excluído na pasta INBOX
		print(f"Executando comando STORE para marcar o e-mail UID {email_uid} como excluído")
		status, messages = mail.store(email_uid, '+FLAGS', '\\Deleted')
		print(f"Resposta do comando STORE: Status = {status}, Mensagens = {messages}")
		if status != 'OK':
			varl_detail = f"Erro ao marcar e-mail UID {email_uid} como excluído na INBOX, Status: {status}, Mensagem: {messages}"
			raise Exception(varl_detail)  # Gera um erro se falhar

		# Comando EXPUNGE para excluir definitivamente o e-mail da pasta INBOX
		print("Executando comando EXPUNGE para remover e-mails marcados")
		mail.expunge()
		print("Comando EXPUNGE executado com sucesso.")

		log_info = "F0"  # Sucesso após copiar e excluir

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"  # Erro final
		return {"Resultado": [], 'Status_log': log_info, 'Detail_log': varl_detail}

	finally:
		mail.logout()

	return {"Resultado": "Sucesso", 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_salvar_anexos(email, uid, diretorio_destino):
	try:
		# Criação do diretório caso não exista
		if not os.path.exists(diretorio_destino):
			os.makedirs(diretorio_destino)

		msg = message_from_bytes(email['Resultado'], policy=policy.default)
		arquivos_salvos = []

		# Iteração sobre os anexos da mensagem
		for part in msg.iter_attachments():
			if part.get_content_disposition() == "attachment":
				file_name = part.get_filename()
				if file_name:
					file_path = os.path.join(diretorio_destino, file_name)
					arquivos_salvos.append(file_path)

		# Exibição dos anexos encontrados
		print("\nArquivos encontrados:")
		for idx, file in enumerate(arquivos_salvos, 1):
			print(f"{idx}: {os.path.basename(file)}")

		# Confirmação do salvamento
		salvar = input("\nDeseja salvar os arquivos listados? (s/n): ").strip().lower()
		if salvar != "s":
			print("Salvamento cancelado pelo usuário.")
			return False

		# Salvar os arquivos confirmados
		for file_path in arquivos_salvos:
			with open(file_path, 'wb') as file:
				part = next(p for p in msg.iter_attachments() if os.path.join(diretorio_destino, p.get_filename()) == file_path)
				file.write(part.get_payload(decode=True))

		print("Arquivos salvos com sucesso.")
		return True

	except Exception as e:
		print(f"Erro ao salvar anexos: {e}")
		return False


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
				print(email_data['assunto'])
				if "SOLICITACAO DE ORCAMENTO" in email_data['assunto'].upper():
					processed_email = prc_process_email(email_data)
					print("UID: ", processed_email['uid'], "TEL: ", processed_email["telefone"], "MAIL: ", processed_email["email"], "TIPO: ", processed_email["assunto"])
					if processed_email["email"].startswith('SPAM,'):
						print('+1 mail SPAM')
					else:
						if processed_email["email"] != "Não identificado" or processed_email["telefone"] != "Não identificado":
							caminho = json_caminho('Contato_VCard')
							file_dir = caminho['Diretorio']
							file_name = fnc_sanitize_filename(processed_email["nome"])
							file_name = os.path.join(file_dir, file_name + '.vcf')
							fnc_gerar_vcard(processed_email["nome"], processed_email["email"],
											processed_email["telefone"], processed_email["mensagem"], file_name)
							print('CARD GERADO')
						else:
							print('CARD NÃO GERADO')
							file_name = None
						if processed_email["telefone"] != "Não identificado":
							pass
							# resultado = enviar_whatsapp_anexo("PSM - ADMINISTRAÇÃO", processed_email["mensagem"], file_name)
							# exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
							# exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
							# exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
						elif processed_email["telefone"] == "Não identificado":
							pass
							# resultado = prc_reply_mail(processed_email)
							# exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
							# exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
							# exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"

				elif email_data['assunto'].upper() == "EXTRATO DA SUA CONTA PJ":
					print('+1 extrato')
					# caminho = json_caminho('Extrato_PJ')
					# file_dir = caminho['Diretorio']
					# sucesso = salvar_anexos(mail, email_data['uid'], file_dir)
					# if sucesso:
					# 	prc_move_email(mail['Resultado'], email_data['uid'], 'EXTRATOS')

				elif email_data['assunto'][:5].upper() in ["RES: ", "ENC: "]:
					print('+1 mail ENC/RES')

				else:
					print('+1 excluido')
					prc_move_email(email_data['assunto'], 'AUTO_DELETE')
				# gravar linha no excel
				# gravar linha no Db
		else:
			print('não achou mails data')
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