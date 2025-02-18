import os
import logging
import traceback
import inspect
import pymssql
from decouple import config
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados, json_registra, json_limpa
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

		cursor.execute(query, params)

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


def fnc_salvar_falha(server, conn_log, sql_query, params):
	log_info = "F1"
	varl_detail = None
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_dados = json_dados(os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

	try:
		log_info = "F2"
		pilha = falhas_dados if falhas_dados else []
		falha = {
			"server": server,
			"log": conn_log,
			"query": sql_query,
			"params": params,
		}

		if falha not in pilha:
			pilha.append(falha)
			json_registra(pilha, arquivo=os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo']))

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": "Inserido na pilha", 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_reprocessar_falha():
	log_info = "F1"
	varl_detail = None
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_path = os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo'])

	try:
		log_info = "F2"
		pilha = json_dados(falhas_path)

		log_info = "F3"
		for falha in pilha:
			query = falha["query"]
			params = falha["params"]
			prc_executa_db(query, params)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		if log_info == "F0":
			pass
			json_limpa(falhas_path)

	return {"Resultado": "Pilha Reprocessada", 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_executa_db(sql_query, params):
	log_info = "F1"
	varl_detail = None
	conexao = None

	try:
		log_info = "F2"
		conexao = fnc_connect_local()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		fnc_execute_sql(conn_obj, sql_query, params)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		fnc_salvar_falha('SQL_SERVER', conn_log, sql_query, params)
		log_info = "F99"

	finally:
		fnc_close_local(conn_obj)

	return {"Resultado": "Executado", 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		sql_query = """
		INSERT INTO dbo.PRD_CONTATOMAIL
		VALUES (GETDATE(), %(nome)s, %(telefone)s, %(email)s, %(assunto)s, %(mensagem)s, %(c_anexos)s, %(tag)s)
		"""
		params = {
			"nome": "nome_teste2", "telefone": "telefone_teste", "email": "email_teste", "assunto": "assunto_teste", "mensagem": "mensagem_teste", "c_anexos": "0", "tag": "TESTE_PYTHON"
		}

		resultado = prc_executa_db(sql_query, params)
		# resultado = fnc_reprocessar_falha()
		exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
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