"""Exercício 8.1 — Dashboard de alertas com defesa contra XSS.
Jinja2 escapa por padrão (render_template_string também). NUNCA use |safe nem Markup em dado do usuário."""
from flask import Flask, redirect, render_template_string, request

PAGINA = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Alertas</title></head><body>
<h1>Dashboard de alertas</h1>
<form method="post" action="/alertas"><input name="descricao" maxlength="300" placeholder="Descrição" required>
<button>Cadastrar</button></form>
<ul>{% for a in alertas %}<li>{{ a }}</li>{% else %}<li>Nenhum alerta</li>{% endfor %}</ul>
</body></html>"""


def create_app():
    app = Flask(__name__)
    alertas = []

    @app.after_request
    def headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Content-Security-Policy"] = "default-src 'self'"
        return resp

    @app.get("/")
    def index():
        return render_template_string(PAGINA, alertas=alertas)

    @app.post("/alertas")
    def cadastrar():
        desc = request.form.get("descricao", "").strip()[:300]
        if desc:
            alertas.append(desc)
        return redirect("/")

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)
