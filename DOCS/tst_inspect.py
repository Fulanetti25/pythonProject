import tst_inspect

def minha_funcao():
    nome_funcao = inspect.currentframe().f_code.co_name
    print(nome_funcao)  # Vai imprimir 'minha_funcao'

def obter_nome_modulo():
    # Usando __name__ para pegar o nome do módulo atual
    nome_modulo = __name__
    return nome_modulo

# Chama a função
minha_funcao()

# Fora de qualquer função
nome_funcao_global = inspect.currentframe().f_code.co_name
print(nome_funcao_global)  # Vai imprimir '<module>'
print(obter_nome_modulo()) # Vai imprimir '__main__'

#Laço que percorre a execução completa
stack = inspect.stack()
for i, frame_info in enumerate(stack):
    print(f"Frame {i}:")
    print(f"  Arquivo: {frame_info.filename}")
    print(f"  Linha: {frame_info.lineno}")
    print(f"  Função: {frame_info.function}")
    print(f"  Módulo: {frame_info.frame.f_globals['__name__']}")
    print("-" * 40)