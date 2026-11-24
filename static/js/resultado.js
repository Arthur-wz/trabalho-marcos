/* =========================================================
   STADIUM DO COFFEE — RESULTADO.JS
   Consulta o resultado da partida e o histórico de gols.
   API documentada no Back-End do projeto.
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    const API = window.location.origin;

    const elementos = {
        nome1: document.getElementById("nomeJogador1"),
        nome2: document.getElementById("nomeJogador2"),
        gols1: document.getElementById("golsJogador1"),
        gols2: document.getElementById("golsJogador2"),
        mensagem: document.getElementById("mensagemResultado"),
        status: document.getElementById("statusPartida"),
        historico: document.getElementById("historicoGols"),
        vencedor: document.getElementById("vencedorPartida"),
        botaoNovoJogo: document.getElementById("botaoNovoJogo"),
        botaoVoltar: document.getElementById("botaoVoltar")
    };

    function obterIdPartida() {
        const parametros = new URLSearchParams(window.location.search);

        return (
            parametros.get("partida_id") ||
            parametros.get("id") ||
            sessionStorage.getItem("partidaId") ||
            localStorage.getItem("partidaId")
        );
    }

    function mostrarMensagem(texto, erro = false) {
        if (!elementos.mensagem) return;

        elementos.mensagem.textContent = texto;
        elementos.mensagem.classList.toggle("erro", erro);
    }

    function definirTexto(elemento, valor) {
        if (elemento) elemento.textContent = valor;
    }

    async function requisicao(url) {
        const resposta = await fetch(`${API}${url}`);

        let dados;
        try {
            dados = await resposta.json();
        } catch {
            throw new Error("O servidor retornou uma resposta inválida.");
        }

        if (!resposta.ok || dados.sucesso === false) {
            throw new Error(
                dados.mensagem || `Erro na comunicação com o servidor (${resposta.status}).`
            );
        }

        return dados;
    }

    async function carregarNomes(partida) {
        try {
            const dados = await requisicao("/api/jogadores");
            const jogadores = dados.jogadores || [];

            const jogador1 = jogadores.find(
                jogador => Number(jogador.id) === Number(partida.jogador1)
            );

            const jogador2 = jogadores.find(
                jogador => Number(jogador.id) === Number(partida.jogador2)
            );

            definirTexto(elementos.nome1, jogador1?.nome || "Jogador 1");
            definirTexto(elementos.nome2, jogador2?.nome || "Jogador 2");
        } catch (erro) {
            console.warn("Não foi possível carregar os nomes dos jogadores:", erro);
            definirTexto(elementos.nome1, "Jogador 1");
            definirTexto(elementos.nome2, "Jogador 2");
        }
    }

    function mostrarVencedor(partida) {
        const gols1 = Number(partida.gols_jogador1 || 0);
        const gols2 = Number(partida.gols_jogador2 || 0);

        let resultado;

        if (gols1 > gols2) {
            resultado = `${elementos.nome1?.textContent || "Jogador 1"} venceu!`;
        } else if (gols2 > gols1) {
            resultado = `${elementos.nome2?.textContent || "Jogador 2"} venceu!`;
        } else {
            resultado = "A partida terminou empatada!";
        }

        definirTexto(elementos.vencedor, resultado);
    }

    function formatarData(data) {
        if (!data) return "Data não informada";

        const dataConvertida = new Date(data);

        if (Number.isNaN(dataConvertida.getTime())) {
            return "Data não informada";
        }

        return dataConvertida.toLocaleString("pt-BR");
    }

    function renderizarHistorico(gols) {
        if (!elementos.historico) return;

        elementos.historico.replaceChildren();

        if (!gols || gols.length === 0) {
            const item = document.createElement("li");
            item.textContent = "Nenhum gol registrado nesta partida.";
            elementos.historico.appendChild(item);
            return;
        }

        gols.forEach((gol, indice) => {
            const item = document.createElement("li");
            const jogador = Number(gol.jogador_id);

            let nome = "Jogador não identificado";

            if (jogador === Number(window.partidaAtual?.jogador1)) {
                nome = elementos.nome1?.textContent || "Jogador 1";
            } else if (jogador === Number(window.partidaAtual?.jogador2)) {
                nome = elementos.nome2?.textContent || "Jogador 2";
            }

            item.textContent = `${indice + 1}. ${nome} — ${formatarData(gol.data)}`;
            elementos.historico.appendChild(item);
        });
    }

    async function carregarHistorico(id) {
        if (!elementos.historico) return;

        try {
            const dados = await requisicao(
                `/api/partidas/${encodeURIComponent(id)}/historico-gols`
            );

            renderizarHistorico(dados.gols || []);
        } catch (erro) {
            console.warn("Não foi possível carregar o histórico de gols:", erro);
            elementos.historico.replaceChildren();

            const item = document.createElement("li");
            item.textContent = "Não foi possível carregar o histórico de gols.";
            elementos.historico.appendChild(item);
        }
    }

    async function carregarResultado() {
        const id = obterIdPartida();

        if (!id || !/^\d+$/.test(String(id))) {
            mostrarMensagem(
                "Não foi encontrado o ID da partida. Volte ao jogo e tente novamente.",
                true
            );
            definirTexto(elementos.status, "Partida não identificada");
            return;
        }

        try {
            mostrarMensagem("Carregando resultado da partida...");

            const dados = await requisicao(
                `/api/partidas/${encodeURIComponent(id)}`
            );

            const partida = dados.partida;

            if (!partida) {
                throw new Error("Os dados da partida não foram encontrados.");
            }

            window.partidaAtual = partida;

            await carregarNomes(partida);

            definirTexto(elementos.gols1, partida.gols_jogador1 ?? 0);
            definirTexto(elementos.gols2, partida.gols_jogador2 ?? 0);

            const status = partida.status || "não informado";
            definirTexto(elementos.status, status.replaceAll("_", " "));

            mostrarVencedor(partida);
            await carregarHistorico(id);

            if (status === "em_andamento") {
                mostrarMensagem(
                    "A partida ainda está em andamento. O resultado pode mudar."
                );
            } else {
                mostrarMensagem("Resultado da partida carregado com sucesso!");
            }
        } catch (erro) {
            console.error("Erro ao carregar resultado:", erro);
            mostrarMensagem(erro.message || "Não foi possível carregar o resultado.", true);
        }
    }

    if (elementos.botaoNovoJogo) {
        elementos.botaoNovoJogo.addEventListener("click", () => {
            window.location.href = "/cadastro";
        });
    }

    if (elementos.botaoVoltar) {
        elementos.botaoVoltar.addEventListener("click", () => {
            window.location.href = "/";
        });
    }

    carregarResultado();
});