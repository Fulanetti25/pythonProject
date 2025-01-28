from spellchecker import SpellChecker
import re

def calcular_percentual_sentido(texto):
    spell = SpellChecker(language='pt')
    # Tokenizar o texto
    palavras = re.findall(r'\b\w+\b', texto.lower())

    if not palavras:
        return 0  # Sem palavras para avaliar

    # Verificar palavras válidas no dicionário
    palavras_validas = [palavra for palavra in palavras if palavra in spell.word_frequency]
    percentual_sentido = len(palavras_validas) / len(palavras) * 100
    return percentual_sentido

mensagem = """
Preciso de uma planilha bem completa visando o controle de custos dos contratos da minha empresa.
Hoje enfrentamos uma falta de controle e de gestão orçamentária dos nossos centros de custos.
"""
print(f"Percentual de sentido: {calcular_percentual_sentido(mensagem):.2f}%")
