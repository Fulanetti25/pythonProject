# https://youtu.be/hD0uJln4S2Y?list=PL3ZslI15yo2pfkf7EGNR14xTwe-wZ2bNX

# Exemplo 1
import pandas as pd
data = {'col_1': [3, 2, 1, 0], 'col_2': ['a', 'b', 'c', 'd']}
x = pd.DataFrame.from_dict(data)
print(x)

# Exemplo 2
import pandas as pd
data = {'row_1': [3, 2, 1, 0], 'row_2': ['a', 'b', 'c', 'd']}
x = pd.DataFrame.from_dict(data, orient='index')
print(x)

# Exemplo 3
import pandas as pd
x = pd.DataFrame.from_dict(data, orient='index',
                       columns=['A', 'B', 'C', 'D'])
print(x)

# Exemplo 4
import pandas as pd
data = {'index': [('a', 'b'), ('a', 'c')],
        'columns': [('x', 1), ('y', 2)],
        'data': [[1, 3], [2, 4]],
        'index_names': ['n1', 'n2'],
        'column_names': ['z1', 'z2']}
x = pd.DataFrame.from_dict(data, orient='tight')
print(x)

# Abrindo arquivo .csv e visualizando tabela e dados
import pandas as pd
tabela = pd.read_csv("00 - FILES\Pasta1.csv", delimiter=";")
print(tabela)
soma_seguidores = tabela['result_followers.total'].sum()
media_seguidores = tabela['result_followers.total'].mean()
conta_seguidores = tabela['result_followers.total'].count()
print(tabela, '\n',soma_seguidores, '\n',media_seguidores, '\n',conta_seguidores)

# Convert Json to DataFrame
# https://www.youtube.com/watch?v=V5kBzzsLqw4
import pandas as pd
a = '[[["times complex","house"],["1530","house_number"],["new street","road"],["mumbai","city"],["India","country"]]]\n'
data = pd.DataFrame({key: val for val, key in eval(a)[0]}, index=[0])
print(data)

pd.json_normalize(result) # normalizar tabela
pd.head() # 4 primeiras linhas