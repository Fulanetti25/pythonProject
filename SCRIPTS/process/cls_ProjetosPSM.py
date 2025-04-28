import logging
import traceback
import inspect
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_DataBases import prc_executa_local


def fnc_padronizar_datas(serie_datas):
	datas = pd.to_datetime(serie_datas, errors='coerce', utc=True)
	nao_convertidas = serie_datas[datas.isna()]
	if not nao_convertidas.empty:
		datas_corrigidas = pd.to_datetime(nao_convertidas, errors='coerce', dayfirst=True, utc=True)
		datas.update(datas_corrigidas)
	datas = datas.dt.tz_localize(None)

	return datas


def fnc_projetos_por_periodo():
	log_info = "F1"
	varl_detail = None

	try:
		log_info = "F2"
		hoje = pd.Timestamp.now(tz=None).normalize()
		inicio_mes = hoje.replace(day=1)
		inicio_ano = hoje.replace(month=1, day=1)

		resultado = prc_executa_local('dbo.PRD_PROJETOS', None, "SELECT")
		df_raw = resultado["Resultado"]['Resultado']
		df_raw.to_csv(r'G:\Meu Drive\PSM\01 - OPERACIONAL\00_FONTES\saida.csv', sep=';', mode='w', index=False)

		df = pd.DataFrame(df_raw) if not isinstance(df_raw, pd.DataFrame) else df_raw
		df['DATA_CRIACAO'] = fnc_padronizar_datas(df['CNTT_DATA'])

		periodos = []
		for data in df['DATA_CRIACAO']:
			if data > hoje:
				periodos.append(None)
			elif data >= inicio_mes:
				periodos.append("MTD")
			elif data >= inicio_ano:
				periodos.append("YTD")
			else:
				for i in range(1, 7):
					ref = (inicio_mes - pd.DateOffset(months=i))
					if data >= ref and data < ref + pd.DateOffset(months=1):
						periodos.append(f"M-{i}")
						break
				else:
					periodos.append("ATUAL")

		df['PERIODO'] = periodos
		df['PERIODO'] = df['PERIODO'].fillna("ATUAL")

		log_info = "F3"
		df_base = df.copy()
		agrupado = df_base.groupby('PERIODO')
		df_resultado = pd.DataFrame()

		df_resultado['total Leads'] = agrupado.size()
		filtro_validos = df['PROJ_APROVAÇÃO'].str.startswith(('2', '3')) & (df['PROJ_APROVAÇÃO'] != '3 - INVÁLIDO')
		df_validos = df[filtro_validos]
		df_resultado['Leads Válidos'] = df_validos.groupby('PERIODO').size()
		df_resultado['% Leads Válidos'] = (df_resultado['Leads Válidos'] / df_resultado['total Leads']).fillna(0).round(2)
		filtro_aprovado = df['PROJ_APROVAÇÃO'] == '2 - APROVADO'
		df_aprovado = df[filtro_aprovado]
		df_resultado['total Aprovado'] = df_aprovado.groupby('PERIODO').size()
		df_resultado['% Sucesso COM'] = (df_resultado['total Aprovado'] / df_resultado['Leads Válidos']).fillna(0).round(2)
		filtro_sucesso = df['PROJ_STATUS'] == '6 - PSM_SUCESSO'
		df_sucesso = df[filtro_sucesso]
		df_resultado['% Sucesso DEV'] = (df_sucesso.groupby('PERIODO').size() / df_resultado['total Aprovado']).fillna(0).round(2)
		filtro_andamento = df['PROJ_STATUS'] == '2-DEV_ANDAMENTO'
		df_resultado['Projetos Andamento'] = df[filtro_andamento].groupby('PERIODO').size()
		ordem = ["ATUAL", "YTD", "MTD", "M-1", "M-2", "M-3", "M-4", "M-5", "M-6"]
		df_resultado = df_resultado.reindex(ordem).fillna(0).astype(int)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"{log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": df_resultado.reset_index(), 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = fnc_projetos_por_periodo()
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