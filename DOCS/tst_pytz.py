import tst_pytz

# Verificar todos os fusos horários disponíveis
print(pytz.all_timezones)

# Verificar se 'America/Sao_Paulo' está listado
if 'America/Sao_Paulo' in pytz.all_timezones:
    print("Fuso horário 'America/Sao_Paulo' encontrado.")
else:
    print("Fuso horário 'America/Sao_Paulo' não encontrado.")
