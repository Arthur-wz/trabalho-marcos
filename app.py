
from flask import Flask, jsonify
from flask_cors import CORS
from routes.rankings import rankings_bp
from routes.jogadores import jogadores_bp
from routes.partidas import partidas_bp

app = Flask(__name__)

CORS(app)

# Registro dos módulos da API
app.register_blueprint(jogadores_bp)
app.register_blueprint(partidas_bp)
app.register_blueprint(rankings_bp)

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "sucesso": True,
        "mensagem": "Back-End do Futebol de Botão funcionando!",
        "servidor": "online"
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
