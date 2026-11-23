from datetime import datetime, timezone, timedelta


def calcular_tempo_restante(partida):
    """
    Calcula quantos segundos ainda restam na partida.
    """

    inicio = datetime.fromisoformat(partida["inicio"])
    agora = datetime.now(timezone.utc)

    tempo_decorrido = int((agora - inicio).total_seconds())
    tempo_decorrido = max(0, tempo_decorrido)

    tempo_restante = partida["duracao_segundos"] - tempo_decorrido

    return max(0, tempo_restante)


def atualizar_estado_partida(partida):
    """
    Verifica se o tempo acabou e encerra a partida.
    """

    tempo_restante = calcular_tempo_restante(partida)

    if tempo_restante == 0 and partida["status"] == "em_andamento":

        partida["status"] = "encerrada"

        gols1 = partida["gols_jogador1"]
        gols2 = partida["gols_jogador2"]

        if gols1 > gols2:
            partida["vencedor_id"] = partida["jogador1"]
            partida["resultado"] = "jogador1_venceu"

        elif gols2 > gols1:
            partida["vencedor_id"] = partida["jogador2"]
            partida["resultado"] = "jogador2_venceu"

        else:
            partida["vencedor_id"] = None
            partida["resultado"] = "empate"

    return tempo_restante
