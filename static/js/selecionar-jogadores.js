const form = document.getElementById("form-partida");
const vermelhoSelect = document.getElementById("jogador-vermelho");
const azulSelect = document.getElementById("jogador-azul");
const mensagem = document.getElementById("mensagem-partida");
const botao = document.getElementById("btn-iniciar-partida");

async function carregarListaJogadores() {
    try {
        const resposta = await fetch("/api/jogadores");
        const dados = await resposta.json();

        if (!resposta.ok || !dados.sucesso) {
            throw new Error(dados.mensagem || "Falha ao consultar jogadores.");
        }

        const jogadores = dados.jogadores || [];
        preencherSelect(vermelhoSelect, jogadores, "Selecione o jogador vermelho");
        preencherSelect(azulSelect, jogadores, "Selecione o jogador azul");

        if (jogadores.length < 2) {
            mensagem.textContent = "Cadastre pelo menos dois jogadores para criar uma partida.";
            botao.disabled = true;
        }
    } catch (erro) {
        mensagem.textContent = erro.message || "Não foi possível carregar os jogadores.";
        vermelhoSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        azulSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        botao.disabled = true;
    }
}

function preencherSelect(select, jogadores, textoInicial) {
    select.replaceChildren();
    const inicial = document.createElement("option");
    inicial.value = "";
    inicial.textContent = textoInicial;
    select.appendChild(inicial);

    jogadores.forEach(jogador => {
        const option = document.createElement("option");
        option.value = jogador.id;
        option.textContent = jogador.nome;
        select.appendChild(option);
    });
}

function atualizarOpcoes() {
    const escolhidoVermelho = vermelhoSelect.value;
    Array.from(azulSelect.options).forEach(option => {
        option.disabled = Boolean(escolhidoVermelho) && option.value === escolhidoVermelho;
    });
    if (azulSelect.value && azulSelect.value === escolhidoVermelho) {
        azulSelect.value = "";
    }
}
vermelhoSelect.addEventListener("change", atualizarOpcoes);
azulSelect.addEventListener("change", atualizarOpcoes);

form.addEventListener("submit", async evento => {
    evento.preventDefault();
    const jogador1 = Number(vermelhoSelect.value);
    const jogador2 = Number(azulSelect.value);

    if (!jogador1 || !jogador2) {
        mensagem.textContent = "Escolha os dois jogadores.";
        return;
    }
    if (jogador1 === jogador2) {
        mensagem.textContent = "Escolha jogadores diferentes para cada time.";
        return;
    }

    botao.disabled = true;
    mensagem.textContent = "Criando partida...";
    try {
        const resposta = await fetch("/api/partidas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jogador1_id: jogador1,
                jogador2_id: jogador2
            })
        });
        const dados = await resposta.json();

        if (!resposta.ok || !dados.sucesso || !dados.partida || !dados.partida.id) {
            throw new Error(dados.mensagem || "A API não conseguiu criar a partida.");
        }

        window.location.href = `/jogo?id=${encodeURIComponent(dados.partida.id)}`;
    } catch (erro) {
        mensagem.textContent = erro.message || "Erro ao criar partida.";
        botao.disabled = false;
    }
});

carregarListaJogadores();