import mysql.connector
from decouple import config

# Configurações de conexão
host = config('UMBLER_SERVER')
port = config('UMBLER_PORT')
database = config('UMBLER_DATABASE')
user = config('UMBLER_USER')
password = config('UMBLER_PASS')

try:
    conn = mysql.connector.connect(host=host,port=port,database=database,user=user,password=password)

    if conn.is_connected():
        print("✅ Conexão com MySQL bem-sucedida!")

    conn.close()
except Exception as e:
    print(f"❌ Erro ao conectar ao MySQL: {e}")