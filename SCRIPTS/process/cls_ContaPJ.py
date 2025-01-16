import os
import logging
import traceback
import inspect
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def prc_limpar_arquivos():
	log_info = "F1"
	varl_detail = None
	varl_count = 0
	caminhos = json_caminho('Extrato_PJ')
	file_dir = caminhos['Diretorio']

	try:
		log_info = "F3"
		for arquivo in os.listdir(file_dir):
			file_name = os.path.join(file_dir, arquivo)
			if os.path.isfile(file_name):
				if not arquivo.lower().endswith('.csv'):
					varl_count += 1
					os.remove(file_name)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": str(varl_count) + ' Excluidos', 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_preparar_base():
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho('Extrato_PJ')
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])
	dataframes = []
	pd.set_option('display.max_columns', None)
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_colwidth', None)

	try:
		log_info = "F3"
		for arquivo in os.listdir(file_dir):
			file_name = os.path.join(file_dir, arquivo)
			if os.path.isfile(file_name):
				if arquivo.lower().endswith('.csv'):
					if arquivo != 'NU_500633351_HISTORICO.csv':
						df = pd.read_csv(file_name)
						# df['ORIGEM_ARQUIVO'] = arquivo
						dataframes.append(df)

		log_info = "F4"
		df_final = pd.concat(dataframes, ignore_index=True)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": df_final, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_processar_base(df1):
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F3"
		caminhos = json_caminho('Extrato_PJ')
		file_dir = caminhos['Diretorio']
		file_name = os.path.join(file_dir, 'NU_500633351_HISTORICO.csv')
		df2 = pd.read_csv(file_name, sep=";")

		df3 = pd.concat([df1, df2], ignore_index=True)

		df3['Data'] = pd.to_datetime(df3['Data'], format='%d/%m/%Y')
		df3['Ano'] = df3['Data'].dt.year
		df3['Valor'] = pd.to_numeric(df3['Valor'], errors='coerce')
		df3['MES_REF'] = pd.to_datetime(df3['Data']).dt.to_period('M').astype(str).str.replace('-', '')
		df3['TIPO'] = df3['Descrição'].apply(lambda x: 'RECEITA' if 'receb' in str(x).lower() or 'crã©dito' in str(x).lower() else ('DESPESA' if 'envia' in str(x).lower() else 'OUTRO'))
		df3.drop(columns=['Identificador'], inplace=True)
		df3.drop(columns=['Descrição'], inplace=True)
		# df3.to_csv("df_final_exportado.csv", index=False)

		df_receita = (df3[df3['TIPO'] == 'RECEITA'].groupby(['Ano', 'MES_REF']).agg(RECEITA=('Valor', 'sum')).reset_index())
		df_despesa = (df3[df3['TIPO'] == 'DESPESA'].groupby(['Ano', 'MES_REF']).agg(DESPESA=('Valor', 'sum')).reset_index())
		df_saldo = (df3.groupby(['Ano', 'MES_REF']).agg(SALDO=('Valor', 'sum')).reset_index())

		df_saldo = (df_saldo.merge(df_receita, on=['Ano', 'MES_REF'], how='left').merge(df_despesa, on=['Ano', 'MES_REF'], how='left'))
		df_saldo[['RECEITA', 'DESPESA']] = df_saldo[['RECEITA', 'DESPESA']].fillna(0)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": df_saldo, 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado1 = prc_limpar_arquivos()
		exec_info += f"\t\t\t\tResultado: {resultado1['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado1['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado1['Detail_log']}\n"
		resultado2 = fnc_preparar_base()
		exec_info += f"\t\t\t\tResultado: {resultado2['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado2['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado2['Detail_log']}\n"
		resultado3 = fnc_processar_base(resultado2['Resultado'])
		exec_info += f"\t\t\t\tResultado: {resultado3['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado3['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado3['Detail_log']}\n"
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