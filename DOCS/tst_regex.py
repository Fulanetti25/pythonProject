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
Necessidade do Cliente: Desenvolvimento de planilha para orçamento de servicos e produtos. 
Contato: (85) 98428-3082 
E-mail: marcos.serpa@mpenergy.com.br 
"""
testar_regex(body)
