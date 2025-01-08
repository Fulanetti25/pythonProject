import os
import logging
import traceback
import inspect
import win32com.client
import pandas as pd
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def etl_ExportaProjetos():
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho('Base_Projetos_Excel')
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])

	excel = win32com.client.Dispatch("Excel.Application")
	varl_aberto = any(wb.FullName == r"C:\Users\paulo\OneDrive\Documentos\ADM PSM.xlsb" for wb in
					  win32com.client.Dispatch("Excel.Application").Workbooks)
	workbook = excel.Workbooks.Open(r"C:\Users\paulo\OneDrive\Documentos\ADM PSM.xlsb")
	sheet = workbook.Sheets("PROJETOS")
	try:
		log_info = "F2"
		used_range = sheet.UsedRange
		last_row = used_range.Rows.Count  # Número da última linha usada
		data = sheet.Range("A10" + ":AU" + str(last_row)).Value
		df = pd.DataFrame(data)

		log_info = "F3"
		df = df.map(lambda x: str(x).replace(';', ',') if isinstance(x, str) else x)
		df = df.map(lambda x: str(x).replace('\n', '') if isinstance(x, str) else x)
		df = df.map(lambda x: str(x).replace('\r', '') if isinstance(x, str) else x)

		log_info = "F4"
		df.to_csv(file_name)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		if varl_aberto == True:
			workbook.Close(SaveChanges=False)
		excel.Quit()
		del excel

	return {"Resultado": str(df.shape), 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = False
	exec_info += "\tGF\n"

	exec_info += "\t\tM1\n"
	try:
		resultado = etl_ExportaProjetos()
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
