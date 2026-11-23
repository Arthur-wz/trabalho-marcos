
from flask import Blueprint, jsonify, request
from database import memoria
from datetime import datetime, timezone
from services.turnos import alternar_turno
import math
from services.tempo import atualizar_estado_partida

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

    tempo_restante = atualizar_estado_partida(partida)

    return jsonify({
    "sucesso": True,
    "partida": partida,
    "tempo_restante": tempo_restante
}), 200


# REGISTRAR JOGADA
@partidas_bp.route(
    "/api/partidas/<int:partida_id>/jogadas",
    methods=["POST"]
)
def registrar_jogada(partida_id):

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie os dados em formato JSON."
        }), 400

    # Procura a partida
    partida = next(
        (p for p in memoria.partidas if p["id"] == partida_id),
        None
    )

    if partida is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Partida não encontrada."
        }), 404

    atualizar_estado_partida(partida)
    if partida["status"] != "em_andamento":
        return jsonify({
            "sucesso": False,
            "mensagem": "Essa partida não está em andamento."
        }), 400

    jogador_id = dados.get("jogador_id")
    botao_id = dados.get("botao_id")
    forca = dados.get("forca")
    direcao_x = dados.get("direcao_x")
    direcao_y = dados.get("direcao_y")

    # Valida os IDs
    if type(jogador_id) is not int or type(botao_id) is not int:
        return jsonify({
            "sucesso": False,
            "mensagem": "IDs inválidos."
        }), 400

    # Verifica se o jogador participa da partida
    if jogador_id not in [partida["jogador1"], partida["jogador2"]]:
        return jsonify({
            "sucesso": False,
            "mensagem": "Jogador não participa dessa partida."
        }), 403

    # Verifica o turno
    if jogador_id != partida["turno_atual"]:
        return jsonify({
            "sucesso": False,
            "mensagem": "Não é sua vez de jogar."
        }), 403

    # Verifica o botão
    if not 1 <= botao_id <= partida["botoes_por_time"]:
        return jsonify({
            "sucesso": False,
            "mensagem": "Botão inválido."
        }), 400

    # Verifica a força
    if (
        type(forca) not in (int, float)
        or not math.isfinite(forca)
        or not 1 <= forca <= 100
    ):
        return jsonify({
            "sucesso": False,
            "mensagem": "A força deve estar entre 1 e 100."
        }), 400

    # Verifica a direção
    if (
        type(direcao_x) not in (int, float)
        or type(direcao_y) not in (int, float)
        or not math.isfinite(direcao_x)
        or not math.isfinite(direcao_y)
    ):
        return jsonify({
            "sucesso": False,
            "mensagem": "Direção inválida."
        }), 400

    if not (-1 <= direcao_x <= 1 and -1 <= direcao_y <= 1):
        return jsonify({
            "sucesso": False,
            "mensagem": "Direção fora dos limites permitidos."
        }), 400

    if math.hypot(direcao_x, direcao_y) == 0:
        return jsonify({
            "sucesso": False,
            "mensagem": "A direção não pode ser zero."
        }), 400

    # Registra a jogada
    if "jogadas" not in partida:
        partida["jogadas"] = []

    jogada = {
        "numero": len(partida["jogadas"]) + 1,
        "jogador_id": jogador_id,
        "botao_id": botao_id,
        "forca": forca,
        "direcao_x": direcao_x,
        "direcao_y": direcao_y
    }

    partida["jogadas"].append(jogada)

    # Passa a vez para o outro jogador
    proximo_jogador = alternar_turno(partida)

    return jsonify({
        "sucesso": True,
        "mensagem": "Jogada registrada com sucesso!",
        "jogada": jogada,
        "proximo_jogador": proximo_jogador
    }), 201



# REGISTRAR GOL
@partidas_bp.route(
    "/api/partidas/<int:partida_id>/gols",
    methods=["POST"]
)
def registrar_gol(partida_id):

    dados = request.get_json(silent=True)

    # Verifica se recebeu um JSON válido
    if not isinstance(dados, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie os dados em formato JSON."
        }), 400

    jogador_id = dados.get("jogador_id")
    evento_id = dados.get("evento_id")

    # Valida o ID do jogador
    if type(jogador_id) is not int:
        return jsonify({
            "sucesso": False,
            "mensagem": "Informe um ID de jogador válido."
        }), 400

    # Valida o identificador único do gol
    if not isinstance(evento_id, str):
        return jsonify({
            "sucesso": False,
            "mensagem": "Informe o identificador do evento."
        }), 400

    evento_id = evento_id.strip()

    if not evento_id or len(evento_id) > 100:
        return jsonify({
            "sucesso": False,
            "mensagem": "Identificador do evento inválido."
        }), 400

    # Procura a partida
    partida = next(
        (p for p in memoria.partidas if p["id"] == partida_id),
        None
    )

    if partida is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Partida não encontrada."
        }), 404

    # Atualiza e verifica o tempo da partida
    atualizar_estado_partida(partida)

    if partida["status"] != "em_andamento":
        return jsonify({
            "sucesso": False,
            "mensagem": "A partida já foi encerrada."
        }), 400

    # Verifica se o jogador participa da partida
    if jogador_id not in [partida["jogador1"], partida["jogador2"]]:
        return jsonify({
            "sucesso": False,
            "mensagem": "Esse jogador não participa da partida."
        }), 403

    # Verifica se esse evento já foi registrado
    gol_existente = next(
        (
            gol for gol in memoria.gols
            if gol["partida_id"] == partida_id
            and gol.get("evento_id") == evento_id
        ),
        None
    )

    if gol_existente is not None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Esse gol já foi registrado."
        }), 409

    # Atualiza o placar
    if jogador_id == partida["jogador1"]:
        partida["gols_jogador1"] += 1
    else:
        partida["gols_jogador2"] += 1

    # Registra o gol no histórico
    novo_gol = {
        "id": memoria.proximo_gol_id,
        "partida_id": partida_id,
        "jogador_id": jogador_id,
        "evento_id": evento_id,
        "data": datetime.now(timezone.utc).isoformat()
    }

    memoria.gols.append(novo_gol)
    memoria.proximo_gol_id += 1

    return jsonify({
        "sucesso": True,
        "mensagem": "Gol registrado com sucesso!",
        "partida": partida
    }), 200

# HISTÓRICO DE GOLS DA PARTIDA
@partidas_bp.route(
    "/api/partidas/<int:partida_id>/historico-gols",
    methods=["GET"]
)
def listar_gols(partida_id):

    # Verifica se a partida existe
    partida = next(
        (p for p in memoria.partidas if p["id"] == partida_id),
        None
    )

    if partida is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Partida não encontrada."
        }), 404

    # Busca todos os gols dessa partida
    gols_partida = [
        gol for gol in memoria.gols
        if gol["partida_id"] == partida_id
    ]

    return jsonify({
        "sucesso": True,
        "total_gols": len(gols_partida),
        "gols": gols_partida
    }), 200
