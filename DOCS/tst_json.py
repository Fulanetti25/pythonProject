import tst_json

json_string = '''
    {
        "students": [
            {
                "id": 1,
                "name": "Tim",
                "age": 21,
                "fulltime": true
            },
            {
                "id": 2,
                "name": "Joe",
                "age": 33,
                "fulltime": false
            }
        ]
    }
'''

# Saída em Laço
data = json.loads(json_string)
for i in range(0, len(data['students'])):
    print(data['students'][i])

# Saída Padrão
print(1, data)
print(2, data['students'])
print(3, data['students'][0])
print(4, data['students'][0]['name'])

# Entrada
data['test'] = True
#new_json = json.dumps(data)
#new_json = json.dumps(data, indent = 2)
#new_json = json.dumps(data, indent = 4)
new_json = json.dumps(data, indent = 4, sort_keys=True)
print(new_json)

# Lendo arquivo
import tst_json
with open ("FILES\data.json", "r") as f:
    data = json.load(f)
print(data.items())

# Escrevendo arquivo
import tst_json
with open("FILES\data.json", "w") as f:
    json.dump(data, f)

# Utilizando método .get() - Renan
dict = {'a':1,'b':2}
x = dict.get('a')
print(x)
y = dict.get('c')
print(y)
z = dict.get('c', 'Default')


# Carregamento de agenda local:
import tst_json

def carregar_agendas():
    try:
        caminho_arquivo = r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\SCRIPTS\config\agenda.json"
        with open(caminho_arquivo, "r") as arquivo_json:
            dados = json.load(arquivo_json)
            return dados.get("agenda", [])
    except FileNotFoundError:
        print("Arquivo 'process.json' não encontrado.")
        return []
    except json.JSONDecodeError:
        print("Erro ao ler o arquivo JSON.")
        return []

agendas = carregar_agendas()
print(agendas)