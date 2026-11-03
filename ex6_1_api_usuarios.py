"""Exercício 6.1 — API CRUD de usuários (em memória). Execução: python -m aula06.ex6_1_api_usuarios"""
from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)
    usuarios, estado = [], {"proximo_id": 1}

    def achar(uid):
        return next((u for u in usuarios if u["id"] == uid), None)

    def validar(d, parcial=False):
        """Retorna mensagem de erro ou None."""
        if not isinstance(d, dict):
            return "corpo inválido"
        if not parcial and not all(k in d for k in ("nome", "email", "nivel")):
            return "campos 'nome', 'email' e 'nivel' são obrigatórios"
        if "nome" in d and (not isinstance(d["nome"], str) or not d["nome"].strip()):
            return "nome inválido"
        if "email" in d:
            if not isinstance(d["email"], str) or "@" not in d["email"]:
                return "email inválido"
        if "nivel" in d and (not isinstance(d["nivel"], int) or isinstance(d["nivel"], bool) or not 1 <= d["nivel"] <= 5):
            return "nível inválido"
        return None

    def email_existe(email, ignorar_id=None):
        return any(u["email"].lower() == email.lower() and u["id"] != ignorar_id for u in usuarios)

    @app.get("/api/usuarios")
    def listar():
        return jsonify(usuarios)

    @app.get("/api/usuarios/<int:uid>")
    def obter(uid):
        u = achar(uid)
        return (jsonify(u), 200) if u else (jsonify(erro="usuário não encontrado"), 404)

    @app.post("/api/usuarios")
    def criar():
        d = request.get_json(silent=True)
        erro = validar(d)
        if erro:
            return jsonify(erro=erro), 400
        if email_existe(d["email"]):
            return jsonify(erro="email já existe"), 400
        u = {"id": estado["proximo_id"], "nome": d["nome"].strip(), "email": d["email"], "nivel": d["nivel"]}
        estado["proximo_id"] += 1
        usuarios.append(u)
        return jsonify(u), 201

    @app.put("/api/usuarios/<int:uid>")
    def atualizar(uid):
        u = achar(uid)
        if not u:
            return jsonify(erro="usuário não encontrado"), 404
        d = request.get_json(silent=True)
        erro = validar(d, parcial=True)
        if erro:
            return jsonify(erro=erro), 400
        if "email" in d and email_existe(d["email"], ignorar_id=uid):
            return jsonify(erro="email já existe"), 400
        u.update({k: d[k] for k in ("nome", "email", "nivel") if k in d})
        return jsonify(u)

    @app.delete("/api/usuarios/<int:uid>")
    def remover(uid):
        u = achar(uid)
        if not u:
            return jsonify(erro="usuário não encontrado"), 404
        usuarios.remove(u)
        return jsonify(mensagem="Removido"), 200

    @app.errorhandler(404)
    def e404(e): return jsonify(erro="rota não existe"), 404

    @app.errorhandler(500)
    def e500(e): return jsonify(erro="erro interno do servidor"), 500

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)  # nunca debug=True fora do laboratório
