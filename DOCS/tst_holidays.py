import pandas as pd
import tst_holidays

# Exemplo de datas
data_inicial = pd.to_datetime("2024-11-01")
data_final = pd.to_datetime("2024-11-30")

# Definindo os feriados nacionais (exemplo para o Brasil)
br_holidays = holidays.Brazil(years=[2024])
print(br_holidays)

# Gerando um intervalo de datas entre as duas datas
todos_os_dias = pd.date_range(start=data_inicial, end=data_final, freq='B')  # freq='B' retorna apenas dias úteis

# Filtrando os feriados
dias_uteis_com_feriados = todos_os_dias[~todos_os_dias.isin(br_holidays.keys())]

# Contando os dias úteis (excluindo feriados)
dias_uteis_sem_feriados = len(dias_uteis_com_feriados)

print(f"Dias úteis (sem considerar feriados): {len(todos_os_dias)}")
print(f"Dias úteis (excluindo feriados): {dias_uteis_sem_feriados}")
