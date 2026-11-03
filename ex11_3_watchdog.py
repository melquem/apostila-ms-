"""Exercício 11.3 — Watchdog: confere a cada 10 s, alerta e reinicia o contêiner se parar.
Uso: python -m aula11.ex11_3_watchdog [nome_do_container] [iteracoes]"""
import sys
import time
from datetime import datetime

import docker


def verificar(container, agora=datetime.now):
    """Retorna a linha de log e reinicia o contêiner se necessário."""
    container.reload()  # sem reload() o status ficaria desatualizado
    ts = agora().strftime("%H:%M:%S")
    if container.status == "running":
        return f"[{ts}] {container.name}: running — OK"
    msg = f"[{ts}] {container.name}: {container.status} — ⚠️ ALERTA! Tentando reiniciar..."
    try:
        container.restart()
        return msg + f"\n[{agora().strftime('%H:%M:%S')}] {container.name} reiniciado com sucesso."
    except docker.errors.APIError:
        return msg + "\nFalha ao reiniciar."


def main(nome="web_lab", iteracoes=6, intervalo=10):
    client = docker.from_env()
    try:
        container = client.containers.get(nome)
    except docker.errors.NotFound:
        print(f"Erro: contêiner '{nome}' não existe")
        return
    for i in range(iteracoes):
        print(verificar(container))
        if i < iteracoes - 1:
            time.sleep(intervalo)


if __name__ == "__main__":
    main(*(sys.argv[1:2] or ["web_lab"]), *(int(x) for x in sys.argv[2:3]))
