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
	caminhos = json_caminho('Arquivo_PF')
	file_dir = caminhos['Diretorio']

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
				df = df.reset_index(drop=True)
				df_controle = df[df['Histórico'].isin(['SALDO ANTERIOR', 'Total'])].copy()
				df = df[~df['Histórico'].isin(['SALDO ANTERIOR', 'Total'])].reset_index(drop=True)
				df['Data'] = df['Data'].astype(str)
				for i in df[df['Data'].isna() | df['Data'].eq('nan')].index:
					df.at[i - 1, 'Histórico'] = f"{df.at[i - 1, 'Histórico']} {df.at[i, 'Histórico']}"
				df = df[~df['Data'].isin(['nan', 'NaT'])].reset_index(drop=True)

				df['Crédito (R$)'] = fnc_converter_valor(df['Crédito (R$)'])
				df['Débito (R$)'] = fnc_converter_valor(df['Débito (R$)'])
				df_controle['Crédito (R$)'] = fnc_converter_valor(df_controle['Crédito (R$)'])
				df_controle['Débito (R$)'] = fnc_converter_valor(df_controle['Débito (R$)'])

				soma_credito = df['Crédito (R$)'].sum(skipna=True)
				soma_debito = df['Débito (R$)'].sum(skipna=True)
				valor_credito_total = df_controle.loc[df_controle['Histórico'] == 'Total', 'Crédito (R$)'].sum()
				valor_debito_total = df_controle.loc[df_controle['Histórico'] == 'Total', 'Débito (R$)'].sum()
				valor_saldo_anterior = fnc_converter_valor(df_controle.loc[df_controle['Histórico'] == 'SALDO ANTERIOR', 'Saldo (R$)']).sum()

				valor_saldo_final_calc = soma_credito + soma_debito + valor_saldo_anterior
				valor_saldo_final_real = fnc_converter_valor(df['Saldo (R$)']).dropna().iloc[-1]

				if {valor_saldo_final_calc:.2f} == {valor_saldo_final_real:.2f}:
					print('Bateu')
				breakpoint()



		log_info = "F3"
		df['MES_REF'] = pd.to_datetime(df['Data']).dt.to_period('M').astype(str).str.replace('-', '')
		df_receita = (df[df['TIPO'] == 'RECEITA'].groupby(['Ano', 'MES_REF']).agg(RECEITA=('F_VALOR', 'sum')).reset_index())
		df_despesa = (df[df['TIPO'] == 'DESPESA'].groupby(['Ano', 'MES_REF']).agg(DESPESA=('F_VALOR', 'sum')).reset_index())
		df_saldo = (df.groupby(['Ano', 'MES_REF']).agg(SALDO=('F_VALOR', 'sum')).reset_index())

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