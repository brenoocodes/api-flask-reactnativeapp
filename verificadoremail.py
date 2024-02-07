from flask import Flask, request, url_for
from bancoconfig import *
from configemail import *
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

verificador = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/verificar/<email>', methods=['GET', 'POST'])
def verificar(email):
    token = verificador.dumps(email, salt='email-confirm')
    link = url_for('confirm_email', token=token, _external=True)
    enviar_email(email, 'Confirme seu email', link, 'email_template.html')
    
    # Verifica se o email não é None antes de criar uma instância de TokenVerificacaoEmail
    if email:
        token = TokenVerificacaoEmail(token=token, email=email)
        db.session.add(token)
        db.session.commit()
        return 'Email enviado para verificação'
    else:
        return 'Email inválido'

@app.route('/confirm_email/<token>')
def confirm_email(token):
    email = None  # Defina email como None antes do bloco try
    try:
        email = verificador.loads(token, salt='email-confirm', max_age=180)
        print(f'Token válido para o email {email}')
        usuario = Autor.query.filter_by(email=email).first()
        
        # Verifica se o usuário foi encontrado antes de atualizar o email_verificado
        if usuario:
            usuario.email_verificado = True
            db.session.commit()
            
            verificacao = TokenVerificacaoEmail.query.filter_by(token=token).first()
            
            # Verifica se a instância de TokenVerificacaoEmail foi encontrada antes de deletar
            if verificacao:
                db.session.delete(verificacao)
                db.session.commit()
                print(f'Registro na tabela TokenVerificacaoEmail removido para o email {email}')
            else:
                print(f'Registro na tabela TokenVerificacaoEmail não encontrado para o email {email}')
        else:
            print(f'Usuário não encontrado para o email {email}')
    except SignatureExpired:
        # Declare email novamente após o bloco except
        email = None
        verificacao = TokenVerificacaoEmail.query.filter_by(token=token).first()
        email_associado = verificacao.email

        
        # Verifica se a instância de TokenVerificacaoEmail foi encontrada antes de deletar
        if verificacao:
            db.session.delete(verificacao)
            db.session.commit()
            verificar(email_associado)
            return 'Token expirado, foi enviado um novo email para verificação'
        else:
            return 'Token expirado, mas registro na tabela TokenVerificacaoEmail não encontrado'
    return 'Email validado'
