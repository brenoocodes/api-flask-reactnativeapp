from flask import request, jsonify, render_template, redirect, url_for
from bancoconfig import *
from configemail import *
from configemail import *
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

verificador = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/recuperar_senha', methods=['POST'])
def recuperar_senha():
    try:
        data = request.get_json()
        email_alterar = data.get('email')  # Aqui pegamos o email enviado pelo cliente
        print(email_alterar)
        autor = Autor.query.filter_by(email=email_alterar).first()
        if autor:
            novasenha(email_alterar)
            return jsonify({'Mensagem': 'Autor encontrado, foi enviado um email para recuperação'})
        else:
            return jsonify({'Mensagem': 'Autor inexistente'})
    except Exception as e:
        return str(e)

@app.route('/nova_senha/<email>', methods=['GET', 'POST'])
def novasenha(email):
    token = verificador.dumps(email, salt='email-confirm')
    link = url_for('mudar_senha', token=token, _external=True)
    enviar_email(email, 'Mude sua senha', link, 'recuperacao_senha_template.html')
    return jsonify({'Mensagem': 'Email de recuperação enviado'})


@app.route('/mudar_senha/<token>', methods=['GET', 'POST'])
def mudar_senha(token):
    try:
        # Verificando se o método é GET (para renderizar o formulário)
        if request.method == 'GET':
            # Renderiza o template HTML para a página de mudança de senha
            return render_template('nova_senha.html', token=token)
        
        # Verificando se o método é POST (quando o formulário é enviado)
        elif request.method == 'POST':
            # Recebendo a nova senha e a confirmação da senha do formulário
            nova_senha = request.form['nova_senha']
            confirmar_senha = request.form['confirmar_senha']
            
            # Verificando se a nova senha e a confirmação da senha coincidem
            if nova_senha != confirmar_senha:
                return jsonify({'Mensagem': 'A nova senha e a confirmação da senha não coincidem'})
            
            # Decodificando o token para obter o email do usuário
            email = verificador.loads(token, salt='email-confirm', max_age=3600)  # 1 hora de validade
            
            # Buscando o autor no banco de dados com base no email
            autor = Autor.query.filter_by(email=email).first()
            if not autor:
                return jsonify({'Mensagem': 'Autor não encontrado'})
            
            # Criptografando a nova senha
            senha_criptografada = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
            
            # Atualizando a senha do autor
            autor.senha = senha_criptografada
            
            # Salvando as alterações no banco de dados
            db.session.commit()
            
            autor.email_verificado = True
            db.session.commit()

            verificacao = TokenVerificacaoEmail.query.filter_by(email=email).first()
            if verificacao:
                db.session.delete(verificacao)
                db.session.commit()
            
            # Redirecionando para a página de confirmação de mudança de senha
            return redirect(url_for('senha_modificada'))
    
    except Exception as e:
        return str(e)

# Rota para a página de confirmação de mudança de senha
@app.route('/senha_modificada')
def senha_modificada():
    return render_template('senha_modificada.html')
