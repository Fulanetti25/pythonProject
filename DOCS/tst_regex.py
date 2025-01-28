import re

def testar_regex(body):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    telefone_pattern = r"(\+?\d{1,3}[ \-]?)?(\(?\d{2}\)?[ \-]?)?(9\d{4}\-?\d{4}|\d{4}\-?\d{4})"

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
body = """
Necessidade do Cliente: UJ4SglF 1i3J oY5y3Wp pK7RpvU jI5J wtN1miO 

Contato: williamsellisbcvroa@gmail.com 

E-mail: williamsellisbcvroa@gmail.com 

"""
testar_regex(body)
