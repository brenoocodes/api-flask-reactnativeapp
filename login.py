# login.py

from flask import jsonify, request, make_response
from bancoconfig import Autor, app, bcrypt, db, TokenVerificacaoEmail
from datetime import datetime, timedelta
from functools import wraps
import jwt
from configemail import *

# Lista de tokens inválidos (blacklist)
blacklisted_tokens = set()

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Verificar se o token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído'}), 401

        # Verificar se o token está na lista de tokens inválidos (blacklist)
        if token in blacklisted_tokens:
            return jsonify({'mensagem': 'Token inválido'}), 401

        # Se temos um token, verificar dados
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()

            # Verificar se o ID do usuário no token corresponde ao ID do usuário que está sendo acessado
            if 'id_autor' in kwargs and autor.id_autor != kwargs['id_autor']:
                return jsonify({'mensagem': 'Permissão negada'}), 403

            # Verificar se o e-mail do usuário está verificado
            if not autor.email_verificado:
                # Se o e-mail não estiver verificado, reenvie um novo token
                gerar_e_enviar_token(autor.email)
                return jsonify({'mensagem': 'E-mail não verificado. Um novo token foi enviado para ativação'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token inválido'}), 401
        except Exception as e:
            print(e)
            return jsonify({'mensagem': 'Erro interno'}), 500

        return f(autor, *args, **kwargs)

    return decorated


def gerar_e_enviar_token(email):
    try:
        # Verificar se já existe um token para o e-mail na tabela
        token_registro_existente = TokenVerificacaoEmail.query.filter_by(email=email).first()

        if token_registro_existente:
            # Verificar se o último token enviado foi há mais de 3 minutos
            time_difference = datetime.utcnow() - token_registro_existente.timestamp
            time_difference_seconds = time_difference.total_seconds()

            if time_difference_seconds <= timedelta(minutes=3).total_seconds():
                tempo_restante = int(timedelta(minutes=3).total_seconds() - time_difference_seconds)
                return jsonify({'mensagem': f'O seu token foi enviado há 3 minutos ou menos, portanto ainda está válido. Clique no link dele ou aguarde os 3 minutos'}), 401
            else:
                # Reenviar um novo token
                token_result = gerar_e_enviar_token(email)
                if "Link de verificação enviado com sucesso" in token_result.get_json()['mensagem']:
                    return token_result
                return jsonify({'mensagem': 'E-mail não verificado. Um novo token foi enviado para ativação'}), 401

        else:
            # Gerar um novo token
            expiration_time = datetime.utcnow() + timedelta(minutes=3)
            token = serializer.dumps({'email': email, 'exp': expiration_time.isoformat()})
            token_registro_existente = TokenVerificacaoEmail(token=token, email=email)

            # Criar o link com o token
            token_link = f"{BASE_URL}/verificar_email/{token}"

            # Enviar e-mail com o token
            enviar_email_dinamico(email, 'Token de Verificação', token_link, 'enviartoken.html')

            # Adicionar o novo token ao banco de dados
            db.session.add(token_registro_existente)
            db.session.commit()

            # Exibir a mensagem indicando que um novo token foi enviado
            return jsonify({'mensagem': 'E-mail não verificado. Um novo token foi enviado para ativação'}), 401

    except Exception as e:
        print(f"Erro ao enviar/reenviar e-mail: {e}")
        return jsonify({'mensagem': 'Algo deu errado ao enviar/reenviar o token de verificação por e-mail'}), 500


@app.route('/verificar_email/<token>')
def verificar_email(token):
    try:
        # Deserializar o token
        data = serializer.loads(token, max_age=600)  # 600 segundos = 10 minutos

        # Verificar se o token está na tabela de tokens de verificação
        token_registro = TokenVerificacaoEmail.query.filter_by(token=token, email=data['email']).first()
        if not token_registro:
            return jsonify({'mensagem': 'Token inválido ou expirado'})

        # Atualizar o status de e-mail verificado no autor associado
        autor = Autor.query.filter_by(email=data['email']).first()
        if autor:
            autor.email_verificado = True
            db.session.delete(token_registro)
            db.session.commit()

            return jsonify({'mensagem': f'E-mail {data["email"]} verificado com sucesso!'})
        else:
            return jsonify({'mensagem': 'Erro interno. Autor não encontrado.'}), 500
    except Exception as e:
        print(f"Erro na verificação do e-mail: {e}")
        return jsonify({'mensagem': 'Erro na verificação do e-mail. O link pode ter expirado ou ser inválido.'}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})

        usuario = Autor.query.filter_by(email=auth.username).first()

        if not usuario:
            return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})

        # Verificar se o e-mail não está verificado e reenviar token
        if not usuario.email_verificado:
            # Verificar se já existe um token para o e-mail na tabela
            token_registro_existente = TokenVerificacaoEmail.query.filter_by(email=usuario.email).first()

            if token_registro_existente:
                # Verificar se o último token enviado foi há mais de 3 minutos
                time_difference = datetime.utcnow() - token_registro_existente.timestamp
                time_difference_seconds = time_difference.total_seconds()

                if time_difference_seconds <= timedelta(minutes=3).total_seconds():
                    tempo_restante = int(timedelta(minutes=3).total_seconds() - time_difference_seconds)
                    return make_response(f'O seu token foi enviado há 3 minutos ou menos, portanto ainda está válido. Clique no link dele ou aguarde os 3 minutos. Tempo restante: {tempo_restante} segundos', 401)

            # Se não passou 3 minutos, reenvie um novo token
            gerar_e_enviar_token(usuario.email)
            return make_response('E-mail não verificado. Um novo token foi enviado para ativação', 401)

        if bcrypt.check_password_hash(usuario.senha, auth.password):
            print("Senha válida!")
            token = jwt.encode({'id_autor': usuario.id_autor, 'exp': (datetime.utcnow() + timedelta(minutes=10)).timestamp()},
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
        else:
            print("Senha incorreta!")
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
