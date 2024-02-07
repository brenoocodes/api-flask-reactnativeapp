from flask import Flask
from login import *
from autor import *
from postagem import *
from bancoconfig import *
from configemail import *
from recuperarsenha import *
from verificadoremail import *


@app.route('/', methods=['GET'])
def home():
    return '<p>Olá</p>'

if __name__ == '__main__':
    app.run(debug=True)