import requests
import json
from decouple import config
import openai


api_key = config('DANILO_GPT_API')


headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
# Modelo get para recuperar os modelos de chatGPT disponíveis.
# link = "https://api.openai.com/v1/models"
# requisicao = requests.get(link,headers=headers)
# print(requisicao)
# print(requisicao.text)

link = "https://api.openai.com/v1/chat/completions"
body = {
    "model":"gpt-3.5-turbo",
    "messages": [{"role":"user","content": "Quem é o descobridor dos sete mares?"}]
}
body = json.dumps(body)
requisicao = requests.post(link,headers=headers, data=body)

resposta = requisicao.json()
print(resposta)
mensagem = resposta["choices"][0]["message"]["content"]
print(mensagem)