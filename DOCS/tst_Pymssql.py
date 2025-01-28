import pymssql
from decouple import config

# Configurar os dados de conexão
server = config('SQL_SERVER')  # Exemplo: "localhost" ou "IP/hostname"
database = config('SQL_DATABASE')    # Nome do banco de dados

try:
    # Criar a conexão
    conn = pymssql.connect(server=server, database=database)
    print("Conexão bem-sucedida!")

    # Criar cursor para executar comandos SQL
    cursor = conn.cursor()

    # Testar SELECT
    cursor.execute("SELECT TOP 5 * FROM dbo.PRD_CONTATO")  # Substitua "SuaTabela" por uma tabela do banco
    for row in cursor.fetchall():
        print(row)

    conn.close()
except Exception as e:
    print("Erro na conexão:", e)






import pymssql
from decouple import config

# Configurar os dados de conexão
server = config('SQL_SERVER')
database = config('SQL_DATABASE')

try:
    # Criar a conexão
    conn = pymssql.connect(server=server, database=database)
    print("Conexão bem-sucedida!")

    # Criar cursor
    cursor = conn.cursor()

    # Definir comando SQL com placeholders
    # insert_query = """
    #     INSERT INTO dbo.PRD_CONTATO
    #     VALUES (%s, %s, %s)
    # """
    # Dados para inserir
    # dados = ("valor1", "valor2", 123)

    insert_query = "insert into  dbo.PRD_CONTATO values(getdate(), 'teste','5511964821360','paulo.fulanetti@hotmail.com','Mail','Conteudo',2)"

    # Executar o comando SQL
    cursor.execute(insert_query)

    # Confirmar a transação (commit)
    conn.commit()

    print("Registro inserido com sucesso!")
    conn.close()
except Exception as e:
    print("Erro ao inserir registro:", e)










import pymssql
from decouple import config

# Configurar os dados de conexão
server = config('SQL_SERVER')
database = config('SQL_DATABASE')

try:
    # Criar a conexão
    conn = pymssql.connect(server=server, database=database)
    print("Conexão bem-sucedida!")

    # Criar cursor
    cursor = conn.cursor()

    delete_query = "delete from dbo.PRD_CONTATO where nm_contato = 'teste'"

    # Executar o comando SQL
    cursor.execute(delete_query)

    # Confirmar a transação (commit)
    conn.commit()

    print("Registro excluido com sucesso!")
    conn.close()
except Exception as e:
    print("Erro ao excluir registro:", e)
