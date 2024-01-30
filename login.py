from flask import jsonify, request, make_response
from bancoconfig import Autor, Postagem, bcrypt, app
import jwt
from datetime import datetime, timedelta
from functools import wraps

# Mantenha uma lista de tokens inválidos (blacklist)
blacklisted_tokens = set()


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Verificar se o token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído'}, 401)

        # Verificar se o token está na lista de tokens inválidos (blacklist)
        if token in blacklisted_tokens:
            return jsonify({'mensagem': 'Token inválido'}, 401)

        # Se temos um token, verificar dados
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()

            # Verificar se o ID do usuário no token corresponde ao ID do usuário que está sendo acessado
            if 'id_autor' in kwargs and autor.id_autor != kwargs['id_autor']:
                return jsonify({'mensagem': 'Permissão negada'}, 403)

        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado'}, 401)
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token inválido'}, 401)
        except Exception as e:
            print(e)
            return jsonify({'mensagem': 'Erro interno'}, 500)

        return f(autor, *args, **kwargs)

    return decorated


@app.route('/login')
def login():
    try:
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})

        usuario = Autor.query.filter_by(email=auth.username).first()

        if not usuario:
            return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})

        if bcrypt.check_password_hash(usuario.senha, auth.password):
            token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() + timedelta(minutes=15)},
                               app.config['SECRET_KEY'])
            response_data = {
                'token': token,
                'usuario': {
                    'id_autor': usuario.id_autor,
                    'nome': usuario.nome,
                    'email': usuario.email
                }
            }
            return jsonify(response_data)
        # Mensagem específica para senha incorreta
        return make_response('Senha incorreta', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    except Exception as e:
        print(e)
        return make_response(jsonify({'mensagem': 'Não foi possível fazer login'}), 500)


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
