# Exercício 8.3 — Auditoria de código (OWASP Top 10:2025)

Código auditado:

```python
@app.route("/user/<nome>")
def user(nome):
    cur.execute("SELECT * FROM users WHERE nome='" + nome + "'")   # (1)
    dados = cur.fetchone()
    return f"<h1>Bem-vindo {nome}</h1>" + str(dados)               # (2)

app.run(debug=True, host="0.0.0.0")                                # (3)
SENHA_DB = "123456"                                                # (4)
# (5) nenhuma rota registra logs de acesso ou tentativa de erro
```

| # | Falha | Categoria OWASP 2025 | Risco | Correção |
|---|---|---|---|---|
| 1 | SQL Injection: `nome` concatenado na query | **A05 Injection** | `/user/' OR '1'='1` devolve todos os usuários; pode permitir ler ou alterar o banco | Query parametrizada: `cur.execute("SELECT id, nome FROM users WHERE nome=%s", (nome,))` |
| 2 | XSS refletido: `nome` entra cru no HTML. Além disso `str(dados)` expõe a linha inteira do banco (hash de senha, e-mail) | **A05 Injection** (e A01 pelo vazamento de dados) | `/user/<script>...</script>` executa JavaScript no navegador da vítima | Usar template Jinja2 (escape automático) ou `markupsafe.escape(nome)`; devolver só os campos necessários |
| 3 | `debug=True` com `host="0.0.0.0"`: console interativo (Werkzeug) exposto na rede, com stack traces detalhados | **A02 Security Misconfiguration** (também A10 pelo vazamento em erros) | Execução remota de código via debugger se o PIN for obtido; vazamento de código-fonte | `debug=False`, servidor WSGI (gunicorn) atrás de proxy, `host` restrito e handler de erro genérico |
| 4 | Segredo no código (`SENHA_DB = "123456"`), fraco e versionável no Git | **A02 Security Misconfiguration** / **A04 Cryptographic Failures** (segredo exposto, senha fraca) | Qualquer pessoa com acesso ao repositório obtém o acesso ao banco | `os.environ["SENHA_DB"]`, senha forte e rotacionada, gerenciador de segredos, `.env` no `.gitignore` |
| 5 | Sem logging de acessos e de erros | **A09 Security Logging & Alerting Failures** | Ataques como o do item 1 passam sem deixar rastro e sem alerta | `logging` com data, IP, método, rota e status em `after_request`, sanitizando quebras de linha; alerta para rajadas de 4xx/5xx |

## Falhas adicionais encontradas

- `fetchone()` pode devolver `None`, e `str(None)` mostraria "None" ao usuário: tratar com 404.
- Falta tratamento de exceções do banco (**A10 Mishandling of Exceptional Conditions**): uma falha de conexão derrubaria a rota com traceback (já visível por causa do `debug=True`).
- Sem autenticação nem controle de acesso na rota (**A01 Broken Access Control**): qualquer um consulta qualquer usuário.
- Faltam headers de segurança (CSP, X-Content-Type-Options, X-Frame-Options).

## Versão corrigida

```python
import logging, os
from flask import Flask, abort, render_template_string, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.after_request
def log_e_headers(resp):
    logging.info("%s %s -> %s", request.remote_addr, request.path.replace("\n", "?"), resp.status_code)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    return resp

@app.route("/user/<nome>")
@login_required                      # autenticação/autorização (A01)
def user(nome):
    try:
        cur.execute("SELECT id, nome FROM users WHERE nome=%s", (nome,))
        dados = cur.fetchone()
    except Exception:
        logging.exception("erro no banco")
        abort(503)
    if not dados:
        abort(404)
    return render_template_string("<h1>Bem-vindo {{ nome }}</h1>", nome=dados[1])   # escape automático

if __name__ == "__main__":
    app.run(debug=False)             # produção: gunicorn
# senha do banco: os.environ["SENHA_DB"]
```
