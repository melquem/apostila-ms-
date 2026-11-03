"""Exercício 7.3 — API de usuários (Flask + MySQL) com tratamento de erros.
409 email duplicado | 404 inexistente | 400 corpo inválido | 500 amigável se o banco cair (sem traceback/query).
Execução: MYSQL_PASSWORD=... python -m aula07.ex7_3_usuarios_mysql_api
"""
import logging

import mysql.connector
from flask import Flask, jsonify, request

import comum

log = logging.getLogger("api.usuarios")


def validar(d, parcial=False):
    if not isinstance(d, dict):
        return "corpo inválido"
    if not parcial and not all(k in d for k in ("nome", "email")):
        return "campos 'nome' e 'email' são obrigatórios"
    if "nome" in d and (not isinstance(d["nome"], str) or not 1 <= len(d["nome"].strip()) <= 100):
        return "nome inválido"
    if "email" in d and (not isinstance(d["email"], str) or "@" not in d["email"] or len(d["email"]) > 150):
        return "email inválido"
    n = d.get("nivel_acesso", 1)
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= 5:
        return "nivel_acesso deve estar entre 1 e 5"
    return None


def create_app(get_db=comum.mysql_conn):
    app = Flask(__name__)

    @app.get("/api/usuarios")
    def listar():
        con = get_db()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT id, nome, email, nivel_acesso FROM usuarios ORDER BY id")
            return jsonify(cur.fetchall())
        finally:
            con.close()

    @app.get("/api/usuarios/<int:uid>")
    def obter(uid):
        con = get_db()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT id, nome, email, nivel_acesso FROM usuarios WHERE id = %s", (uid,))
            u = cur.fetchone()
        finally:
            con.close()
        return (jsonify(u), 200) if u else (jsonify(erro="usuário não encontrado"), 404)

    @app.post("/api/usuarios")
    def criar():
        d = request.get_json(silent=True)
        erro = validar(d)
        if erro:
            return jsonify(erro=erro), 400
        con = get_db()
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s)",
                        (d["nome"].strip(), d["email"].lower(), d.get("nivel_acesso", 1)))
            con.commit()
            return jsonify(id=cur.lastrowid), 201
        except mysql.connector.IntegrityError:
            con.rollback()
            return jsonify(erro="email já cadastrado"), 409
        finally:
            con.close()

    @app.put("/api/usuarios/<int:uid>")
    def atualizar(uid):
        d = request.get_json(silent=True)
        erro = validar(d, parcial=True)
        if erro:
            return jsonify(erro=erro), 400
        campos = {k: d[k] for k in ("nome", "email", "nivel_acesso") if k in d}
        if not campos:
            return jsonify(erro="nenhum campo para atualizar"), 400
        # nomes de coluna vêm de uma lista fixa, só os valores são parametrizados
        sets = ", ".join(f"{c} = %s" for c in campos)
        con = get_db()
        try:
            cur = con.cursor()
            cur.execute(f"UPDATE usuarios SET {sets} WHERE id = %s", (*campos.values(), uid))
            con.commit()
            if cur.rowcount == 0:
                cur.execute("SELECT 1 FROM usuarios WHERE id = %s", (uid,))
                if cur.fetchone() is None:
                    return jsonify(erro="usuário não encontrado"), 404
            return jsonify(mensagem="Atualizado"), 200
        except mysql.connector.IntegrityError:
            con.rollback()
            return jsonify(erro="email já cadastrado"), 409
        finally:
            con.close()

    @app.delete("/api/usuarios/<int:uid>")
    def remover(uid):
        con = get_db()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM usuarios WHERE id = %s", (uid,))
            con.commit()
            return (jsonify(mensagem="Removido"), 200) if cur.rowcount else (jsonify(erro="usuário não encontrado"), 404)
        finally:
            con.close()

    @app.errorhandler(mysql.connector.Error)
    def erro_banco(e):
        log.error("erro de banco: %s", e.__class__.__name__)  # detalhe só no log
        return jsonify(erro="serviço indisponível"), 500

    @app.errorhandler(404)
    def e404(e): return jsonify(erro="rota não existe"), 404

    @app.errorhandler(Exception)
    def e500(e):
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return jsonify(erro=e.name.lower()), e.code
        log.exception("erro interno")
        return jsonify(erro="serviço indisponível"), 500

    return app


if __name__ == "__main__":
    from aula03.ex3_1_usuarios import criar_tabela
    c = comum.mysql_conn()
    criar_tabela(c)
    c.close()
    create_app().run(port=5000, debug=False)
