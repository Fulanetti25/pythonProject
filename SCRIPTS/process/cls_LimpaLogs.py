import os
import re
import logging
import traceback
import inspect
import pandas as pd
from datetime import datetime, timedelta
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def prc_LimparPesquisas():
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho("Base_Pesquisas_Google")
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])

	try:
		log_info = "F2"
		df = pd.read_csv(file_name, parse_dates=['DATA_HORA'])
		data_limite = datetime.now() - timedelta(days=31)
		df = df[df['DATA_HORA'] > data_limite]

		log_info = "F3"
		df.to_csv(file_name, index=False)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": "Higienizado", 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_LimparLogs():
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho("Log_Acompanhamento")
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])

	try:
		log_info = "F2"
		data_limite = datetime.now() - timedelta(days=1)
		regex_data = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
		linhas = []
		cortar = True
		with open(file_name, "r", encoding="utf-8", errors="replace") as f:
			for linha in f:
				match = regex_data.search(linha)
				if match:
					data_linha = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
					if data_linha > data_limite:
						cortar = False
				if not cortar:
					linhas.append(linha)

		log_info = "F3"
		if linhas:
			with open(file_name, "w", encoding="utf-8") as f:
				f.writelines(linhas)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": "Higienizado", 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado1 = prc_LimparPesquisas()
		exec_info += f"\t\t\t\tResultado: {resultado1['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado1['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado1['Detail_log']}\n"
		resultado2 = prc_LimparLogs()
		exec_info += f"\t\t\t\tResultado: {resultado2['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado2['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado2['Detail_log']}\n"
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