from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FsjdejefweFRFWG#3452%@%@TRWWewrgwg4rtwghyettwwt254536g'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:breno19042003@brenocodesbanco.clysq3fxahpq.us-east-1.rds.amazonaws.com/brenocodesbanco'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:breno19042003@localhost/blog'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), index=True)
    email = db.Column(db.String(50), unique=True)
    senha = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    email_verificado = db.Column(db.Boolean, default=False)  # Adicionando campo de verificação de e-mail
    postagens = db.relationship('Postagem', backref='autor', lazy=True)

    def __init__(self, nome, email, senha, admin=False, email_verificado=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.admin = admin
        self.email_verificado = email_verificado

class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(50))
    descricao = db.Column(db.String(700))
    autor_nome = db.Column(db.String(255), db.ForeignKey('autor.nome'))

# Adicionando a tabela para armazenar tokens de verificação de e-mail
class TokenVerificacaoEmail(db.Model):
    __tablename__ = 'token_verificacao_email'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(50), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Adiciona a coluna de data e hora

    def __init__(self, token, email):
        self.token = token
        self.email = email




# Criar o database
# with app.app_context():
#     db.drop_all()
#     db.create_all()