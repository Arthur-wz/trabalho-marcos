from services.tempo import atualizar_estado_partida
from flask import Blueprint, jsonify
from database.conexao import obter_conexao

rankings_bp = Blueprint("rankings", __name__)


# RANKING DE ARTILHEIROS
@rankings_bp.route("/api/rankings/artilheiros", methods=["GET"])
def ranking_artilheiros():

    # Busca os jogadores e conta os gols registrados no PostgreSQL
    with obter_conexao() as conn:

        registros = conn.execute(
            """
            SELECT
                j.id AS jogador_id,
                j.nome,
                COUNT(g.id) AS gols
            FROM public.jogadores j
            LEFT JOIN public.gols g
                ON g.jogador_id = j.id
            GROUP BY j.id, j.nome
            ORDER BY COUNT(g.id) DESC, LOWER(j.nome)
            """
        ).fetchall()

    # Monta a lista do ranking
    ranking = []

    for registro in registros:
        ranking.append({
            "jogador_id": registro["jogador_id"],
            "nome": registro["nome"],
            "gols": registro["gols"]
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

    with obter_conexao() as conn:

        # Busca os jogadores cadastrados
        jogadores = conn.execute(
            """
            SELECT id, nome
            FROM public.jogadores
            """
        ).fetchall()

        # Busca todas as partidas
        partidas = conn.execute(
            """
            SELECT
                id,
                jogador1_id,
                jogador2_id,
                gols_jogador1,
                gols_jogador2,
                duracao_segundos,
                inicio,
                status,
                vencedor_id,
                resultado
            FROM public.partidas
            """
        ).fetchall()

        # Cria as estatísticas iniciais de cada jogador
        estatisticas = {}

        for jogador in jogadores:
            estatisticas[jogador["id"]] = {
                "jogador_id": jogador["id"],
                "nome": jogador["nome"],
                "vitorias": 0,
                "derrotas": 0,
                "empates": 0,
                "partidas": 0
            }

        # Analisa as partidas
        for registro in partidas:

            partida = {
                "id": registro["id"],
                "jogador1": registro["jogador1_id"],
                "jogador2": registro["jogador2_id"],
                "gols_jogador1": registro["gols_jogador1"],
                "gols_jogador2": registro["gols_jogador2"],
                "duracao_segundos": registro["duracao_segundos"],
                "inicio": registro["inicio"].isoformat(),
                "status": registro["status"],
                "vencedor_id": registro["vencedor_id"],
                "resultado": registro["resultado"]
            }

            # Atualiza o estado da partida caso o tempo tenha acabado
            status_anterior = partida["status"]

            atualizar_estado_partida(partida)

            # Salva o encerramento no PostgreSQL
            if partida["status"] != status_anterior:
                conn.execute(
                    """
                    UPDATE public.partidas
                    SET status = %s,
                        vencedor_id = %s,
                        resultado = %s
                    WHERE id = %s
                    """,
                    (
                        partida["status"],
                        partida.get("vencedor_id"),
                        partida.get("resultado"),
                        partida["id"]
                    )
                )

            # Analisa somente partidas encerradas
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