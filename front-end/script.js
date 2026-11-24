
// =============================================
// 1. ELEMENTOS DO JOGO
// =============================================

const campo = document.querySelector(".campo");
const botoes = [...document.querySelectorAll(".botao")];
const bola = document.querySelector(".bola");

const mensagem = document.getElementById("mensagem");
const gols1 = document.getElementById("gols1");
const gols2 = document.getElementById("gols2");
const tempoElemento = document.getElementById("tempo");
const turnoElemento = document.getElementById("turno");

// Verificar elementos necessários
if (!campo || !bola || botoes.length !== 10) {
    throw new Error(
        "Verifique o HTML: campo, bola e 10 jogadores são necessários."
    );
}

// =============================================
// 2. CONFIGURAÇÕES DA PARTIDA
// =============================================

const CONFIG = {
    forca: 0.075,
    forcaMaxima: 140,
    atrito: 0.985,
    velocidadeMinima: 0.08,
    elasticidade: 0.82,
    duracao: 5 * 60
};

// =============================================
// 3. ESTADO DO JOGO
// =============================================

let jogadorSelecionado = null;
let puxando = false;
let emMovimento = false;

let partidaIniciada = false;
let partidaFinalizada = false;

let jogadorDaVez = "vermelho";

let velocidadeX = 0;
let velocidadeY = 0;

let mira = null;

let ultimoTempo = 0;
let tempoRestante = CONFIG.duracao;
let ultimoSegundo = null;

let animacaoCronometro = null;

// Armazenar posições originais
let posicoesIniciais = [];

let pontuacaoVermelho = 0;
let pontuacaoAzul = 0;

// =============================================
// 4. CRIAR OS OBJETOS FÍSICOS
// =============================================

const jogadores = botoes.map(elemento => ({
    elemento,
    x: 0,
    y: 0,
    vx: 0,
    vy: 0,
    raio: 0,
    tipo: "jogador"
}));

const objetoBola = {
    elemento: bola,
    x: 0,
    y: 0,
    vx: 0,
    vy: 0,
    raio: 0,
    tipo: "bola"
};

const objetos = [...jogadores, objetoBola];

// =============================================
// 5. POSIÇÃO DOS OBJETOS
// =============================================

function obterCentro(elemento) {

    const rect = elemento.getBoundingClientRect();
    const campoRect = campo.getBoundingClientRect();

    return {
        x: rect.left + rect.width / 2 -
            campoRect.left - campo.clientLeft,

        y: rect.top + rect.height / 2 -
            campoRect.top - campo.clientTop
    };
}

function inicializarObjetos() {

    objetos.forEach(objeto => {

        const centro = obterCentro(objeto.elemento);

        objeto.x = centro.x;
        objeto.y = centro.y;

        objeto.raio = Math.min(
            objeto.elemento.offsetWidth,
            objeto.elemento.offsetHeight
        ) / 2;

        objeto.vx = 0;
        objeto.vy = 0;

    });
}

function atualizarPosicao(objeto) {

    objeto.elemento.style.left = objeto.x + "px";
    objeto.elemento.style.top = objeto.y + "px";

}

// =============================================
// 6. CONFIGURAÇÃO DOS TURNOS
// =============================================

function atualizarTurno() {

    if (jogadorDaVez === "vermelho") {

        turnoElemento.textContent = "Vez de Marcos 🔴";

    } else {

        turnoElemento.textContent = "Vez de Marcus 🔵";

    }
}

function trocarTurno() {

    jogadorDaVez =
        jogadorDaVez === "vermelho" ? "azul" : "vermelho";

    atualizarTurno();

}

function jogadorPertenceAoTurno(jogador) {

    return jogador.classList.contains(jogadorDaVez);

}

// =============================================
// 7. MIRA DO LANÇAMENTO
// =============================================

function criarMira() {

    mira = document.createElement("div");
    mira.className = "linha-impulso";

    campo.appendChild(mira);

}

function atualizarMira(mouseX, mouseY) {

    if (!jogadorSelecionado || !mira) return;

    const centro = obterCentro(jogadorSelecionado);

    const dx = centro.x - mouseX;
    const dy = centro.y - mouseY;

    const distancia = Math.hypot(dx, dy);

    const tamanho = Math.min(
        distancia,
        CONFIG.forcaMaxima
    );

    const angulo = Math.atan2(dy, dx) * 180 / Math.PI;

    mira.style.left = centro.x + "px";
    mira.style.top = centro.y + "px";
    mira.style.width = tamanho + "px";

    mira.style.transform =
        `translateY(-50%) rotate(${angulo}deg)`;

}

// =============================================
// 8. POSIÇÃO DO MOUSE
// =============================================

function obterPosicao(evento) {

    const rect = campo.getBoundingClientRect();

    return {
        x: evento.clientX - rect.left - campo.clientLeft,
        y: evento.clientY - rect.top - campo.clientTop
    };

}

// =============================================
// 9. SELECIONAR JOGADOR
// =============================================

botoes.forEach(jogador => {

    jogador.addEventListener("pointerdown", evento => {

        if (evento.button !== 0) return;

        if (
            emMovimento ||
            puxando ||
            partidaFinalizada
        ) return;

        if (!jogadorPertenceAoTurno(jogador)) {

            mensagem.textContent =
                "Espere sua vez de jogar!";

            return;
        }

        evento.preventDefault();

        jogadorSelecionado = jogador;
        puxando = true;

        botoes.forEach(botao => {

            botao.classList.remove("selecionado");

        });

        jogador.classList.add("selecionado");

        criarMira();

        mensagem.textContent =
            "Puxe a peça para trás e solte para lançar!";

        jogador.setPointerCapture(evento.pointerId);

    });

});

// =============================================
// 10. MOVIMENTAR A MIRA
// =============================================

window.addEventListener("pointermove", evento => {

    if (!puxando || !jogadorSelecionado) return;

    const mouse = obterPosicao(evento);

    atualizarMira(mouse.x, mouse.y);

});

// =============================================
// 11. LANÇAR JOGADOR
// =============================================

window.addEventListener("pointerup", evento => {

    if (!puxando || !jogadorSelecionado) return;

    puxando = false;

    const mouse = obterPosicao(evento);
    const centro = obterCentro(jogadorSelecionado);

    const dx = centro.x - mouse.x;
    const dy = centro.y - mouse.y;

    const distancia = Math.hypot(dx, dy);

    if (mira) {

        mira.remove();
        mira = null;

    }

    if (distancia < 8) {

        mensagem.textContent =
            "Puxada muito curta. Tente novamente!";

        jogadorSelecionado.classList.remove("selecionado");

        jogadorSelecionado = null;

        return;
    }

    const forca = Math.min(
        distancia,
        CONFIG.forcaMaxima
    );

    const direcaoX = dx / distancia;
    const direcaoY = dy / distancia;

    const objeto = jogadores.find(
        item => item.elemento === jogadorSelecionado
    );

    objeto.vx = direcaoX * forca * CONFIG.forca;
    objeto.vy = direcaoY * forca * CONFIG.forca;

    objeto.x = centro.x;
    objeto.y = centro.y;

    velocidadeX = objeto.vx;
    velocidadeY = objeto.vy;

    jogadorSelecionado.classList.remove("selecionado");

    jogadorSelecionado = null;

    // Iniciar cronômetro na primeira jogada
    iniciarPartida();

    emMovimento = true;
    ultimoTempo = 0;

    mensagem.textContent = "Peça lançada!";

    requestAnimationFrame(atualizarFisica);

});

// =============================================
// 12. INICIAR PARTIDA E CRONÔMETRO
// =============================================

function iniciarPartida() {

    if (partidaIniciada || partidaFinalizada) return;

    partidaIniciada = true;

    ultimoSegundo = performance.now();

    atualizarCronometroContinuamente();

}

// =============================================
// 13. ATUALIZAR CRONÔMETRO
// =============================================

function atualizarCronometroContinuamente() {

    if (!partidaIniciada || partidaFinalizada) return;

    const agora = performance.now();

    if (ultimoSegundo === null) {

        ultimoSegundo = agora;

    }

    const decorrido = (agora - ultimoSegundo) / 1000;

    if (decorrido >= 1) {

        const segundos = Math.floor(decorrido);

        tempoRestante -= segundos;

        ultimoSegundo += segundos * 1000;

        if (tempoRestante <= 0) {

            tempoRestante = 0;

            atualizarDisplayCronometro();

            finalizarPartida();

            return;
        }

        atualizarDisplayCronometro();

    }

    animacaoCronometro = requestAnimationFrame(
        atualizarCronometroContinuamente
    );

}

function atualizarDisplayCronometro() {

    const minutos = Math.floor(tempoRestante / 60);
    const segundos = tempoRestante % 60;

    tempoElemento.textContent =
        `${String(minutos).padStart(2, "0")}:${String(segundos).padStart(2, "0")}`;

}

// =============================================
// 14. COLISÃO ENTRE DOIS OBJETOS
// =============================================

function verificarColisao(a, b) {

    const dx = b.x - a.x;
    const dy = b.y - a.y;

    const distancia = Math.hypot(dx, dy);

    const distanciaMinima = a.raio + b.raio;

    if (distancia >= distanciaMinima || distancia === 0) {
        return false;
    }

    const nx = dx / distancia;
    const ny = dy / distancia;

    // Corrigir sobreposição
    const sobreposicao = distanciaMinima - distancia;

    a.x -= nx * sobreposicao / 2;
    a.y -= ny * sobreposicao / 2;

    b.x += nx * sobreposicao / 2;
    b.y += ny * sobreposicao / 2;

    // Velocidade relativa
    const velocidadeRelativaX = b.vx - a.vx;
    const velocidadeRelativaY = b.vy - a.vy;

    const velocidadeNormal =
        velocidadeRelativaX * nx +
        velocidadeRelativaY * ny;

    // Não aplicar impulso se estiverem se afastando
    if (velocidadeNormal > 0) return true;

    const impulso =
        -(1 + CONFIG.elasticidade) * velocidadeNormal / 2;

    a.vx -= impulso * nx;
    a.vy -= impulso * ny;

    b.vx += impulso * nx;
    b.vy += impulso * ny;

    return true;

}

// =============================================
// 15. COLISÕES ENTRE TODOS OS OBJETOS
// =============================================

function verificarTodasColisoes() {

    for (let i = 0; i < objetos.length; i++) {

        for (let j = i + 1; j < objetos.length; j++) {

            verificarColisao(objetos[i], objetos[j]);

        }

    }

}

// =============================================
// 16. COLISÃO COM AS LATERAIS
// =============================================

function verificarLimites(objeto) {

    const largura = campo.clientWidth;
    const altura = campo.clientHeight;

    const raio = objeto.raio;

    if (objeto.x < raio) {

        objeto.x = raio;

        objeto.vx = Math.abs(objeto.vx) * CONFIG.elasticidade;

    }

    if (objeto.x > largura - raio) {

        objeto.x = largura - raio;

        objeto.vx = -Math.abs(objeto.vx) * CONFIG.elasticidade;

    }

    if (objeto.y < raio) {

        objeto.y = raio;

        objeto.vy = Math.abs(objeto.vy) * CONFIG.elasticidade;

    }

    if (objeto.y > altura - raio) {

        objeto.y = altura - raio;

        objeto.vy = -Math.abs(objeto.vy) * CONFIG.elasticidade;

    }

}

// =============================================
// 17. RESTAURAR POSIÇÕES INICIAIS
// =============================================

function restaurarPosicoesIniciais() {

    objetos.forEach((objeto, indice) => {

        const posicao = posicoesIniciais[indice];

        objeto.x = posicao.x;
        objeto.y = posicao.y;

        // Zerar velocidades
        objeto.vx = 0;
        objeto.vy = 0;

        // Atualizar posição visual
        atualizarPosicao(objeto);

    });

    velocidadeX = 0;
    velocidadeY = 0;

    emMovimento = false;
    ultimoTempo = 0;

}

// =============================================
// 18. DETECTAR GOLS
// =============================================

function verificarGol() {

    const gols = [...campo.querySelectorAll(".gol")];

    for (const gol of gols) {

        const rectCampo = campo.getBoundingClientRect();
        const rectGol = gol.getBoundingClientRect();

        const esquerda =
            rectGol.left - rectCampo.left - campo.clientLeft;

        const direita =
            rectGol.right - rectCampo.left - campo.clientLeft;

        const topo =
            rectGol.top - rectCampo.top - campo.clientTop;

        const baixo =
            rectGol.bottom - rectCampo.top - campo.clientTop;

        const bolaEntrou =
            objetoBola.x >= esquerda &&
            objetoBola.x <= direita &&
            objetoBola.y >= topo &&
            objetoBola.y <= baixo;

        if (!bolaEntrou) continue;

        registrarGol(gol);

        return true;

    }

    return false;

}

// =============================================
// 19. REGISTRAR GOL
// =============================================

function registrarGol(gol) {

    const centroCampo = campo.clientWidth / 2;

    const rectCampo = campo.getBoundingClientRect();
    const rectGol = gol.getBoundingClientRect();

    const centroGol =
        rectGol.left + rectGol.width / 2 -
        rectCampo.left - campo.clientLeft;

    let timeQueMarcou;

    if (
        Math.abs(centroGol - centroCampo) >
        campo.clientWidth * 0.1
    ) {

        // Gol esquerdo: azul marca
        // Gol direito: vermelho marca

        timeQueMarcou =
            centroGol < centroCampo ? "azul" : "vermelho";

    } else {

        // Gols superiores e inferiores

        timeQueMarcou =
            gol.classList.contains("gol-topo")
                ? "azul"
                : "vermelho";

    }

    // Atualizar placar
    if (timeQueMarcou === "vermelho") {

        pontuacaoVermelho++;

        gols1.textContent = pontuacaoVermelho;

    } else {

        pontuacaoAzul++;

        gols2.textContent = pontuacaoAzul;

    }

    // Mensagem do gol
    mensagem.textContent =
        timeQueMarcou === "vermelho"
            ? "GOOOOL DO MARCOS! 🔴"
            : "GOOOOL DO MARCUS! 🔵";

    // Parar todos os movimentos
    pararMovimento();

    // RETORNAR TODOS OS JOGADORES E A BOLA
    restaurarPosicoesIniciais();

    // Trocar turno
    trocarTurno();

}

// =============================================
// 20. APLICAR ATRITO
// =============================================

function aplicarAtrito(objeto, dt) {

    const fator = Math.pow(CONFIG.atrito, dt);

    objeto.vx *= fator;
    objeto.vy *= fator;

    if (Math.abs(objeto.vx) < CONFIG.velocidadeMinima) {

        objeto.vx = 0;

    }

    if (Math.abs(objeto.vy) < CONFIG.velocidadeMinima) {

        objeto.vy = 0;

    }

}

// =============================================
// 21. VERIFICAR SE TUDO PAROU
// =============================================

function verificarSeParou() {

    return objetos.every(objeto =>

        Math.abs(objeto.vx) < CONFIG.velocidadeMinima &&
        Math.abs(objeto.vy) < CONFIG.velocidadeMinima

    );

}

// =============================================
// 22. PARAR MOVIMENTO
// =============================================

function pararMovimento() {

    emMovimento = false;

    objetos.forEach(objeto => {

        objeto.vx = 0;
        objeto.vy = 0;

    });

    velocidadeX = 0;
    velocidadeY = 0;

    ultimoTempo = 0;

}

// =============================================
// 23. MOTOR DA FÍSICA
// =============================================

function atualizarFisica(tempoAtual) {

    if (!emMovimento || partidaFinalizada) return;

    if (ultimoTempo === 0) {

        ultimoTempo = tempoAtual;

    }

    const dt = Math.min(
        (tempoAtual - ultimoTempo) / 16.67,
        2
    );

    ultimoTempo = tempoAtual;

    // Mover todos os objetos
    objetos.forEach(objeto => {

        objeto.x += objeto.vx * dt;
        objeto.y += objeto.vy * dt;

    });

    // Detectar gol antes dos limites
    if (verificarGol()) return;

    // Colisões entre jogadores e bola
    verificarTodasColisoes();

    // Limites e atrito
    objetos.forEach(objeto => {

        verificarLimites(objeto);

        aplicarAtrito(objeto, dt);

        atualizarPosicao(objeto);

    });

    // Verificar se tudo parou
    if (verificarSeParou()) {

        pararMovimento();

        trocarTurno();

        mensagem.textContent =
            "Jogada encerrada! Prepare a próxima jogada.";

        return;

    }

    requestAnimationFrame(atualizarFisica);

}

// =============================================
// 24. FINALIZAR PARTIDA
// =============================================

function finalizarPartida() {

    if (partidaFinalizada) return;

    partidaFinalizada = true;

    // Cancelar cronômetro
    if (animacaoCronometro !== null) {

        cancelAnimationFrame(animacaoCronometro);

        animacaoCronometro = null;

    }

    // Parar todas as peças
    pararMovimento();

    if (pontuacaoVermelho > pontuacaoAzul) {

        mensagem.textContent =
            "FIM DE JOGO! Marcos venceu! 🔴";

    } else if (pontuacaoAzul > pontuacaoVermelho) {

        mensagem.textContent =
            "FIM DE JOGO! Marcus venceu! 🔵";

    } else {

        mensagem.textContent =
            "FIM DE JOGO! Empate! 🤝";

    }

    turnoElemento.textContent = "Partida encerrada";

}

// =============================================
// 25. CANCELAR PUXADA
// =============================================

window.addEventListener("pointercancel", () => {

    if (!puxando) return;

    puxando = false;

    if (mira) {

        mira.remove();

        mira = null;

    }

    if (jogadorSelecionado) {

        jogadorSelecionado.classList.remove("selecionado");

    }

    jogadorSelecionado = null;

    mensagem.textContent =
        "Movimento cancelado. Tente novamente.";

});

// =============================================
// 26. INICIALIZAR O JOGO
// =============================================

function inicializarJogo() {

    // Posicionar objetos conforme o HTML
    inicializarObjetos();

    // SALVAR POSIÇÕES ORIGINAIS
    posicoesIniciais = objetos.map(objeto => ({

        x: objeto.x,
        y: objeto.y

    }));

    // Inicializar cronômetro
    tempoElemento.textContent = "05:00";

    // Inicializar placar
    gols1.textContent = "0";
    gols2.textContent = "0";

    // Inicializar turno
    atualizarTurno();

    mensagem.textContent =
        "Jogo pronto! Marcos começa. Selecione uma peça vermelha.";

}

inicializarJogo();
