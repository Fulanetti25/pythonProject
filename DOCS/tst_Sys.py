import ctypes, sys
print(sys.executable)
msg = sys.argv[1]
title = sys.argv[2]
style = sys.argv[3]
ctypes.windll.user32.MessageBoxW(0,title,msg,style)

# Executar no terminal com a linha de comando
# python.exe teste_simples.py 'Teste Arg 1', 'Teste Arg 2', 'Teste Arg 3'

import sys

def main():
    var_modulo = sys.argv[1]  # Recebe o nome do módulo
    var_funcao = sys.argv[2]  # Recebe o nome da função
    var_detalhe = sys.argv[3]  # Recebe o detalhe
    var_erro = sys.argv[4]  # Recebe o erro (True/False)
    # Continue com o processamento do log