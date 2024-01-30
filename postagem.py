from flask import jsonify, request
from bancoconfig import Postagem, db
from login import *

@app.route('/postagens')
@token_obrigatorio
def obter_postagem(autor):
    try:
        postagens = Postagem.query.all()
        listapostagem = []
        for postagem in postagens:
            postagem_atual = {}
            postagem_atual['id_postagem'] = postagem.id_postagem
            postagem_atual['autor_nome'] = postagem.autor_nome
            postagem_atual['titulo'] = postagem.titulo
            postagem_atual['descricao'] = postagem.descricao
            listapostagem.append(postagem_atual)
        return jsonify(listapostagem)
    except:
        return jsonify({'mensagem': 'Algum erro ao exibir postagem'})


@app.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_id(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem:
        return jsonify(f'Não tem essa postagem não pow,vai com calma ai')
    postagem_escolhida = {}
    postagem_escolhida['id_postagem'] = postagem.id_postagem
    postagem_escolhida['autor_nome'] = postagem.autor_nome
    postagem_escolhida['titulo'] = postagem.titulo
    postagem_escolhida['descricao'] = postagem.descricao

    return jsonify(postagem_escolhida)


@app.route('/postagens', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    try:
        nova_postagem = request.get_json()
        autor_nome = autor.nome  # Extrai o nome do autor do objeto autor obtido pelo token
        postagem = Postagem(autor_nome=autor_nome, titulo=nova_postagem['titulo'], descricao=nova_postagem['descricao'])
        db.session.add(postagem)
        db.session.commit()
        return jsonify({'mensagem': 'Postagem adicionada com sucesso'})
    except Exception as e:
        print(e)
        return jsonify({'mensagem': 'Algo deu errado, confere essa porra de documentação direito front-end'}), 500


@app.route('/postagens/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    try:
        postagem_alterar = request.get_json()
        postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

        if not postagem:
            return jsonify({'mensagem': 'Postagem não encontrada'})

        if postagem.autor_nome != autor.nome:
            return jsonify({'mensagem': 'Você não tem permissão para alterar esta postagem'})

        try:
            if 'autor_nome' in postagem_alterar:
                postagem.autor_nome = postagem_alterar['autor_nome']
        except KeyError:
            pass

        try:
            if 'titulo' in postagem_alterar:
                postagem.titulo = postagem_alterar['titulo']
        except KeyError:
            pass

        try:
            if 'descricao' in postagem_alterar:
                postagem.descricao = postagem_alterar['descricao']
        except KeyError:
            pass

        db.session.commit()
        return jsonify({'mensagem': 'Postagem alterada com sucesso'})

    except Exception as e:
        print(f"Erro durante a alteração da postagem: {e}")
        return jsonify({'mensagem': 'Postagem não alterada, ocorreu algum erro'})


@app.route('/postagens/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

    if not postagem:
        return jsonify({'mensagem': 'Postagem não encontrada'})

    if postagem.autor_nome != autor.nome:
        return jsonify({'mensagem': 'Você não tem permissão para alterar esta postagem'})

    postagem_info = {
        'id_postagem': postagem.id_postagem,
        'autor_nome': postagem.autor_nome,
        'titulo': postagem.titulo,
        'descricao': postagem.descricao
    }

    db.session.delete(postagem)
    db.session.commit()

    return jsonify({'postagem_excluida': postagem_info, 'mensagem': 'Postagem excluída com sucesso'})
