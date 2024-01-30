from flask import Flask, jsonify

app = Flask(__name__)

# Dados de exemplo para usuários
usuarios = [
    {"id": 1, "nome": "João"},
    {"id": 2, "nome": "Maria"},
    {"id": 3, "nome": "José"}
]

# Rota para obter a lista de usuários
@app.route('/', methods=['GET'])
def home():
    return '<p>Olá</p>'
@app.route('/usuarios', methods=['GET'])
def obter_usuarios():
    return jsonify(usuarios)


if __name__ == '__main__':
    app.run(debug=True)
