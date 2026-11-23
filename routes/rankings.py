from services.tempo import atualizar_estado_partida
from flask import Blueprint, jsonify
from database import memoria

rankings_bp = Blueprint("rankings", __name__)


# RANKING DE ARTILHEIROS
@rankings_bp.route("/api/rankings/artilheiros", methods=["GET"])
def ranking_artilheiros():

    # Cria uma contagem inicial de gols para cada jogador
    gols_por_jogador = {
        jogador["id"]: 0
        for jogador in memoria.jogadores
    }

    # Conta os gols registrados
    for gol in memoria.gols:
        jogador_id = gol["jogador_id"]

        if jogador_id in gols_por_jogador:
            gols_por_jogador[jogador_id] += 1

    # Monta a lista do ranking
    ranking = []

    for jogador in memoria.jogadores:
        ranking.append({
            "jogador_id": jogador["id"],
            "nome": jogador["nome"],
            "gols": gols_por_jogador[jogador["id"]]
        })

    # Ordena do maior número de gols para o menor
    ranking.sort(
        key=lambda jogador: (-jogador["gols"], jogador["nome"].lower())
    )

    # Define a posição dos jogadores
    posicao_anterior = None

    for indice, jogador in enumerate(ranking):
        if jogador["gols"] != posicao_anterior:
            posicao = indice + 1
            posicao_anterior = jogador["gols"]

        jogador["posicao"] = posicao

    return jsonify({
        "sucesso": True,
        "total_jogadores": len(ranking),
        "ranking": ranking
    }), 200


# RANKING DE VITÓRIAS
@rankings_bp.route("/api/rankings/vitorias", methods=["GET"])
def ranking_vitorias():

    # Atualiza o estado de todas as partidas
    for partida in memoria.partidas:
        atualizar_estado_partida(partida)

    # Cria as estatísticas iniciais de cada jogador
    estatisticas = {}

    for jogador in memoria.jogadores:
        estatisticas[jogador["id"]] = {
            "jogador_id": jogador["id"],
            "nome": jogador["nome"],
            "vitorias": 0,
            "derrotas": 0,
            "empates": 0,
            "partidas": 0
        }

    # Analisa somente partidas encerradas
    for partida in memoria.partidas:

        if partida["status"] != "encerrada":
            continue

        jogador1 = partida["jogador1"]
        jogador2 = partida["jogador2"]
        vencedor = partida.get("vencedor_id")

        # Ignora partidas cujos jogadores não estejam cadastrados
        if jogador1 not in estatisticas or jogador2 not in estatisticas:
            continue

        estatisticas[jogador1]["partidas"] += 1
        estatisticas[jogador2]["partidas"] += 1

        # Registra o empate
        if vencedor is None:
            estatisticas[jogador1]["empates"] += 1
            estatisticas[jogador2]["empates"] += 1

        # Registra a vitória e a derrota
        elif vencedor == jogador1:
            estatisticas[jogador1]["vitorias"] += 1
            estatisticas[jogador2]["derrotas"] += 1

        elif vencedor == jogador2:
            estatisticas[jogador2]["vitorias"] += 1
            estatisticas[jogador1]["derrotas"] += 1

    # Transforma o dicionário em lista
    ranking = list(estatisticas.values())

    # Ordena por vitórias, empates e menos derrotas
    ranking.sort(
        key=lambda jogador: (
            -jogador["vitorias"],
            -jogador["empates"],
            jogador["derrotas"],
            jogador["nome"].lower()
        )
    )

    # Define as posições
    posicao_anterior = None

    for indice, jogador in enumerate(ranking):
        criterio = (
            jogador["vitorias"],
            jogador["empates"],
            jogador["derrotas"]
        )

        if criterio != posicao_anterior:
            posicao = indice + 1
            posicao_anterior = criterio

        jogador["posicao"] = posicao

    return jsonify({
        "sucesso": True,
        "total_jogadores": len(ranking),
        "ranking": ranking
    }), 200
