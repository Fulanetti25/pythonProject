from decouple import config
import openai

# Substitua pela sua chave da OpenAI
openai.api_key = config('DANILO_GPT_API')

def chat_with_gpt(prompt, model="gpt-4-turbo"):
    response = openai.chat.completions.create(  # Novo método de criação de chat
        model=model,
        messages=[{"role": "system", "content": "Você é um assistente útil."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

if __name__ == "__main__":
    pergunta = input("Digite sua pergunta: ")
    resposta = chat_with_gpt(pergunta)
    print("ChatGPT:", resposta)