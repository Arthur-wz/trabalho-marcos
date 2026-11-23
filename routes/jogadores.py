
from flask import Blueprint, jsonify, request
from database import memoria

jogadores_bp = Blueprint("jogadores", __name__)


# CADASTRAR JOGADOR
@jogadores_bp.route("/api/jogadores", methods=["POST"])
def cadastrar_jogador():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie os dados em formato JSON."
        }), 400

    nome = dados.get("nome")
    usuario = dados.get("usuario")

    if not isinstance(nome, str) or not isinstance(usuario, str):
        return jsonify({
            "sucesso": False,
            "mensagem": "Nome e usuário são obrigatórios."
        }), 400

    nome = nome.strip()
    usuario = usuario.strip()

    if not nome or not usuario:
        return jsonify({
            "sucesso": False,
            "mensagem": "Os campos não podem estar vazios."
        }), 400

    if len(nome) > 80 or len(usuario) > 30:
        return jsonify({
            "sucesso": False,
            "mensagem": "Nome ou usuário muito longo."
        }), 400

    for jogador in memoria.jogadores:
        if jogador["usuario"].lower() == usuario.lower():
            return jsonify({
                "sucesso": False,
                "mensagem": "Esse nome de usuário já existe."
            }), 409

    novo_jogador = {
        "id": memoria.proximo_jogador_id,
        "nome": nome,
        "usuario": usuario
    }

    memoria.jogadores.append(novo_jogador)
    memoria.proximo_jogador_id += 1

    return jsonify({
        "sucesso": True,
        "mensagem": "Jogador cadastrado com sucesso!",
        "jogador": novo_jogador
    }), 201


# LISTAR JOGADORES
@jogadores_bp.route("/api/jogadores", methods=["GET"])
def listar_jogadores():
    return jsonify({
        "sucesso": True,
        "jogadores": memoria.jogadores
    }), 200
