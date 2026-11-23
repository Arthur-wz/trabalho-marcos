# Futebol de Botão

Back-End de uma aplicação de futebol de botão digital, desenvolvida em Python com Flask.

## Sobre o projeto

O projeto consiste em um jogo de futebol de botão para dois jogadores no mesmo computador.

O Back-End é responsável por controlar as regras da partida, validar jogadas, registrar gols, controlar o tempo, alternar os turnos e disponibilizar rankings por meio de uma API REST.

O Front-End é responsável pela interface visual e pela física dos movimentos dos botões e da bola.

## Tecnologias utilizadas

- Python
- Flask
- Flask-CORS
- JSON para comunicação entre Front-End e Back-End

## Estrutura do projeto

```text
trabalho-marcos/
├── app.py
├── requirements.txt
├── README.md
├── database/
│   ├── __init__.py
│   └── memoria.py
├── routes/
│   ├── __init__.py
│   ├── jogadores.py
│   ├── partidas.py
│   └── rankings.py
└── services/
    ├── __init__.py
    ├── tempo.py
    └── turnos.py
```

## Instalação

Clone o repositório:

```bash
git clone https://github.com/Arthur-wz/trabalho-marcos.git
cd trabalho-marcos
```

Crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie o servidor:

```bash
python app.py
```

A API ficará disponível em:

`http://127.0.0.1:5000`

## Comunicação com a API

A comunicação acontece por meio de requisições HTTP, utilizando JSON.

Todas as respostas da API são retornadas em JSON.

### Padrão de resposta

As respostas possuem, geralmente, os seguintes campos:

- `sucesso`: indica se a operação foi realizada.
- `mensagem`: informa o resultado da operação.
- Outros campos podem retornar os dados solicitados ou criados.

## Endpoints da API

### 1. Status do servidor

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/status` | Verifica se a API está funcionando |

Resposta:

```json
{
  "sucesso": true,
  "mensagem": "Back-End do Futebol de Botão funcionando!",
  "servidor": "online"
}
```

### 2. Jogadores

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/jogadores` | Cadastra um jogador |
| GET | `/api/jogadores` | Lista os jogadores cadastrados |

**Cadastrar jogador**

Rota: `POST /api/jogadores`

JSON obrigatório:

```json
{
  "nome": "Arthur",
  "usuario": "arthur123"
}
```

Resposta de sucesso (HTTP 201):

```json
{
  "sucesso": true,
  "mensagem": "Jogador cadastrado com sucesso!",
  "jogador": {
    "id": 1,
    "nome": "Arthur",
    "usuario": "arthur123"
  }
}
```

Validações:
- Nome e usuário são obrigatórios.
- Os campos não podem estar vazios.
- Nome possui limite de 80 caracteres.
- Usuário possui limite de 30 caracteres.
- Não é permitido cadastrar usuários duplicados, mesmo com diferenças entre letras maiúsculas e minúsculas.

Principais erros:
- HTTP 400: dados inválidos ou campos vazios.
- HTTP 409: nome de usuário já existente.

**Listar jogadores**

Rota: `GET /api/jogadores`

Resposta:

```json
{
  "sucesso": true,
  "jogadores": [
    {
      "id": 1,
      "nome": "Arthur",
      "usuario": "arthur123"
    }
  ]
}
```

### 3. Partidas

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/partidas` | Cria uma partida |
| GET | `/api/partidas/<id>` | Consulta uma partida |
| POST | `/api/partidas/<id>/jogadas` | Registra uma jogada |
| POST | `/api/partidas/<id>/gols` | Registra um gol |
| GET | `/api/partidas/<id>/historico-gols` | Consulta o histórico de gols |

**Criar partida**

Rota: `POST /api/partidas`

JSON obrigatório:

```json
{
  "jogador1_id": 1,
  "jogador2_id": 2
}
```

Atenção: os campos devem ser exatamente `jogador1_id` e `jogador2_id`.

Resposta de sucesso (HTTP 201):

```json
{
  "sucesso": true,
  "mensagem": "Partida criada com sucesso!",
  "partida": {
    "id": 1,
    "jogador1": 1,
    "jogador2": 2,
    "gols_jogador1": 0,
    "gols_jogador2": 0,
    "botoes_por_time": 5,
    "duracao_segundos": 300,
    "turno_atual": 1,
    "status": "em_andamento",
    "inicio": "2026-11-23T21:20:43.144123+00:00"
  }
}
```

Validações:
- Os dois IDs devem ser números inteiros.
- Os jogadores precisam ser diferentes.
- Os dois jogadores precisam estar cadastrados.

Principais erros:
- HTTP 400: IDs inválidos ou jogadores iguais.
- HTTP 404: um ou ambos os jogadores não existem.

**Consultar partida**

Rota: `GET /api/partidas/<id>`

Exemplo:

`GET /api/partidas/1`

Resposta:

```json
{
  "sucesso": true,
  "partida": {
    "id": 1,
    "jogador1": 1,
    "jogador2": 2,
    "gols_jogador1": 0,
    "gols_jogador2": 0,
    "botoes_por_time": 5,
    "duracao_segundos": 300,
    "turno_atual": 1,
    "status": "em_andamento",
    "inicio": "2026-11-23T21:20:43.144123+00:00"
  },
  "tempo_restante": 250
}
```

O campo `tempo_restante` informa quantos segundos ainda restam.

A consulta também atualiza o estado da partida caso o tempo tenha acabado.

Principais erros:
- HTTP 404: partida não encontrada.

**Registrar jogada**

Rota: `POST /api/partidas/<id>/jogadas`

JSON obrigatório:

```json
{
  "jogador_id": 1,
  "botao_id": 1,
  "forca": 50,
  "direcao_x": 1,
  "direcao_y": 0
}
```

Atenção aos nomes:
- `jogador_id`: ID do jogador que está realizando a jogada.
- `botao_id`: número do botão utilizado.
- `forca`: intensidade da jogada.
- `direcao_x` e `direcao_y`: direção do movimento.

Validações:
- O jogador precisa participar da partida.
- O jogador precisa estar com o turno atual.
- `botao_id` deve estar entre 1 e 5.
- `forca` deve estar entre 1 e 100.
- `direcao_x` e `direcao_y` devem estar entre -1 e 1.
- A direção não pode ter os dois valores iguais a zero.
- Os valores numéricos precisam ser válidos e finitos.

Resposta de sucesso (HTTP 201):

```json
{
  "sucesso": true,
  "mensagem": "Jogada registrada com sucesso!",
  "jogada": {
    "numero": 1,
    "jogador_id": 1,
    "botao_id": 1,
    "forca": 50,
    "direcao_x": 1,
    "direcao_y": 0
  },
  "proximo_jogador": 2
}
```

O campo `proximo_jogador` informa qual jogador deverá realizar a próxima jogada.

Principais erros:
- HTTP 400: dados inválidos, botão inválido, força fora dos limites ou direção inválida.
- HTTP 403: jogador não participa da partida ou não é sua vez.
- HTTP 404: partida não encontrada.

**Registrar gol**

Rota: `POST /api/partidas/<id>/gols`

JSON obrigatório:

```json
{
  "jogador_id": 1,
  "evento_id": "gol-001"
}
```

Atenção:
- `jogador_id` identifica quem marcou o gol.
- `evento_id` identifica de maneira única aquele evento de gol.
- O Front-End deve gerar um novo `evento_id` para cada gol.
- O mesmo identificador não pode ser utilizado duas vezes na mesma partida.

Resposta de sucesso (HTTP 200):

```json
{
  "sucesso": true,
  "mensagem": "Gol registrado com sucesso!",
  "partida": {
    "id": 1,
    "jogador1": 1,
    "jogador2": 2,
    "gols_jogador1": 1,
    "gols_jogador2": 0
  }
}
```

O objeto `partida` retorna os dados atualizados da partida.

Principais erros:
- HTTP 400: dados inválidos ou partida encerrada.
- HTTP 403: jogador não participa da partida.
- HTTP 404: partida não encontrada.
- HTTP 409: evento de gol já registrado.

Importante: o Back-End registra o gol informado pelo Front-End e protege contra duplicidade do mesmo evento. A detecção física de que a bola entrou no gol é responsabilidade do Front-End.

**Consultar histórico de gols**

Rota: `GET /api/partidas/<id>/historico-gols`

Exemplo:

`GET /api/partidas/1/historico-gols`

Resposta:

```json
{
  "sucesso": true,
  "total_gols": 1,
  "gols": [
    {
      "id": 1,
      "partida_id": 1,
      "jogador_id": 1,
      "evento_id": "gol-001",
      "data": "2026-11-23T21:25:00+00:00"
    }
  ]
}
```

Erro:
- HTTP 404: partida não encontrada.

### 4. Rankings

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/rankings/artilheiros` | Exibe o ranking de gols |
| GET | `/api/rankings/vitorias` | Exibe o ranking de vitórias, derrotas e empates |

**Ranking de artilheiros**

Rota: `GET /api/rankings/artilheiros`

Resposta:

```json
{
  "sucesso": true,
  "total_jogadores": 2,
  "ranking": [
    {
      "jogador_id": 1,
      "nome": "Arthur",
      "gols": 3,
      "posicao": 1
    },
    {
      "jogador_id": 2,
      "nome": "Jogador 2",
      "gols": 1,
      "posicao": 2
    }
  ]
}
```

O ranking é organizado pela quantidade de gols. Jogadores com a mesma quantidade de gols compartilham a posição.

**Ranking de vitórias**

Rota: `GET /api/rankings/vitorias`

Resposta:

```json
{
  "sucesso": true,
  "total_jogadores": 2,
  "ranking": [
    {
      "jogador_id": 1,
      "nome": "Arthur",
      "vitorias": 2,
      "derrotas": 0,
      "empates": 1,
      "partidas": 3,
      "posicao": 1
    },
    {
      "jogador_id": 2,
      "nome": "Jogador 2",
      "vitorias": 0,
      "derrotas": 2,
      "empates": 1,
      "partidas": 3,
      "posicao": 2
    }
  ]
}
```

O ranking considera somente partidas encerradas e é organizado por:
1. Maior número de vitórias.
2. Maior número de empates.
3. Menor número de derrotas.

Jogadores com os mesmos critérios compartilham a posição.

A consulta atualiza o estado das partidas para verificar se o tempo terminou.

## Regras da partida

- Dois jogadores participam da partida.
- Cada jogador possui cinco botões.
- A partida tem duração de cinco minutos (300 segundos).
- Os turnos são alternados entre os jogadores.
- Cada jogada deve ser validada pelo Back-End.
- O Front-End é responsável pela física dos movimentos.
- Os gols são registrados no placar e no histórico.
- O mesmo evento de gol não pode ser registrado duas vezes na mesma partida.
- Ao terminar o tempo, vence quem tiver marcado mais gols.
- Em caso de igualdade, ocorre empate.

O encerramento da partida é verificado quando uma rota que atualiza seu estado é executada, como a consulta da partida, o registro de jogadas ou gols e a consulta do ranking de vitórias. Não existe um processo de atualização em segundo plano.

## Armazenamento de dados

Atualmente, os dados são armazenados temporariamente em memória, por meio do arquivo `database/memoria.py`.

Isso significa que jogadores, partidas e gols são perdidos quando o servidor é reiniciado.

A integração com um banco de dados definitivo será realizada separadamente.

## Responsabilidades na integração

**Back-End:**
- Cadastrar e listar jogadores.
- Criar e consultar partidas.
- Validar jogadas e alternar turnos.
- Registrar gols e atualizar placares.
- Controlar o tempo e encerrar partidas.
- Disponibilizar rankings e histórico de gols.

**Front-End:**
- Exibir as telas e informações do jogo.
- Controlar a interface visual.
- Calcular a física dos movimentos dos botões e da bola.
- Detectar os gols e enviar os eventos para a API.
- Enviar os dados utilizando os nomes de campos definidos nesta documentação.

## Observação final

Esta versão utiliza armazenamento temporário em memória e foi desenvolvida para o escopo do projeto escolar. A persistência definitiva dos dados será implementada separadamente.
