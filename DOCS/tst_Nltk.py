import re
from nltk.corpus import words
import nltk

# Baixar recursos da biblioteca NLTK
nltk.download('words')

# Lista de palavras em português (você pode usar uma lista personalizada)
palavras_portugues = set(words.words())  # Substitua por um dicionário em português confiável


# Função para calcular o percentual de sentido
def calcular_percentual_sentido(texto):
    # Remove caracteres especiais e transforma em minúsculas
    palavras = re.findall(r'\b\w+\b', texto.lower())

    if not palavras:
        return 0  # Nenhuma palavra para avaliar

    palavras_validas = [palavra for palavra in palavras if palavra in palavras_portugues]
    percentual_sentido = len(palavras_validas) / len(palavras) * 100
    return percentual_sentido


# Exemplo de mensagem
mensagem = """
Preciso de uma planilha bem completa visando o controle de custos dos contratos da minha empresa. Hoje enfrentamos uma falta de controle e de gestão orçamentária dos nossos centros de custos. 
"""

# Resultado
percentual = calcular_percentual_sentido(mensagem)
print(f"Percentual de sentido na mensagem: {percentual:.2f}%")
