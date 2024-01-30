from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FsjdejefweFRFWG#3452%@%@TRWWewrgwg4rtwghyettwwt254536g'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:breno19042003@brenocodesbanco.clysq3fxahpq.us-east-1.rds.amazonaws.com/brenocodesbanco'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Definitions of classes (Autor, Postagem, etc.) and other database configurations

# Creating the Autor and Postagem models
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), index=True)
    email = db.Column(db.String(50))
    senha = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem', backref='autor', lazy=True)

class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(50))
    descricao = db.Column(db.String(700))
    autor_nome = db.Column(db.String(255), db.ForeignKey('autor.nome'))

# Creating the database
# with app.app_context():
#     db.drop_all()
#     db.create_all()

