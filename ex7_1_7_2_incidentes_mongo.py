"""Exercícios 7.1 e 7.2 — API de incidentes (Flask + MongoDB): CRUD, paginação, filtros e ordenação.

Execução: python -m aula07.ex7_1_7_2_incidentes_mongo   (MONGO_URI opcional)

Parâmetros de GET /api/incidentes:
  pagina   (int >= 1, padrão 1)      tamanho (int 1..100, padrão 10)
  severidade (baixa|media|alta|critica)      status (aberto|em_andamento|resolvido)
Ordenação fixa: criado_em decrescente (mais recentes primeiro).
"""
import ipaddress
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request

import comum

SEVERIDADES = ("baixa", "media", "alta", "critica")
STATUS = ("aberto", "em_andamento", "resolvido")


def serializar(doc):
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("criado_em"), datetime):
        doc["criado_em"] = doc["criado_em"].isoformat()
    return doc


def validar(d, parcial=False):
    if not isinstance(d, dict):
        return "corpo inválido"
    if not parcial and (not isinstance(d.get("titulo"), str) or not d["titulo"].strip() or "severidade" not in d):
        return "campos 'titulo' e 'severidade' são obrigatórios"
    if "titulo" in d and (not isinstance(d["titulo"], str) or not 1 <= len(d["titulo"].strip()) <= 200):
        return "titulo inválido"
    if "severidade" in d and d["severidade"] not in SEVERIDADES:
        return "severidade inválida"
    if "status" in d and d["status"] not in STATUS:
        return "status inválido"
    if "ip_origem" in d:
        try:
            ipaddress.ip_address(d["ip_origem"])
        except (ValueError, TypeError):
            return "ip_origem inválido"
    return None


def create_app(colecao=None):
    app = Flask(__name__)
    col = colecao if colecao is not None else comum.mongo_db().incidentes

    def oid(valor):
        try:
            return ObjectId(valor)
        except (InvalidId, TypeError):
            return None

    @app.post("/api/incidentes")
    def criar():
        d = request.get_json(silent=True)
        erro = validar(d)
        if erro:
            return jsonify(erro=erro), 400
        doc = {"titulo": d["titulo"].strip(), "severidade": d["severidade"], "status": d.get("status", "aberto"),
               "ip_origem": d.get("ip_origem"), "criado_em": datetime.now()}
        return jsonify(id=str(col.insert_one(doc).inserted_id)), 201

    @app.get("/api/incidentes")
    def listar():
        try:
            pagina, tamanho = int(request.args.get("pagina", 1)), int(request.args.get("tamanho", 10))
        except ValueError:
            return jsonify(erro="pagina e tamanho devem ser inteiros"), 400
        if pagina < 1 or not 1 <= tamanho <= 100:
            return jsonify(erro="pagina >= 1 e tamanho entre 1 e 100"), 400
        filtro = {}
        for campo, validos in (("severidade", SEVERIDADES), ("status", STATUS)):
            v = request.args.get(campo)
            if v:
                if v not in validos:
                    return jsonify(erro=f"{campo} inválido"), 400
                filtro[campo] = v
        cur = col.find(filtro).sort("criado_em", -1).skip((pagina - 1) * tamanho).limit(tamanho)
        return jsonify(pagina=pagina, tamanho=tamanho, total=col.count_documents(filtro),
                       itens=[serializar(x) for x in cur])

    @app.get("/api/incidentes/<id>")
    def obter(id):
        _id = oid(id)
        if _id is None:
            return jsonify(erro="id inválido"), 400
        doc = col.find_one({"_id": _id})
        return (jsonify(serializar(doc)), 200) if doc else (jsonify(erro="não encontrado"), 404)

    @app.put("/api/incidentes/<id>")
    def atualizar(id):
        _id = oid(id)
        if _id is None:
            return jsonify(erro="id inválido"), 400
        d = request.get_json(silent=True)
        erro = validar(d, parcial=True)
        if erro:
            return jsonify(erro=erro), 400
        campos = {k: d[k] for k in ("titulo", "severidade", "status", "ip_origem") if k in d}
        if not campos:
            return jsonify(erro="nenhum campo para atualizar"), 400
        if col.update_one({"_id": _id}, {"$set": campos}).matched_count == 0:
            return jsonify(erro="não encontrado"), 404
        return jsonify(mensagem="Atualizado"), 200

    @app.delete("/api/incidentes/<id>")
    def remover(id):
        _id = oid(id)
        if _id is None:
            return jsonify(erro="id inválido"), 400
        if col.delete_one({"_id": _id}).deleted_count == 0:
            return jsonify(erro="não encontrado"), 404
        return jsonify(mensagem="Removido"), 200

    @app.errorhandler(404)
    def e404(e): return jsonify(erro="rota não existe"), 404

    @app.errorhandler(500)
    def e500(e): return jsonify(erro="erro interno do servidor"), 500

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)
