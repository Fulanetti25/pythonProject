import tst_xlwings as xw

try:
    # Conectando à instância do Excel
    app = xw.apps.active  # Obtém a instância ativa do Excel
    wb = app.books['ADM PSM.xlsb']  # Nome do arquivo já aberto
    sheet = wb.sheets['PROJETOS']  # Nome da planilha que deseja acessar

    used_range = sheet.used_range
    last_row = used_range.last_cell.row  # Última linha usada
    print(f"A última linha usada é: {last_row}")

    # Lendo um intervalo de dados (ajuste conforme necessário)
    data = sheet.range('A10:AU10').value  # Substitua pelo intervalo de interesse
    print(data)

except Exception as e:
    print(f"Erro ao acessar o arquivo Excel: {e}")
