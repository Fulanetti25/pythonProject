import os
import logging
import traceback
import inspect
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def fnc_convert_to_float(obj):
	if isinstance(obj, dict):
		return {k: fnc_convert_to_float(v) for k, v in obj.items()}
	elif isinstance(obj, list):
		return [fnc_convert_to_float(v) for v in obj]
	elif isinstance(obj, np.float64):
		return float(obj)
	else:
		return obj


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
	caminho = json_caminho('Extrato_PJ')
	file_dir = caminho['Diretorio']
	caminho_out = json_caminho('Banco_Extrato')
	file_out = os.path.join(caminho_out['Diretorio'], caminho_out['Arquivo'])

	pd.set_option('display.max_columns', None)
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_colwidth', None)

	try:
		log_info = "F3"
		if not os.path.exists(file_out):
			df_base = pd.DataFrame(columns=['Conta', 'Data', 'Valor', 'Identificador', 'Descrição'])
		else:
			df_base = pd.read_csv(file_out, sep=',', dtype=str)

		log_info = "F4"
		for arquivo in os.listdir(file_dir):
			file_path = os.path.join(file_dir, arquivo)
			if os.path.isfile(file_path) and arquivo.lower().endswith('.csv'):
				df = pd.read_csv(file_path, sep=',', dtype=str)
				if df.shape[0] == 0:
					os.remove(file_path)
				else:
					conta_nome = "_".join(arquivo.split("_")[:2])
					df.insert(0, 'Conta', conta_nome)

					colunas_chave = ['Conta', 'Data', 'Valor', 'Identificador', 'Descrição']

					# Faz o merge para saber quais linhas já existem
					df_merged = df.merge(df_base[colunas_chave], on=colunas_chave, how='left', indicator=True)

					# Inicializa um DataFrame vazio para novos registros
					df_novos = pd.DataFrame(columns=df.columns)

					# Percorre cada linha do DataFrame merged
					for idx, row in df_merged.iterrows():
						if row['_merge'] == 'left_only':
							# Se não existe na base, adiciona em df_novos
							df_novos = pd.concat([df_novos, row[df.columns].to_frame().T], ignore_index=True)
							# Remove esta linha do df original
							df.drop(idx, inplace=True)

					# Se houver novos registros, salva no banco de extrato
					if not df_novos.empty:
						df_novos.to_csv(file_out, sep=',', mode='a', header=not os.path.exists(file_out), index=False)

					# Se o df (agora atualizado) ainda tem linhas, sobrescreve o arquivo csv original
					if not df.empty:
						df.to_csv(file_path, sep=',', index=False)
					else:
						os.remove(file_path)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": 'banco_extrato.csv atualizado com sucesso', 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_saldos_por_periodo():
	log_info = "F1"
	varl_detail = None
	df_resultados = {'receitas': {}, 'despesas': {}, 'saldo': {}}
	contas_map = {'NU_2152502229': 'NU_FULA_PJ', 'NU_500633351': 'NU_DAN_PJ'}
	caminho_base = json_caminho('Banco_Extrato')
	file_out = os.path.join(caminho_base['Diretorio'], caminho_base['Arquivo'])

	try:
		log_info = "F2"
		df = pd.read_csv(file_out, sep=',', dtype=str)
		df['Data'] = pd.to_datetime(df['Data'], format="%d/%m/%Y", errors='coerce')
		df['Valor'] = pd.to_numeric(df['Valor'].str.replace(',', '.'), errors='coerce')

		hoje = datetime.today().date()
		df = df.dropna(subset=['Data', 'Valor'])

		lista_periodos = {
			'ATUAL': (df['Data'].min().date(), hoje),
			'YTD': (datetime(hoje.year, 1, 1).date(), hoje),
			'MTD': (datetime(hoje.year, hoje.month, 1).date(), hoje),
		}
		for i in range(1, 7):
			ref = hoje.replace(day=1) - relativedelta(months=i)
			fim_mes = ref.replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
			lista_periodos[f'M-{i}'] = (ref, fim_mes)

		for conta_cod, conta_nome in contas_map.items():
			df_conta = df[df['Conta'] == conta_cod]
			for nome, (data_ini, data_fim) in lista_periodos.items():
				df_filtrado = df_conta[
					(df_conta['Data'] >= pd.to_datetime(data_ini)) & (df_conta['Data'] <= pd.to_datetime(data_fim))]
				receitas = df_filtrado[df_filtrado['Valor'] > 0]['Valor'].sum()
				despesas = df_filtrado[df_filtrado['Valor'] < 0]['Valor'].sum()
				saldo = receitas + despesas
				for tipo, valor in zip(['receitas', 'despesas', 'saldo'], [receitas, despesas, saldo]):
					if conta_nome not in df_resultados[tipo]:
						df_resultados[tipo][conta_nome] = {}
					df_resultados[tipo][conta_nome][nome] = round(valor, 2)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": fnc_convert_to_float(df_resultados), 'Status_log': log_info, 'Detail_log': varl_detail}


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
		resultado3 = fnc_saldos_por_periodo()
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