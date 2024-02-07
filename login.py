from flask import jsonify, request, make_response
from bancoconfig import Autor, app, bcrypt, db, TokenVerificacaoEmail
from datetime import datetime, timedelta
from functools import wraps
import jwt
from configemail import *
from verificadoremail import *

# Lista de tokens inválidos (blacklist)
blacklisted_tokens = set()

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'mensagem': 'Token não incluído!'}, 401)
        # Se temos token, validar no banco de dados
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token é inválido'}), 401

        return f(autor, *args, **kwargs)

    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login Obrigatório"'})

    usuario = Autor.query.filter_by(email=auth.username).first()

    if not usuario:
        return make_response('Não existe esse usuário cadastrado', 401, {'WWW-Authenticate': 'Basic realm="Login Obrigatório"'})

    if bcrypt.check_password_hash(usuario.senha, auth.password):
        if usuario.email_verificado:
            print("Senha válida! Usuário verificado.")
            token = jwt.encode({'id_autor': usuario.id_autor, 'exp': (datetime.utcnow() + timedelta(days=15)).timestamp()},
                              app.config['SECRET_KEY'])
            response_data = {
                'token': token,
                'id_autor': usuario.id_autor,
                'nome': usuario.nome,
                'email': usuario.email
                
            }
            return jsonify(response_data)
        else:
            # Verifica se o último token enviado foi há menos de 3 minutos
            ultimo_token = TokenVerificacaoEmail.query.filter_by(email=usuario.email).order_by(TokenVerificacaoEmail.timestamp.desc()).first()

            if ultimo_token:
                print('Há ultimo token')
                tempo_atual = datetime.utcnow()
                tempo_envio_token = ultimo_token.timestamp
                tempo_limite = tempo_envio_token + timedelta(minutes=3)
                if tempo_atual <= tempo_limite:
                    tempo_restante = int((tempo_limite - tempo_atual).total_seconds())
                    print(f'Tempo Restante: {tempo_restante} segundos')
                    return jsonify({'mensagem': f'O seu token foi enviado há 3 minutos ou menos, portanto ainda está válido. Clique no link dele ou aguarde os 3 minutos. Tempo restante: {tempo_restante} segundos'}), 401
                else:
                    # Se passaram mais de 3 minutos, apagar registro de token e enviar novo token
                    if ultimo_token:
                        db.session.delete(ultimo_token)
                        db.session.commit()

                    verificar(usuario.email)
                    return make_response('Um novo token foi enviado para verificação. Verifique seu email.', 401, {'WWW-Authenticate': 'Basic realm="Login Obrigatório"'})

    else:
        return make_response('Senha incorreta', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})




@app.route('/logout')
@token_obrigatorio
def logout(autor):
    try:
        # Adicione o token atual à lista de tokens inválidos
        blacklisted_tokens.add(request.headers['x-access-token'])

        return jsonify({'mensagem': 'Logout bem-sucedido'})

    except Exception as e:
        print(e)
        return jsonify({'mensagem': 'Não foi possível fazer logout'}, 500)
