import win32com.client

# Inicia o Excel e acessa o arquivo aberto
excel = win32com.client.Dispatch("Excel.Application")
workbook = excel.Workbooks.Open(r"C:\Users\paulo\OneDrive\Documentos\ADM PSM.xlsb")

# Acesse a planilha
sheet = workbook.Sheets("PROJETOS")
used_range = sheet.UsedRange
last_row = used_range.Rows.Count  # Número da última linha usada
data = sheet.Range("A10"+":AU"+str(last_row)).Value
print(data)