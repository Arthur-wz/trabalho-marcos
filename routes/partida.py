
from flask import Blueprint, jsonify, request
from database import memoria
from datetime import datetime, timezone

partidas_bp = Blueprint("partidas", __name__)


# CRIAR PARTIDA
@partidas_bp.route("/api/partidas", methods=["POST"])
def criar_partida():

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie os dados em formato JSON."
        }), 400

    jogador1_id = dados.get("jogador1_id")
    jogador2_id = dados.get("jogador2_id")

    # Verifica se os IDs são números inteiros
    if (type(jogador1_id) is not int or
            type(jogador2_id) is not int):

        return jsonify({
            "sucesso": False,
            "mensagem": "Informe IDs válidos para os jogadores."
        }), 400

    # Impede que um jogador jogue contra si mesmo
    if jogador1_id == jogador2_id:
        return jsonify({
            "sucesso": False,
            "mensagem": "Uma partida precisa de dois jogadores diferentes."
        }), 400

    # Procura os jogadores cadastrados
    jogador1 = next(
        (j for j in memoria.jogadores
         if j["id"] == jogador1_id), None
    )

    jogador2 = next(
        (j for j in memoria.jogadores
         if j["id"] == jogador2_id), None
    )

    if jogador1 is None or jogador2 is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Um ou ambos os jogadores não existem."
        }), 404

    # Cria a partida
    nova_partida = {
        "id": memoria.proxima_partida_id,

        "jogador1": jogador1_id,
        "jogador2": jogador2_id,

        "gols_jogador1": 0,
        "gols_jogador2": 0,

        "botoes_por_time": 5,
        "duracao_segundos": 300,

        "turno_atual": jogador1_id,

        "status": "em_andamento",

        "inicio": datetime.now(timezone.utc).isoformat()
    }

    memoria.partidas.append(nova_partida)
    memoria.proxima_partida_id += 1

    return jsonify({
        "sucesso": True,
        "mensagem": "Partida criada com sucesso!",
        "partida": nova_partida
    }), 201


# CONSULTAR PARTIDA
@partidas_bp.route("/api/partidas/<int:partida_id>", methods=["GET"])
def consultar_partida(partida_id):

    partida = next(
        (p for p in memoria.partidas
         if p["id"] == partida_id), None
    )

    if partida is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Partida não encontrada."
        }), 404

    return jsonify({
        "sucesso": True,
        "partida": partida
    }), 200
