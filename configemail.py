# configemail.py

from flask import jsonify, url_for, render_template
from flask_mail import Message, Mail
from itsdangerous import URLSafeSerializer
from bancoconfig import db, Autor, TokenVerificacaoEmail, app

configemailemail = 'bscbreno1904@gmail.com'
configemailsenha = 'zaxqpypgchmbsfwf'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = configemailemail
app.config['MAIL_PASSWORD'] = configemailsenha

mail = Mail(app)
serializer = URLSafeSerializer(app.config['SECRET_KEY'])

# Adicione a definição da variável BASE_URL
BASE_URL = 'https://api-flask-react-native-477345c2653f.herokuapp.com'  # Substitua pela URL local do seu aplicativo


def ler_html(arquivo_html):
    with open(arquivo_html, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

def enviar_email_dinamico(destinatario, assunto, link_botao, arquivo_template, base_url=BASE_URL):
    remetente = configemailemail

    # Construa o link completo usando BASE_URL
    link_completo = f'{base_url}{link_botao}'

    # Lendo o conteúdo HTML do arquivo
    conteudo_html = ler_html(arquivo_template)

    # Renderizando o template HTML
    conteudo_html = conteudo_html.replace('{{ link_botao }}', link_completo)

    mensagem = Message(assunto, sender=remetente, recipients=[destinatario])
    mensagem.html = conteudo_html

    try:
        mail.send(mensagem)
        print('Email enviado com sucesso!')
        return True
    except Exception as e:
        print('Erro ao enviar o email:')
        print(str(e))
        return False


# Exemplo de uso da função
# destinatario = 'brenos200304@gmail.com'
# assunto = 'Assunto do Email'
# link_botao = 'https://chat.openai.com'
# template = 'templates/email_template.html'

# with app.app_context():
#     enviar_email_dinamico(destinatario, assunto, link_botao, template)


