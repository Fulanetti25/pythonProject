import pyodbc
from decouple import config

# Configurar os dados de conexão
server = config('SQL_SERVER')  # Exemplo: "localhost" ou "IP/hostname"
database = config('SQL_DB')    # Nome do banco de dados

try:
    # Criar a conexão usando Trusted_Connection
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )
    print("Conexão bem-sucedida!")
except Exception as e:
    print("Erro na conexão:", e)

necessário odbc... pqp