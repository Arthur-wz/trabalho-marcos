import math
import psycopg

from flask import Blueprint, jsonify, request

from database.conexao import obter_conexao
from services.turnos import alternar_turno
from services.tempo import atualizar_estado_partida


partidas_bp = Blueprint("partidas", __name__)


# FUNÇÕES AUXILIARES DO BANCO

def buscar_partida(conn, partida_id, bloquear=False):

    consulta = """
        SELECT *
        FROM public.partidas
        WHERE id = %s
    """

    if bloquear:
        consulta += " FOR UPDATE"

    return conn.execute(
        consulta,
        (partida_id,)
    ).fetchone()


def converter_partida(registro):

    inicio = registro["inicio"]

    partida = {
        "id": registro["id"],
        "jogador1": registro["jogador1_id"],
        "jogador2": registro["jogador2_id"],
        "gols_jogador1": registro["gols_jogador1"],
        "gols_jogador2": registro["gols_jogador2"],
        "botoes_por_time": registro["botoes_por_time"],
        "duracao_segundos": registro["duracao_segundos"],
        "turno_atual": registro["turno_atual"],
        "status": registro["status"],
        "inicio": inicio.isoformat()
    }

    if registro["vencedor_id"] is not None:
        partida["vencedor_id"] = registro["vencedor_id"]

    if registro["resultado"] is not None:
        partida["resultado"] = registro["resultado"]

    return partida


def atualizar_tempo_no_banco(conn, registro):

    partida = converter_partida(registro)

    status_anterior = partida["status"]

    tempo_restante = atualizar_estado_partida(partida)

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

    return partida, tempo_restante


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

    with obter_conexao() as conn:

        # Procura os jogadores cadastrados
        jogadores = conn.execute(
            """
            SELECT id
            FROM public.jogadores
            WHERE id IN (%s, %s)
            """,
            (jogador1_id, jogador2_id)
        ).fetchall()

        if len(jogadores) != 2:
            return jsonify({
                "sucesso": False,
                "mensagem": "Um ou ambos os jogadores não existem."
            }), 404

        # Cria a partida no PostgreSQL
        registro = conn.execute(
            """
            INSERT INTO public.partidas (
                jogador1_id,
                jogador2_id,
                gols_jogador1,
                gols_jogador2,
                botoes_por_time,
                duracao_segundos,
                turno_atual,
                status
            )
            VALUES (%s, %s, 0, 0, 5, 300, %s, 'em_andamento')
            RETURNING *
            """,
            (jogador1_id, jogador2_id, jogador1_id)
        ).fetchone()

        nova_partida = converter_partida(registro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Partida criada com sucesso!",
        "partida": nova_partida
    }), 201


# CONSULTAR PARTIDA

@partidas_bp.route("/api/partidas/<int:partida_id>", methods=["GET"])
def consultar_partida(partida_id):

    with obter_conexao() as conn:

        registro = buscar_partida(
            conn,
            partida_id,
            bloquear=True
        )

        if registro is None:
            return jsonify({
                "sucesso": False,
                "mensagem": "Partida não encontrada."
            }), 404

        partida, tempo_restante = atualizar_tempo_no_banco(
            conn,
            registro
        )

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

    with obter_conexao() as conn:

        # Procura a partida
        registro = buscar_partida(
            conn,
            partida_id,
            bloquear=True
        )

        if registro is None:
            return jsonify({
                "sucesso": False,
                "mensagem": "Partida não encontrada."
            }), 404

        partida, tempo_restante = atualizar_tempo_no_banco(
            conn,
            registro
        )

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
        if jogador_id not in [
            partida["jogador1"],
            partida["jogador2"]
        ]:
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

        if not (
            -1 <= direcao_x <= 1
            and -1 <= direcao_y <= 1
        ):
            return jsonify({
                "sucesso": False,
                "mensagem": "Direção fora dos limites permitidos."
            }), 400

        if math.hypot(direcao_x, direcao_y) == 0:
            return jsonify({
                "sucesso": False,
                "mensagem": "A direção não pode ser zero."
            }), 400

        # Calcula o número da próxima jogada
        resultado = conn.execute(
            """
            SELECT COALESCE(MAX(numero), 0) + 1 AS numero
            FROM public.jogadas
            WHERE partida_id = %s
            """,
            (partida_id,)
        ).fetchone()

        numero = resultado["numero"]

        jogada = {
            "numero": numero,
            "jogador_id": jogador_id,
            "botao_id": botao_id,
            "forca": forca,
            "direcao_x": direcao_x,
            "direcao_y": direcao_y
        }

        # Salva a jogada no PostgreSQL
        conn.execute(
            """
            INSERT INTO public.jogadas (
                partida_id,
                jogador_id,
                numero,
                botao_id,
                forca,
                direcao_x,
                direcao_y
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                partida_id,
                jogador_id,
                numero,
                botao_id,
                forca,
                direcao_x,
                direcao_y
            )
        )

        # Passa a vez para o outro jogador
        proximo_jogador = alternar_turno(partida)

        conn.execute(
            """
            UPDATE public.partidas
            SET turno_atual = %s
            WHERE id = %s
            """,
            (proximo_jogador, partida_id)
        )

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

    try:
        with obter_conexao() as conn:

            # Procura a partida
            registro = buscar_partida(
                conn,
                partida_id,
                bloquear=True
            )

            if registro is None:
                return jsonify({
                    "sucesso": False,
                    "mensagem": "Partida não encontrada."
                }), 404

            # Atualiza e verifica o tempo da partida
            partida, tempo_restante = atualizar_tempo_no_banco(
                conn,
                registro
            )

            if partida["status"] != "em_andamento":
                return jsonify({
                    "sucesso": False,
                    "mensagem": "A partida já foi encerrada."
                }), 400

            # Verifica se o jogador participa da partida
            if jogador_id not in [
                partida["jogador1"],
                partida["jogador2"]
            ]:
                return jsonify({
                    "sucesso": False,
                    "mensagem": "Esse jogador não participa da partida."
                }), 403

            # Registra o gol no histórico
            # A restrição UNIQUE impede eventos duplicados
            conn.execute(
                """
                INSERT INTO public.gols (
                    partida_id,
                    jogador_id,
                    evento_id
                )
                VALUES (%s, %s, %s)
                """,
                (partida_id, jogador_id, evento_id)
            )

            # Atualiza o placar
            if jogador_id == partida["jogador1"]:

                partida["gols_jogador1"] += 1

                conn.execute(
                    """
                    UPDATE public.partidas
                    SET gols_jogador1 = gols_jogador1 + 1
                    WHERE id = %s
                    """,
                    (partida_id,)
                )

            else:

                partida["gols_jogador2"] += 1

                conn.execute(
                    """
                    UPDATE public.partidas
                    SET gols_jogador2 = gols_jogador2 + 1
                    WHERE id = %s
                    """,
                    (partida_id,)
                )

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "sucesso": False,
            "mensagem": "Esse gol já foi registrado."
        }), 409

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

    with obter_conexao() as conn:

        # Verifica se a partida existe
        registro = buscar_partida(conn, partida_id)

        if registro is None:
            return jsonify({
                "sucesso": False,
                "mensagem": "Partida não encontrada."
            }), 404

        # Busca todos os gols dessa partida
        registros = conn.execute(
            """
            SELECT
                id,
                partida_id,
                jogador_id,
                evento_id,
                data
            FROM public.gols
            WHERE partida_id = %s
            ORDER BY id
            """,
            (partida_id,)
        ).fetchall()

        gols_partida = []

        for gol in registros:
            gols_partida.append({
                "id": gol["id"],
                "partida_id": gol["partida_id"],
                "jogador_id": gol["jogador_id"],
                "evento_id": gol["evento_id"],
                "data": gol["data"].isoformat()
            })

    return jsonify({
        "sucesso": True,
        "total_gols": len(gols_partida),
        "gols": gols_partida
    }), 200