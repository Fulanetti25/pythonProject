def main():
    try:
        print("Executando o programa principal.")
        # Código principal aqui
        resultado = 42  # Exemplo de processamento
        return resultado  # Retorna o resultado
    except Exception as e:
        print(f"Erro: {e}")
        return 1  # Retorna 1 para indicar erro

if __name__ == "__main__":
    status = main()
    print(f"Status final: {status}")
    # Encerrar com código de status (opcional em scripts Python)
    exit(status)
