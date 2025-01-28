import re
import os
import unicodedata
import logging
import traceback
import inspect
from spellchecker import SpellChecker
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho


def fnc_sanitize_filename(filename):
	filename = unicodedata.normalize('NFKD', filename)
	filename = filename.encode('ascii', 'ignore').decode('ascii')
	filename = re.sub(r'[^\w\s\-_.]', '', filename)
	filename = filename.replace(" ", "_")
	return filename


def fnc_percentual_sentido(texto):
	spell = SpellChecker(language='pt')
	palavras = re.findall(r'\b\w+\b', texto.lower())
	if not palavras:
		return 0
	palavras_validas = [palavra for palavra in palavras if palavra in spell.word_frequency]
	percentual_sentido = len(palavras_validas) / len(palavras) * 100
	return percentual_sentido


def fnc_gerar_vcard(nome, email, telefone, mensagem, file_name):
	log_info = "F1"
	varl_detail = None
	caminho = json_caminho('Contato_VCard')
	file_dir = caminho['Diretorio']

	try:
		log_info = "F2"
		file_name = fnc_sanitize_filename(nome)
		file_name = os.path.join(file_dir, file_name + '.vcf')

		percentual = str(fnc_percentual_sentido(mensagem))

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

	return {"Resultado": file_name, "Percentual": percentual, 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = fnc_gerar_vcard('VTeste', 'v@v.com', '12345678', 'Teste Textual', 'Nome_Teste')
		exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
		exec_info += f"\t\t\t\tPercentual: {resultado['Percentual']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
		exec_info += "\t\tMF\n"
		varg_erro = False

	except Exception as e:
		exec_info += "\t\t\tM99\n"
		exec_info += f"Traceback: {traceback.format_exc()}"
		varg_erro = True
		raise

	finally:
		exec_info += "LF\n"
		log_registra(var_modulo=varg_modulo, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)