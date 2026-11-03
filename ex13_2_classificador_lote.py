"""Exercício 13.2 — Classificação em lote de logs (LLM com fallback por regras).
Uso: python -m aula13.ex13_2_classificador_lote [arquivo_de_logs.txt]"""
import sys
from collections import Counter

from aula13.llm_comum import classificar, get_client

LOGS = [
    "GET /index.html ip=192.168.1.10 status=200",
    "GET /../../etc/passwd ip=91.240.118.172 status=400",
    "POST /login ip=185.220.101.1 status=401 (5x seguidas)",
]


def processar(logs, client=None):
    contagem, linhas = Counter(), []
    for log in logs:
        rotulo, motivo, origem = classificar(log, client)
        contagem[rotulo] += 1
        linhas.append(f"[{rotulo}]".ljust(11) + f" {log}  ({motivo}; {origem})")
    return linhas, contagem


if __name__ == "__main__":
    logs = open(sys.argv[1], encoding="utf-8").read().splitlines() if len(sys.argv) > 1 else LOGS
    linhas, c = processar([l for l in logs if l.strip()], get_client())
    print("\n".join(linhas))
    print(f"=== Resumo === NORMAL:{c['NORMAL']} | SUSPEITO:{c['SUSPEITO']} | CRITICO:{c['CRITICO']}")
