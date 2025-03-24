import os
import logging
import traceback
import inspect
import pymssql
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from decouple import config
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados, json_registra, json_limpa
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_Logging import main as log_registra


local_server = config('SQL_SERVER')
local_database = config('SQL_DATABASE')
local_driver = config('SQL_DRIVER')
umbler_host = config('UMBLER_SERVER')
umbler_port = config('UMBLER_PORT')
umbler_database = config('UMBLER_DATABASE')
umbler_user = config('UMBLER_USER')
umbler_password = config('UMBLER_PASS')

def prc_executa_local(sql_query, params, resultado):
	log_info = "F1"
	varl_detail = None
	conexao = None
	dados = None

	try:
		log_info = "F2"
		conexao = fnc_abrir_local()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		if resultado == True:
			dados = fnc_recuperar_local(conn_obj, sql_query, params)
		else:
			dados = fnc_executar_local(conn_obj, sql_query, params)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		fnc_salvar_falha('SQL_SERVER', conn_log, sql_query, params)
		log_info = "F99"

	finally:
		fnc_fechar_local(conn_obj)

	return {"Resultado": dados, 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_executa_online(sql_query, params, resultado):
	log_info = "F1"
	varl_detail = None
	conexao = None
	conn_obj = None
	conn_log = None

	try:
		log_info = "F2"
		conexao = fnc_abrir_online()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		if resultado == True:
			fnc_recuperar_online(conn_obj, sql_query, params)
		else:
			fnc_executar_online(conn_obj, sql_query, params)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		fnc_salvar_falha('UMBLER', conn_log, sql_query, params)
		log_info = "F99"

	finally:
		if conn_obj:
			fnc_fechar_online(conn_obj)

	return {"Resultado": "Executado", 'Status_log': log_info, 'Detail_log': varl_detail}

def fnc_recuperar_local(conexao, query, params=None):
	log_info = "F1"
	varl_detail = None
	df = None

	try:
		log_info = "F2"
		cursor = conexao.cursor()
		cursor.execute(query, params)
		columns = [column[0] for column in cursor.description]
		data = cursor.fetchall()
		df = pd.DataFrame(data, columns=columns)
		print(df.head())

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": df, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_executar_local(conexao, query, params=None):
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


def fnc_recuperar_online(conexao, query, params=None):
	log_info = "F1"
	varl_detail = None
	df = None

	try:
		log_info = "F2"
		cursor = conexao.cursor()
		cursor.execute(query, params)
		columns = [column[0] for column in cursor.description]
		data = cursor.fetchall()
		df = pd.DataFrame(data, columns=columns)
		print(df.head())  # Exibir amostra dos dados

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": df, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_executar_online(conexao, query, params=None):
	log_info = "F1"
	varl_detail = None
	result = None

	try:
		log_info = "F2"
		cursor = conexao.cursor()
		cursor.execute(query, params)

		if query.strip().lower().startswith("select"):
			result = cursor.fetchall()
		else:
			conexao.commit()
			result = cursor.rowcount
		print(result)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": result, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_abrir_local():
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		conn = pymssql.connect(server=local_server, database=local_database)

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


def fnc_fechar_local(conexao):
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


def fnc_abrir_online():
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		conn = mysql.connector.connect(host=umbler_host, port=umbler_port, database=umbler_database, user=umbler_user, password=umbler_password)

		if conn.is_connected():
			print("✅ Conexão com MySQL bem-sucedida!")
		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": conn, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_fechar_online(conexao):
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

	return {"Resultado": "Conexão fechada", 'Status_log': log_info, 'Detail_log': varl_detail}


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
			prc_executa_local(query, params, False)

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


def fnc_carregar_df_online(df, tabela):
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

		df.to_sql(tabela, con=engine, if_exists="append", index=False)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": "Dados inseridos", 'Status_log': log_info, 'Detail_log': varl_detail}


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
		sql_params = {
			"nome": "nome_teste2", "telefone": "telefone_teste", "email": "email_teste", "assunto": "assunto_teste", "mensagem": "mensagem_teste", "c_anexos": "0", "tag": "TESTE_PYTHON"
		}
		sql_query2 = """
		select * from vactions.users
		"""
		sql_params2 = {
			"nome": "nome_teste2", "telefone": "telefone_teste", "email": "email_teste", "assunto": "assunto_teste", "mensagem": "mensagem_teste", "c_anexos": "0", "tag": "TESTE_PYTHON"
		}
		# resultado = prc_executa_local(sql_query, sql_params, False)
		resultado = prc_executa_online(sql_query2, sql_params2, True)
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