"""Exercício 8.2 — POST /login endurecido (MySQL parametrizado, 401 genérico, limite de tentativas).

Por que a mensagem de erro é genérica? Se a API dissesse "usuário não existe" ou "senha incorreta",
um atacante poderia testar listas de nomes e descobrir quais contas são válidas (user enumeration, OWASP A07)
para então focar a força bruta nelas. Com a mesma resposta (e custo de tempo igual, via hash falso),
usuário inexistente e senha errada ficam indistinguíveis.

Execução: MYSQL_PASSWORD=... python -m aula08.ex8_2_login
"""
import os
import time
from collections import defaultdict, deque

from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

USUARIOS_EXEMPLO = {"admin": "Cyber@2024", "analista": "S3gur4nca!"}
HASH_FALSO = generate_password_hash("hash-para-igualar-tempo")
MAX_FALHAS, JANELA = 5, 60  # 5 falhas por minuto por IP


def preparar_banco():
    import comum
    con = comum.mysql_conn()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS usuarios_login (usuario VARCHAR(50) PRIMARY KEY, senha_hash VARCHAR(255) NOT NULL)")
    for u, s in USUARIOS_EXEMPLO.items():
        cur.execute("REPLACE INTO usuarios_login (usuario, senha_hash) VALUES (%s, %s)", (u, generate_password_hash(s)))
    con.commit()
    con.close()


def buscar_hash_mysql(usuario):
    """Query parametrizada: a entrada nunca é concatenada."""
    import comum
    con = comum.mysql_conn()
    try:
        cur = con.cursor()
        cur.execute("SELECT senha_hash FROM usuarios_login WHERE usuario = %s", (usuario,))
        linha = cur.fetchone()
        return linha[0] if linha else None
    finally:
        con.close()


def create_app(buscar_hash=buscar_hash_mysql, agora=time.time):
    app = Flask(__name__)
    falhas = defaultdict(deque)

    def bloqueado(ip):
        q = falhas[ip]
        while q and agora() - q[0] > JANELA:
            q.popleft()
        return len(q) >= MAX_FALHAS

    @app.post("/login")
    def login():
        ip = request.remote_addr
        if bloqueado(ip):
            return jsonify(erro="Muitas tentativas. Tente novamente mais tarde."), 429
        d = request.get_json(silent=True)
        if not isinstance(d, dict) or not isinstance(d.get("usuario"), str) or not isinstance(d.get("senha"), str) \
                or not d["usuario"].strip() or not d["senha"]:
            return jsonify(erro="usuário e senha são obrigatórios"), 400
        try:
            h = buscar_hash(d["usuario"])
        except Exception:
            return jsonify(erro="serviço indisponível"), 503  # sem vazar detalhes do banco
        ok = check_password_hash(h or HASH_FALSO, d["senha"])
        if h and ok:
            falhas[ip].clear()
            return jsonify(mensagem="Login OK"), 200
        falhas[ip].append(agora())
        return jsonify(erro="Credenciais inválidas"), 401

    return app


if __name__ == "__main__":
    preparar_banco()
    create_app().run(port=5000, debug=False)
