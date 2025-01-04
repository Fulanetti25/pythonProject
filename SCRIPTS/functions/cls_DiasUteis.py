import holidays
import logging
import traceback
import inspect
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra


def df_DiasUteis(var_dt_inicial, var_dt_final):
	log_info = "F1"
	varl_detail = None
	data_inicial = pd.to_datetime(var_dt_inicial)
	data_final = pd.to_datetime(var_dt_final)
	if data_inicial > data_final:
		raise ValueError("A data inicial não pode ser maior que a data final.")

	try:
		log_info = "F2"
		br_holidays = holidays.Brazil(years=range(data_inicial.year, data_final.year))
		datas = pd.date_range(start=data_inicial, end=data_final)

		log_info = "F3"
		df = pd.DataFrame({
			'data': datas,
			'dia_semana': datas.day_name(),
			'feriado': [data in br_holidays for data in datas],
			'util': [data.weekday() < 5 and (data not in br_holidays) for data in datas]
		})
		df['data'] = df['data'].dt.strftime('%Y-%m-%d')
		df['dia_semana'] = df.apply(lambda row: 'Holiday' if row['feriado'] else row['dia_semana'], axis=1)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": df[['data','dia_semana','util']], 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	ultima_barra = inspect.stack()[0].filename.rfind("\\")
	if ultima_barra == -1:
		ultima_barra = inspect.stack()[0].filename.rfind("/")
	varg_modulo = inspect.stack()[0].filename[ultima_barra + 1:]

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = df_DiasUteis('2024-12-01', '2024-12-31')
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
		log_registra(varg_modulo, inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)