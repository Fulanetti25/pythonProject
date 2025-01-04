import tst_traceback

def divisao(a, b):
    """
    Função simples para dividir dois números.
    """
    try:
        resultado = a / b
        return resultado
    except Exception as e:
        # Captura o rastreamento completo do erro
        erro_detalhado = traceback.format_exc()
        print("Ocorreu um erro!")
        print("Detalhes do erro:")
        print(erro_detalhado)
        #return None
        raise RuntimeError("Erro ao realizar divisão") from e

# Exemplo de uso
if __name__ == "__main__":
    print("Divisão com valores válidos:")
    print(divisao(10, 2))  # Deve retornar 5.0
    try:
        print("\nDivisão com erro (divisão por zero):")
        print(divisao(10, 0))  # Gera erro e exibe o traceback
    except RuntimeError  as e:
        print(f"Erro subido: {e}")  # Tratar erro aqui
