import os
import logging
import traceback
import inspect
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_OutWhatsapp import fnc_SalvarFila


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
				if arquivo.lower().startswith('nu'):
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
				elif arquivo.lower().startswith('pagbank_'):
					df = pd.read_csv(file_path, sep=';', dtype=str)
					if df.shape[0] == 0:
						os.remove(file_path)
					else:
						conta_nome = arquivo.replace('.csv','').upper()
						df.insert(0, 'Conta', conta_nome)
						df.rename(columns={'CODIGO DA TRANSACAO': 'Identificador'}, inplace=True)
						df.rename(columns={'DATA': 'Data'}, inplace=True)
						df.rename(columns={'VALOR': 'Valor'}, inplace=True)
						df['Valor'] = df['Valor'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float).map(lambda x: f"{x:.2f}")

						df['Descrição'] = df.pop('TIPO').astype(str) + ' - ' + df.pop('DESCRICAO').astype(str)
						colunas_chave = ['Conta', 'Data', 'Valor', 'Identificador', 'Descrição']
						df = df[colunas_chave + [col for col in df.columns if col not in colunas_chave]]

						# Faz o merge para saber quais linhas já existem e Inicializa um DataFrame vazio para novos registros
						df_merged = df.merge(df_base[colunas_chave], on=colunas_chave, how='left', indicator=True)
						df_novos = pd.DataFrame(columns=df.columns)
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
	contas_map = {'NU_2152502229': 'NU_FULA_PJ', 'NU_500633351': 'NU_DAN_PJ', 'PAGBANK_DAN': 'PB_DAN_PJ', 'PAGBANK_FULA': 'PB_FULA_PJ'}
	caminho_base = json_caminho('Banco_Extrato')
	file_contas = os.path.join(caminho_base['Diretorio'], caminho_base['Arquivo'])
	caminho_base = json_caminho('Notas_Extrato')
	file_notas = os.path.join(caminho_base['Diretorio'], caminho_base['Arquivo'])

	try:
		log_info = "F2"
		df = pd.read_csv(file_contas, sep=',', dtype=str)
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

		log_info = "F3"
		# Totalizadores de CONTAS
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

		log_info = "F4"
		# Totalizador: SALDO CONTA TOTAL
		df_resultados['saldo']['SALDO CONTA TOTAL'] = {}

		for periodo in lista_periodos.keys():
			soma_total = 0
			for conta_nome in ['NU_FULA_PJ', 'NU_DAN_PJ', 'PB_DAN_PJ', 'PB_FULA_PJ']:
				valor = df_resultados['saldo'].get(conta_nome, {}).get(periodo, 0)
				soma_total += valor
			df_resultados['saldo']['SALDO CONTA TOTAL'][periodo] = round(soma_total, 2)

		log_info = "F5"
		# Totalizador: NOTAS FISCAIS
		df = pd.read_csv(file_notas, sep=',', dtype=str)

		df['GERACAO'] = pd.to_datetime(df['GERACAO'], format="%d/%m/%Y", errors='coerce')
		df['VALOR'] = pd.to_numeric(df['VALOR'].str.replace(',', '.'), errors='coerce')
		df = df.dropna(subset=['GERACAO', 'VALOR'])

		df_resultados['notas'] = {}  # Evita erro se chave ainda não existir

		agrupadores = {
			'NF_DAN': (df['CONTA'] == 'NF_DAN'),
			'NF_FULA EMT': (df['CONTA'] == 'NF_FULA') & (df['TIPO'] == 'EMITIDA'),
			'NF_FULA RCB': (df['CONTA'] == 'NF_FULA') & (df['TIPO'] == 'RECEBIDA')
		}

		for nome, filtro in agrupadores.items():
			df_filtrado = df[filtro]
			df_resultados['notas'][nome] = {}
			for periodo_nome, (data_ini, data_fim) in lista_periodos.items():
				df_periodo = df_filtrado[(df_filtrado['GERACAO'] >= pd.to_datetime(data_ini)) &(df_filtrado['GERACAO'] <= pd.to_datetime(data_fim))]
				soma = df_periodo['VALOR'].sum()
				df_resultados['notas'][nome][periodo_nome] = round(soma, 2)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": fnc_convert_to_float(df_resultados), 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_movimentacoes():
	log_info = "F1"
	varl_detail = None
	contas_map = {'NU_2152502229': 'NU_FULA_PJ', 'NU_500633351': 'NU_DAN_PJ', 'PAGBANK_DAN': 'PB_DAN_PJ', 'PAGBANK_FULA': 'PB_FULA_PJ'}
	caminho_base = json_caminho('Banco_Extrato')
	file_contas = os.path.join(caminho_base['Diretorio'], caminho_base['Arquivo'])

	try:
		log_info = "F2"
		df = pd.read_csv(file_contas, sep=',', dtype=str)
		df['Data'] = pd.to_datetime(df['Data'], format="%d/%m/%Y", errors='coerce')
		df['Valor'] = pd.to_numeric(df['Valor'].str.replace(',', '.'), errors='coerce')
		hoje = datetime.today().date()
		df = df.dropna(subset=['Data', 'Valor'])

		log_info = "F3"
		# Define intervalo da semana anterior (segunda a domingo)
		hoje = datetime.today().date()
		inicio_semana = hoje - timedelta(days=hoje.weekday())

		df_resultados = df[(df['Data'] >= pd.to_datetime(inicio_semana)) & (df['Data'] <= pd.to_datetime(hoje))].copy()

		log_info = "F4"
		# (Opcional) Adiciona nome de conta legível
		df_resultados['Conta'] = df_resultados['Conta'].map(contas_map).fillna(df_resultados['Conta'])
		df_resultados['Descrição'] = df_resultados['Descrição'].str.extract(r'Pix - (.*?) - (.*?)(?: -|$)')[0]

		# Remove coluna desnecessária
		df_resultados = df_resultados.drop(['Identificador'], axis=1)

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
		resultado2 = fnc_preparar_base()
		resultado3 = fnc_saldos_por_periodo()
		res = resultado3['Resultado']

		resultado4 = fnc_movimentacoes()
		df_mov = resultado4['Resultado']  # deve ser um DataFrame
		df_mov['Data'] = pd.to_datetime(df_mov['Data'], errors='coerce')
		mov_texto = '\n'.join(
			f"{linha['Data'].strftime('%d/%m')}{f'{linha['Valor']:,.2f}'.rjust(10)} - {linha['Descrição']}"
			for _, linha in df_mov.iterrows()
		)

		# Captura dos valores desejados
		saldo_total = res['saldo'].get('SALDO CONTA TOTAL', {}).get('ATUAL', 0)
		nf_dan = res['notas'].get('NF_DAN', {}).get('YTD', 0)
		nf_fula_emt = res['notas'].get('NF_FULA EMT', {}).get('YTD', 0)

		# Montagem da mensagem
		msg = (
			f"*Report Financeiro:*\n"
			f"Saldo total atual: R$ {saldo_total:,.2f}\n"
			f"NF Dan (YTD): R$ {nf_dan:,.2f}\n"
			f"NF Fula (YTD): R$ {nf_fula_emt:,.2f}\n\n"
			f"Movimentações:"
		)

		# Junta na mensagem
		msg += f"\n{mov_texto}\n"
		msg += f"*Detalhamento Completo no Google Drive*"

		resultado = fnc_SalvarFila(numero = "PSM - ADMINISTRAÇÃO", mensagem=msg, anexo = None)
		exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}:\n"
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