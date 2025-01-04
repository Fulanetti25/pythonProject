import re

def testar_regex(body):
    # Expressões regulares
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    telefone_pattern = r"\+?\d{1,3}\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}|\d{2}\s?\d{4,5}-?\d{4}"

    # Teste para o e-mail
    email_match = re.search(email_pattern, body)
    if email_match:
        print(f"E-mail encontrado: {email_match.group()}")
    else:
        print("Nenhum e-mail encontrado.")

    # Teste para o telefone
    telefone_match = re.search(telefone_pattern, body)
    if telefone_match:
        print(f"Telefone encontrado: {telefone_match.group()}")
    else:
        print("Nenhum telefone encontrado.")

# Testando a entrada
body = "E-mail: Leferreira373@gmail.com Telefone: 16 992127140"
testar_regex(body)
