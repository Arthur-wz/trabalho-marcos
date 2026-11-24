
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DA PÁGINA
    // ==========================================

    const listaRanking = document.getElementById("listaRanking");
    const tituloRanking = document.getElementById("tituloRanking");
    const totalJogadores = document.getElementById("totalJogadores");
    const mensagemRanking = document.getElementById("mensagemRanking");

    const botaoVitorias = document.getElementById("rankingVitorias");
    const botaoArtilheiros = document.getElementById("rankingArtilheiros");
    const botaoAtualizar = document.getElementById("atualizarRanking");

    let rankingAtual = "vitorias";


    // ==========================================
    // CONFIGURAÇÃO DOS RANKINGS
    // ==========================================

    const rankings = {

        vitorias: {
            url: "/api/rankings/vitorias",
            titulo: "Ranking de Vitórias",
            descricao: "Classificação geral do campeonato."
        },

        artilheiros: {
            url: "/api/rankings/artilheiros",
            titulo: "Ranking de Artilheiros",
            descricao: "Jogadores com mais gols marcados."
        }

    };


    // ==========================================
    // MENSAGENS
    // ==========================================

    function mostrarMensagem(texto, tipo = "info") {

        if (!mensagemRanking) return;

        mensagemRanking.textContent = texto;
        mensagemRanking.className = `mensagem ${tipo}`;

    }


    // ==========================================
    // ATUALIZAR BOTÕES
    // ==========================================

    function atualizarBotoes() {

        if (botaoVitorias) {
            botaoVitorias.classList.toggle(
                "ativo",
                rankingAtual === "vitorias"
            );
        }

        if (botaoArtilheiros) {
            botaoArtilheiros.classList.toggle(
                "ativo",
                rankingAtual === "artilheiros"
            );
        }

    }


    // ==========================================
    // CRIAR LINHA DO RANKING
    // ==========================================

    function criarJogador(jogador, tipo) {

        const item = document.createElement("div");

        item.className = "item-ranking";

        const posicao = document.createElement("span");

        posicao.className = "posicao-ranking";
        posicao.textContent = `${jogador.posicao}º`;

        if (jogador.posicao === 1) {
            posicao.classList.add("primeiro-lugar");
        }

        const informacoes = document.createElement("div");

        informacoes.className = "informacoes-jogador";

        const nome = document.createElement("strong");

        nome.textContent = jogador.nome;

        const estatisticas = document.createElement("span");

        estatisticas.className = "estatisticas-jogador";

        if (tipo === "vitorias") {

            estatisticas.textContent =
                `${jogador.partidas} partidas | ` +
                `${jogador.vitorias} vitórias | ` +
                `${jogador.empates} empates | ` +
                `${jogador.derrotas} derrotas`;

        } else {

            estatisticas.textContent =
                `${jogador.gols} gols marcados`;

        }

        const destaque = document.createElement("span");

        destaque.className = "destaque-ranking";

        destaque.textContent =
            tipo === "vitorias"
                ? `${jogador.vitorias} V`
                : `${jogador.gols} GOLS`;

        informacoes.appendChild(nome);
        informacoes.appendChild(estatisticas);

        item.appendChild(posicao);
        item.appendChild(informacoes);
        item.appendChild(destaque);

        return item;

    }


    // ==========================================
    // CARREGAR RANKING
    // ==========================================

    async function carregarRanking(tipo = rankingAtual) {

        rankingAtual = tipo;

        const configuracao = rankings[tipo];

        if (!configuracao || !listaRanking) return;

        atualizarBotoes();

        if (tituloRanking) {
            tituloRanking.textContent = configuracao.titulo;
        }

        listaRanking.innerHTML = "";

        const carregando = document.createElement("p");

        carregando.textContent = "Carregando classificação...";

        listaRanking.appendChild(carregando);

        mostrarMensagem("Atualizando classificação...");

        try {

            const resposta = await fetch(configuracao.url);

            const dados = await resposta.json();

            if (!resposta.ok || !dados.sucesso) {

                throw new Error(
                    dados.mensagem || "Erro ao consultar o ranking."
                );

            }

            listaRanking.innerHTML = "";

            const jogadores = dados.ranking || [];

            if (totalJogadores) {
                totalJogadores.textContent = dados.total_jogadores;
            }

            if (jogadores.length === 0) {

                const vazio = document.createElement("p");

                vazio.textContent =
                    "Nenhum jogador cadastrado para esta classificação.";

                listaRanking.appendChild(vazio);

                mostrarMensagem("Aguardando jogadores.", "info");

                return;

            }

            jogadores.forEach(jogador => {

                const item = criarJogador(jogador, tipo);

                listaRanking.appendChild(item);

            });

            mostrarMensagem(
                "Classificação atualizada com sucesso!",
                "sucesso"
            );

        } catch (erro) {

            console.error("Erro ao carregar ranking:", erro);

            listaRanking.innerHTML = "";

            const erroElemento = document.createElement("p");

            erroElemento.textContent =
                "Não foi possível carregar o ranking. Tente novamente.";

            listaRanking.appendChild(erroElemento);

            mostrarMensagem(erro.message, "erro");

        }

    }


    // ==========================================
    // EVENTOS DOS BOTÕES
    // ==========================================

    if (botaoVitorias) {

        botaoVitorias.addEventListener("click", () => {

            carregarRanking("vitorias");

        });

    }

    if (botaoArtilheiros) {

        botaoArtilheiros.addEventListener("click", () => {

            carregarRanking("artilheiros");

        });

    }

    if (botaoAtualizar) {

        botaoAtualizar.addEventListener("click", () => {

            carregarRanking(rankingAtual);

        });

    }


    // ==========================================
    // INICIALIZAÇÃO
    // ==========================================

    carregarRanking("vitorias");

});
