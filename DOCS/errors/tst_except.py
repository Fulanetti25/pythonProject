def dividir(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("Erro: Tentativa de divisão por zero!")
        return None
    except ValueError:
        print("Erro: Valor inválido fornecido!")
        return None
    except Exception as e:
        print(f"Erro genérico: {e}")
        return None

# Teste da função
print(dividir(10, 0))  # Trata ZeroDivisionError
print(dividir(10, "a"))  # Trata TypeError como um erro genérico
print(dividir("dez", 5))  # Trata erro genérico com Exception
