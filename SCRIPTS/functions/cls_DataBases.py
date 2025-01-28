import logging
import traceback
import inspect
import pymssql
from decouple import config
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_Logging import main as log_registra


server = config('SQL_SERVER')
database = config('SQL_DATABASE')


def fnc_connect_local():
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		conn = pymssql.connect(server=server, database=database)
		cursor = conn.cursor()

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail,
					 var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": conn, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_close_local(conexao):
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		conexao.close()

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": "Conexão fechada", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_execute_sql(conexao, query, params=None):
	log_info = "F1"
	varl_detail = None
	result = None  # Vai armazenar o resultado da consulta

	try:
		log_info = "F2"
		cursor = conexao.cursor()

		# Executar comando SQL
		cursor.execute(query, params)

		# Verifica se a query é um SELECT
		if query.strip().lower().startswith("select"):
			result = cursor.fetchall()  # Retorna todos os resultados
		else:
			conexao.commit()
			result = cursor.rowcount  # Número de linhas afetadas para INSERT, UPDATE, DELETE

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": result, 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = fnc_connect_local()
		print(resultado['Resultado'])
		x = fnc_execute_sql(resultado['Resultado'], "select * from master.dbo.PRD_CONTATO", params=None)
		print(x['Resultado'])
		# exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
		# exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
		# exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
		exec_info += "\t\tMF\n"
		varg_erro = False

	except Exception as e:
		exec_info += "\t\t\tM99\n"
		exec_info += f"Traceback: {traceback.format_exc()}"
		varg_erro = True
		raise

	finally:
		exec_info += "LF\n"
		fnc_close_local(resultado['Resultado'])
		log_registra(var_modulo=varg_modulo, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)