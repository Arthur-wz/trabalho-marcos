
def alternar_turno(partida):
    """
    Recebe uma partida e altera o jogador da vez.
    """

    if partida["turno_atual"] == partida["jogador1"]:
        partida["turno_atual"] = partida["jogador2"]

    else:
        partida["turno_atual"] = partida["jogador1"]

    return partida["turno_atual"]
