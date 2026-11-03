"""Exercício 2.2 — Ingestão do auth.log no MongoDB + top IPs por falhas.
Formato: 2025-02-20 08:15:01 FAIL usuario=admin ip=185.220.101.1
Execução: python -m aula02.ex2_2_ingestao_auth [caminho_do_log]
"""
import sys
from datetime import datetime

import comum


def parse_linha(linha):
    """Normaliza uma linha em documento. Retorna None se malformada."""
    p = linha.split()
    if len(p) != 5 or not p[3].startswith("usuario=") or not p[4].startswith("ip="):
        return None
    try:
        ts = datetime.strptime(f"{p[0]} {p[1]}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return {"timestamp": ts, "fonte": "auth", "tipo": p[2], "ip": p[4][3:],
            "detalhes": {"usuario": p[3][8:]}}


def ler_log(caminho):
    docs = []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if linha.strip():
                d = parse_linha(linha)
                if d:
                    docs.append(d)
    return docs


PIPELINE_TOP_FAILS = [
    {"$match": {"tipo": "FAIL"}},
    {"$group": {"_id": "$ip", "total": {"$sum": 1}}},
    {"$sort": {"total": -1}},
    {"$limit": 5},
]


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "dados/auth.log"
    col = comum.mongo_db().eventos
    col.create_index("ip")
    docs = ler_log(caminho)
    col.insert_many(docs)
    print("=== Top IPs por falhas de login ===")
    for linha in col.aggregate(PIPELINE_TOP_FAILS):
        print(f"{linha['_id']} -> {linha['total']} falhas")
    print(f"Total de eventos inseridos: {len(docs)}")
