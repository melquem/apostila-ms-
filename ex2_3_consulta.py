"""Exercício 2.3 — consultar(fonte, tipo, ip, desde) com filtro dinâmico."""
from datetime import datetime

import comum


def montar_filtro(fonte=None, tipo=None, ip=None, desde=None):
    """Só inclui no filtro os parâmetros diferentes de None."""
    filtro = {}
    if fonte is not None:
        filtro["fonte"] = fonte
    if tipo is not None:
        filtro["tipo"] = tipo
    if ip is not None:
        filtro["ip"] = ip
    if desde is not None:
        filtro["timestamp"] = {"$gte": desde}
    return filtro


def consultar(fonte=None, tipo=None, ip=None, desde=None, colecao=None):
    col = colecao if colecao is not None else comum.mongo_db().eventos
    return list(col.find(montar_filtro(fonte, tipo, ip, desde)).sort("timestamp", 1))


if __name__ == "__main__":
    falhas = consultar(tipo="FAIL", ip="185.220.101.1")
    print(f"FAIL de 185.220.101.1: {len(falhas)}")
    print(f"Eventos de auth: {len(consultar(fonte='auth'))}")
    print(f"Desde 10:00: {len(consultar(desde=datetime(2025, 2, 20, 10, 0)))}")
