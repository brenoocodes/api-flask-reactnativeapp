from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FsjdejefweFRFWG#3452%@%@TRWWewrgwg4rtwghyettwwt254536g'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://bf0f2f751c2f2f:979cdde8@us-cluster-east-01.k8s.cleardb.net/heroku_5755ffd6e54179e'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Definições de classes (Autor, Postagem, etc.) e outras configurações do banco de dados


# Criando os modelos Autor e Postagem
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), index=True)  # Adicionando um índice à coluna nome
    email = db.Column(db.String(50))
    senha = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    # Definindo o relacionamento com Postagem
    postagens = db.relationship('Postagem', backref='autor', lazy=True)

class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(50))
    descricao = db.Column(db.String(700))  # Adicionando comprimento à coluna descricao
    autor_nome = db.Column(db.String(255), db.ForeignKey('autor.nome'))

# # Criando o banco de dados
#with app.app_context():
    # db.drop_all()
#   db.create_all()
