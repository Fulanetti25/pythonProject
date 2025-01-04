#Exemplo 1
def dividir(a, b):
    if b == 0:
        raise ValueError("Divisão por zero não é permitida.")  # Propaga o erro para o nível superior
    return a / b

def calcular():
    return dividir(10, 0)  # Chamando dividir, erro vai subir

try:
    calcular()  # Nível superior
except ValueError as e:
    print(f"Erro subido: {e}")  # Tratar erro aqui


#Exemplo 2
def minha_funcao():
    raise ValueError("Ocorreu um erro!")

minha_funcao()
