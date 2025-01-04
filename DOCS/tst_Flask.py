from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)
print (app)

# construir as funcionalidades
@app.route('/')
def homepage():
    return 'Essa é a homepage do site'

@app.route('/contatos')
def contatos():
    return 'Essa é a página de contatos do site'

@app.route('/pegarvendas')
def pegarvendas():
    tabela = pd.read_csv("../00 - FILES/Pasta1.csv", delimiter=";")
    return jsonify(tabela)

# rodar a nossa api
app.run(host='0.0.0.0')