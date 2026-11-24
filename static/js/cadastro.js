
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DA PÁGINA
    // ==========================================

    const formulario = document.getElementById("cadastroForm");
    const campoNome = document.getElementById("nomeJogador");
    const campoUsuario = document.getElementById("usuarioJogador");
    const mensagem = document.getElementById("mensagemCadastro");
    const listaJogadores = document.getElementById("listaJogadores");
    const botaoAtualizar = document.getElementById("atualizarJogadores");


    // Verifica se os elementos necessários existem
    if (!formulario || !campoNome || !campoUsuario || !mensagem) {
        console.error("Elementos do formulário de cadastro não encontrados.");
        return;
    }


    // ==========================================
    // EXIBIR MENSAGENS
    // ==========================================

    function mostrarMensagem(texto, tipo = "info") {

        mensagem.textContent = texto;

        mensagem.className = `mensagem ${tipo}`;

    }


    // ==========================================
    // LISTAR JOGADORES CADASTRADOS
    // ==========================================

    async function carregarJogadores() {

        if (!listaJogadores) return;

        try {

            const resposta = await fetch("/api/jogadores");

            const dados = await resposta.json();

            if (!resposta.ok || !dados.sucesso) {
                throw new Error("Não foi possível carregar os jogadores.");
            }

            listaJogadores.innerHTML = "";

            if (dados.jogadores.length === 0) {

                const item = document.createElement("li");

                item.textContent = "Nenhum jogador cadastrado ainda.";

                listaJogadores.appendChild(item);

                return;
            }

            dados.jogadores.forEach(jogador => {

                const item = document.createElement("li");

                item.textContent = `${jogador.nome} (@${jogador.usuario})`;

                listaJogadores.appendChild(item);

            });

        } catch (erro) {

            console.error("Erro ao carregar jogadores:", erro);

            mostrarMensagem(
                "Não foi possível carregar a lista de jogadores.",
                "erro"
            );

        }

    }


    // ==========================================
    // CADASTRAR NOVO JOGADOR
    // ==========================================

    formulario.addEventListener("submit", async (evento) => {

        evento.preventDefault();

        const nome = campoNome.value.trim();
        const usuario = campoUsuario.value.trim();

        // Validação dos campos
        if (!nome || !usuario) {

            mostrarMensagem(
                "Preencha todos os campos antes de continuar.",
                "erro"
            );

            return;
        }

        if (nome.length > 80 || usuario.length > 30) {

            mostrarMensagem(
                "O nome deve ter até 80 caracteres e o usuário até 30.",
                "erro"
            );

            return;
        }

        const botaoEnviar = formulario.querySelector(
            'button[type="submit"]'
        );

        if (botaoEnviar) {
            botaoEnviar.disabled = true;
            botaoEnviar.textContent = "Cadastrando...";
        }

        try {

            const resposta = await fetch("/api/jogadores", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    nome: nome,
                    usuario: usuario
                })

            });

            const dados = await resposta.json();

            if (!resposta.ok) {

                throw new Error(
                    dados.mensagem || "Erro ao cadastrar jogador."
                );

            }

            mostrarMensagem(
                dados.mensagem || "Jogador cadastrado com sucesso!",
                "sucesso"
            );

            // Limpa os campos
            formulario.reset();

            // Atualiza a lista
            await carregarJogadores();

            campoNome.focus();

        } catch (erro) {

            mostrarMensagem(erro.message, "erro");

            console.error("Erro no cadastro:", erro);

        } finally {

            if (botaoEnviar) {

                botaoEnviar.disabled = false;
                botaoEnviar.textContent = "Cadastrar jogador";

            }

        }

    });


    // ==========================================
    // ATUALIZAR LISTA MANUALMENTE
    // ==========================================

    if (botaoAtualizar) {

        botaoAtualizar.addEventListener("click", () => {

            carregarJogadores();

        });

    }


    // ==========================================
    // INICIALIZAÇÃO
    // ==========================================

    carregarJogadores();

});
