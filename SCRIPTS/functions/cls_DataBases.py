import os
import logging
import traceback
import inspect
import re
import pymssql
import mysql.connector
import pandas as pd
from datetime import datetime
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


def prc_executa_local(sql_query, params, modo):
	log_info = "F1"
	varl_detail = None
	conexao = None
	retorno = None

	try:
		log_info = "F2"
		conexao = fnc_abrir_local()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		if modo == 'COUNT':
			retorno = fnc_consultar_contagem(conn_obj, sql_query, params)
		elif modo == 'SELECT':
			retorno = fnc_recuperar_dados(conn_obj, sql_query, params)
		elif modo == 'INSERT':
			retorno = fnc_executar_modificacao(conn_obj, sql_query, params)
		elif modo == 'DELETE':
			pass
		elif modo == 'UPDATE':
			pass

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		if isinstance(params, dict) and params.get("tag") == "AUTO_DELETE":
			params_falha = {}
		else:
			params_falha = params
		fnc_salvar_falha('SQL_SERVER', conn_log, sql_query, params_falha)
		log_info = "F99"

	finally:
		fnc_fechar_local(conn_obj)

	return {"Resultado": retorno, 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_executa_online(sql_query, params, modo):
	log_info = "F1"
	varl_detail = None
	conexao = None
	conn_obj = None
	conn_log = None
	retorno = None

	try:
		log_info = "F2"
		conexao = fnc_abrir_online()
		conn_obj = conexao.get("Resultado")
		conn_log = conexao.get("Detail_log")

		log_info = "F3"
		if modo == 'COUNT':
			retorno = fnc_consultar_contagem(conn_obj, sql_query, params)
		elif modo == 'SELECT':
			retorno = fnc_recuperar_dados(conn_obj, sql_query, params)
		elif modo == 'INSERT':
			retorno = fnc_executar_modificacao(conn_obj, sql_query, params)
		elif modo == 'DELETE':
			pass
		elif modo == 'UPDATE':
			pass

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		if modo not in ['SELECT', 'COUNT']:
			fnc_salvar_falha('UMBLER', conn_log, sql_query, params)
		log_info = "F99"
		raise Exception(varl_detail)

	finally:
		if conn_obj:
			fnc_fechar_online(conn_obj)

	return {"Resultado": retorno if retorno is not None else {}, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_recuperar_dados(conexao, query, params=None):
	log_info = "F1"
	varl_detail = None
	df = None
	cursor = None

	try:
		log_info = "F2"
		query = "SELECT * FROM " + query.strip()
		cursor = conexao.cursor()
		cursor.execute(query, params or ())

		columns = [column[0] for column in cursor.description]
		data = cursor.fetchall()
		df = pd.DataFrame(data, columns=columns)

		if not df.empty:
			primeira_coluna = df.columns[0]
			try:
				amostra = df[primeira_coluna].dropna().astype(str).iloc[0]
				formato = None
				if re.fullmatch(r'\d{2}/\d{2}/\d{4}', amostra):
					formato = '%d/%m/%Y'
				elif re.fullmatch(r'\d{4}-\d{2}-\d{2}', amostra):
					formato = '%Y-%m-%d'

				df[primeira_coluna] = pd.to_datetime(
					df[primeira_coluna].astype(str).str.strip(),
					format='%d/%m/%Y %H:%M:%S',
					errors='coerce'
				)

				# Se falhar (todos nulos), tenta com apenas data
				if df[primeira_coluna].isna().all():
					df[primeira_coluna] = pd.to_datetime(
						df[primeira_coluna].astype(str).str.strip(),
						format='%d/%m/%Y',
						errors='coerce'
					)

				if df[primeira_coluna].notna().all():
					df = df.sort_values(by=primeira_coluna, ascending=True)

			except Exception:
				pass

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	return {"Resultado": df, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_consultar_contagem(conexao, query, params=None):
	log_info = "F1"
	varl_detail = None
	linhas = 0

	try:
		log_info = "F2"
		query = "SELECT COUNT(1) FROM " + query.strip()
		cursor = conexao.cursor()
		cursor.execute(query, params or ())

		resultado = cursor.fetchone()
		if resultado is None:
			linhas = 0  # Se não houver resultado, retorna 0
			varl_detail = f"{log_info}, Nenhum resultado encontrado para a consulta."
		else:
			linhas = resultado[0]  # Pega o valor da contagem

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	finally:
		pass

	return {"Resultado": linhas, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_executar_modificacao(conexao, query, params=None):
	log_info = "F1"
	varl_detail = None
	linhas_afetadas = None
	cursor = None

	try:
		log_info = "F2"

		cursor = conexao.cursor()
		cursor.execute(query, params or ())
		conexao.commit()

		linhas_afetadas = cursor.rowcount
		print(linhas_afetadas, ' linhas afetadas')
		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		fnc_salvar_falha('SQL_SERVER', conexao, query, params)
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	finally:
		if cursor:
			cursor.close()

	return {"Resultado": linhas_afetadas, 'Status_log': log_info, 'Detail_log': varl_detail}


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
		fnc_salvar_falha('UMBLER', conexao, query, params)
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
		cursor = conn.cursor()

		cursor.execute("SELECT 1")
		# print("✅ Conexão com SQLServer Aberta!")
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
		# print("❌ Conexão com SQLServer Fechada!")

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
	conn = None

	try:
		log_info = "F2"
		conn = mysql.connector.connect(host=umbler_host, port=umbler_port, database=umbler_database, user=umbler_user, password=umbler_password)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(var_modulo=__name__, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise RuntimeError(f"Erro ao abrir conexão: {e}")

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


def fnc_ReprocessarFalhaDB():
	log_info = "F1"
	varl_detail = None
	falhas_sql = json_caminho('Json_Falhas_SQL')
	falhas_path = os.path.join(falhas_sql['Diretorio'], falhas_sql['Arquivo'])

	try:
		log_info = "F2"
		pilha = json_dados(falhas_path)

		log_info = "F3"
		for falha in pilha:
			if falha.get("server") in ("SQL_SERVER","UMBLER"):
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
		resultado = fnc_ReprocessarFalhaDB()
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