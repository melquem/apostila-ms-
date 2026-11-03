"""Exercício 13.1 — Chatbot de segurança com histórico. /sair encerra.
Com OPENAI_API_KEY usa a API; sem chave usa um modo mock por palavras-chave (mesma interface)."""
import os

BASE = {
    "xss": ("Cross-Site Scripting é a injeção de JavaScript em páginas que outros usuários visualizam.",
            "Para prevenir XSS, escape toda saída (Jinja2 já faz isso), valide a entrada e use Content-Security-Policy."),
    "sql": ("SQL Injection é a inserção de comandos SQL por meio da entrada do usuário.",
            "Para prevenir SQL Injection, use queries parametrizadas e o menor privilégio no banco."),
    "phishing": ("Phishing é um golpe que imita uma entidade confiável para roubar credenciais ou dados.",
                 "Para se proteger do phishing, verifique o domínio do remetente, desconfie de urgência e use MFA."),
    "csrf": ("CSRF faz o navegador da vítima enviar requisições autenticadas sem que ela perceba.",
             "Para prevenir CSRF, use tokens anti-CSRF e cookies SameSite."),
}


def responder_mock(historico):
    """Escolhe o tópico da última pergunta; se ela for um seguimento ('e como prevenir?'), usa o contexto anterior."""
    usuario = [m["content"].lower() for m in historico if m["role"] == "user"]
    ultima = usuario[-1]
    topico = next((k for k in BASE if k in ultima), None)
    seguimento = any(p in ultima for p in ("prevenir", "evitar", "proteger", "defender"))
    if topico is None and seguimento:
        topico = next((k for msg in reversed(usuario[:-1]) for k in BASE if k in msg), None)
    if topico is None:
        return "Posso falar de XSS, SQL Injection, phishing e CSRF. Sobre qual você quer saber?"
    definicao, prevencao = BASE[topico]
    return prevencao if seguimento else definicao


def responder_openai(client, historico):
    r = client.chat.completions.create(model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
                                       messages=historico, temperature=0.3, max_tokens=300)
    return r.choices[0].message.content


def conversar(entrada=input, saida=print, client=None):
    historico = [{"role": "system", "content": "Você é um analista de segurança sênior. Responda em português, de forma curta."}]
    while True:
        try:
            pergunta = entrada("Você: ").strip()
        except EOFError:
            break
        if pergunta == "/sair":
            saida("Assistente: Até logo!")
            break
        if not pergunta:
            continue
        historico.append({"role": "user", "content": pergunta[:1000]})
        try:
            resposta = responder_openai(client, historico) if client else responder_mock(historico)
        except Exception:
            historico.pop()
            saida("Assistente: [erro] não consegui responder agora (API indisponível). Tente de novo.")
            continue
        historico.append({"role": "assistant", "content": resposta})
        saida(f"Assistente: {resposta}")


if __name__ == "__main__":
    from aula13.llm_comum import get_client
    cli = get_client()
    print("(modo OpenAI)" if cli else "(modo mock: defina OPENAI_API_KEY para usar a API)")
    conversar(client=cli)
