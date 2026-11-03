"""Exercício 6.2 — POST /api/analisar-senha (reaproveita verificar_senha do 1º semestre)."""
import re

from flask import Flask, jsonify, request


def verificar_senha(senha):
    criterios = {"tamanho_min": len(senha) >= 8,
                 "maiuscula": bool(re.search(r"[A-Z]", senha)),
                 "minuscula": bool(re.search(r"[a-z]", senha)),
                 "numero": bool(re.search(r"\d", senha)),
                 "especial": bool(re.search(r"[^A-Za-z0-9]", senha))}
    n = sum(criterios.values())
    forca = {5: "Muito forte", 4: "Forte", 3: "Média"}.get(n, "Fraca")
    return forca, criterios


def create_app():
    app = Flask(__name__)

    @app.post("/api/analisar-senha")
    def analisar():
        d = request.get_json(silent=True)
        if not isinstance(d, dict) or "senha" not in d:
            return jsonify(erro="campo 'senha' obrigatório"), 400
        if not isinstance(d["senha"], str) or len(d["senha"]) > 256:
            return jsonify(erro="campo 'senha' inválido"), 400
        forca, criterios = verificar_senha(d["senha"])  # a senha nunca é logada nem devolvida
        return jsonify(forca=forca, criterios=criterios)

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)
