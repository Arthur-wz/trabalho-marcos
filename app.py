
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from routes.rankings import rankings_bp
from routes.jogadores import jogadores_bp
from routes.partidas import partidas_bp


# Configuração da aplicação
app = Flask(__name__)

CORS(app)


# ==========================================
# REGISTRO DAS APIs DO BACK-END
# ==========================================

app.register_blueprint(jogadores_bp)
app.register_blueprint(partidas_bp)
app.register_blueprint(rankings_bp)


# ==========================================
# ROTAS DAS PÁGINAS HTML
# ==========================================

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/regras")
def regras():
    return render_template("regras.html")


@app.route("/jogo")
def jogo():
    return render_template("jogo.html")


@app.route("/resultado")
def resultado():
    return render_template("resultado.html")


@app.route("/ranking")
def ranking():
    return render_template("ranking.html")


# ==========================================
# STATUS DA API
# ==========================================

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "sucesso": True,
        "mensagem": "Back-End do Futebol de Botão funcionando!",
        "servidor": "online"
    }), 200


# ==========================================
# INICIALIZAÇÃO DO SERVIDOR
# ==========================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
