"""Exercício 6.3 — GET /api/checar-ip/<ip> (blacklist em set + privado/público)."""
import ipaddress

from flask import Flask, jsonify

BLACKLIST = {"185.220.101.1", "45.33.32.156", "91.240.118.172"}


def create_app():
    app = Flask(__name__)

    @app.get("/api/checar-ip/<ip>")
    def checar(ip):
        try:
            obj = ipaddress.ip_address(ip)
        except ValueError:
            return jsonify(erro="IP inválido"), 400
        norm = str(obj)
        return jsonify(ip=norm, na_blacklist=norm in BLACKLIST, tipo="privado" if obj.is_private else "publico")

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)
