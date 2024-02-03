from flask import jsonify, request
from bancoconfig import Autor, db, bcrypt, app
from login import *
from configemail import *

@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    listadeautores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        listadeautores.append(autor_atual)
    return jsonify(listadeautores)  # assim só retorna o jsons, bem mais fácil de tratar


@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify(f'Autor não encontrado')
    autor_escolhido = {}
    autor_escolhido['id_autor'] = autor.id_autor
    autor_escolhido['nome'] = autor.nome
    autor_escolhido['email'] = autor.email
    return jsonify(autor_escolhido)


@app.route('/autores', methods=['POST'])
def novo_autor():
    try:
        novo_autor = request.get_json()
        email = novo_autor['email']
        # Verificar se o e-mail já está cadastrado
        autor_existente = Autor.query.filter_by(email=email).first()
        if autor_existente:
            return jsonify({'mensagem': 'E-mail já cadastrado'}), 400
        senha_criptografada = bcrypt.generate_password_hash(novo_autor['senha']).decode('utf-8')
        autor = Autor(nome=novo_autor['nome'], email=email, senha=senha_criptografada, admin=True)
        gerar_e_enviar_token(email)
        db.session.add(autor)
        db.session.commit()
        return jsonify({'mensagem': 'Novo autor cadastrado com sucesso. Verifique seu e-mail para ativar a conta'})
    except Exception as e:
        print(e)
        return jsonify({'mensagem': 'Algo deu errado.'}), 500



@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    try:
        usuario_alterar = request.get_json()
        autor = Autor.query.filter_by(id_autor=id_autor).first()

        if not autor:
            return jsonify({'mensagem': 'Autor não encontrado'})

        try:
            if 'nome' in usuario_alterar:
                autor.nome = usuario_alterar['nome']
        except KeyError:
            pass

        try:
            if 'email' in usuario_alterar:
                autor.email = usuario_alterar['email']
        except KeyError:
            pass

        try:
            if 'admin' in usuario_alterar:
                if usuario_alterar['admin'] == "False":  # solução para colocar o negocio como falso
                    autor.admin = False
                else:
                    autor.admin = True
        except KeyError:
            pass
        try:
            if 'senha' in usuario_alterar:
                senha_criptografada = bcrypt.generate_password_hash(usuario_alterar['senha']).decode('utf-8')
                autor.senha = senha_criptografada
        except KeyError:
            pass

        db.session.commit()
        return jsonify({'mensagem': 'Autor alterado com sucesso'})

    except Exception as e:
        print(f"Erro durante a alteração do autor: {e}")
        return jsonify({'mensagem': 'Autor não alterado, ocorreu algum erro'})


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    autorexcluido = []
    if not autor:
        return jsonify({'mensagem': 'Não tem esse autor'})
    autor_info = {
        'id_autor': autor.id_autor,
        'nome': autor.nome,
        'email': autor.email

    }
    autorexcluido.append(autor_info)
    db.session.delete(autor)
    db.session.commit()
    return jsonify({'autor excluido': autorexcluido})