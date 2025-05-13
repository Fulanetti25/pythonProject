import os
import logging
import traceback
import inspect
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse

#CALCULAR CUSTO DE VIDA PREVISTO E REALIZADO


def fnc_converter_valor(serie_valores):
	return (
		serie_valores.astype(str)
		.str.replace('.', '', regex=False)
		.str.replace(',', '.', regex=False)
		.replace('', '0')
		.astype(float)
	)


def fnc_processar_base():
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho('Extrato_PF')
	file_dir = caminhos['Diretorio']
	file_out = os.path.join(os.path.dirname(os.path.dirname(file_dir)),'Dados_PF.csv')

	try:
		log_info = "F2"
		for _, _, arquivos in os.walk(file_dir):
			for arquivo in arquivos:
				file_name = os.path.join(file_dir, arquivo)
				df_raw = pd.read_excel(file_name, sheet_name='Sheet0', engine='xlrd')
				idx_header = df_raw[df_raw.eq('Data').any(axis=1)].index[0]
				idx_fim = df_raw[df_raw.iloc[:, 0].astype(str).str.contains('Os dados acima', na=False)].index[0]
				df = df_raw.iloc[idx_header + 1:idx_fim].copy()
				df.columns = df_raw.iloc[idx_header]
				df.columns = df.columns.str.upper().str.strip().str.replace(' (R$)', '', regex=False)
				df = df.reset_index(drop=True)
				df_controle = df[df['HISTÓRICO'].isin(['SALDO ANTERIOR', 'Total'])].copy()
				df = df[~df['HISTÓRICO'].isin(['SALDO ANTERIOR', 'Total'])].reset_index(drop=True)
				df['DATA'] = df['DATA'].astype(str)
				for i in df[df['DATA'].isna() | df['DATA'].eq('nan')].index:
					df.at[i - 1, 'HISTÓRICO'] = f"{df.at[i - 1, 'HISTÓRICO']} {df.at[i, 'HISTÓRICO']}"
				df = df[~df['DATA'].isin(['nan', 'NaT'])].reset_index(drop=True)

				df['CRÉDITO'] = fnc_converter_valor(df['CRÉDITO'])
				df['DÉBITO'] = fnc_converter_valor(df['DÉBITO'])
				df_controle['CRÉDITO'] = fnc_converter_valor(df_controle['CRÉDITO'])
				df_controle['DÉBITO'] = fnc_converter_valor(df_controle['DÉBITO'])

				soma_credito = df['CRÉDITO'].sum(skipna=True)
				soma_debito = df['DÉBITO'].sum(skipna=True)
				valor_credito_total = df_controle.loc[df_controle['HISTÓRICO'] == 'Total', 'CRÉDITO'].sum()
				valor_debito_total = df_controle.loc[df_controle['HISTÓRICO'] == 'Total', 'DÉBITO'].sum()
				valor_saldo_anterior = fnc_converter_valor(df_controle.loc[df_controle['HISTÓRICO'] == 'SALDO ANTERIOR', 'SALDO']).sum()

				valor_saldo_final_calc = soma_credito + soma_debito + valor_saldo_anterior
				valor_saldo_final_real = fnc_converter_valor(df['SALDO']).dropna().iloc[-1]

				if round(valor_saldo_final_calc, 2) == round(valor_saldo_final_real, 2):
					if os.path.exists(file_out):
						df_existente = pd.read_csv(file_out, sep=',')
						df['CHAVE_UNICA'] = df.astype(str).agg('|'.join, axis=1)
						df_existente['CHAVE_UNICA'] = df_existente.astype(str).agg('|'.join, axis=1)
						df_novos = df[~df['CHAVE_UNICA'].isin(df_existente['CHAVE_UNICA'])].drop(columns='CHAVE_UNICA')
					else:
						df_novos = df
					if not df_novos.empty:
						if 'SALDO' in df_novos.columns:
							df_novos.drop(columns='SALDO', inplace=True)
							df_novos.to_csv(file_out, sep=',', mode='a', header=not os.path.exists(file_out), index=False)
				else:
					print('Arquivo ' + arquivo + ' não inserido.')

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": 'Arquivo atualizado', 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_calcular_custo():
	log_info = "F1"
	varl_detail = None
	custo_vida = {
		"Aluguel": 2151.0,
		"Condominio": 500.0,
		"Gás": 40.0,
		"Luz": 90.0,
		"Internet": 116.0,
		"Celular": 58.0,
		"Água": 76.0,
		"Convênio": 1618.0,
		"Academia": 250.0
	}

	try:
		log_info = "F2"


		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": 'Arquivo atualizado', 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = fnc_processar_base()
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