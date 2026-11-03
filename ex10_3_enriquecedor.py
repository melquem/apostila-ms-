"""Exercício 10.3 — Enriquecedor de IPs: cache (dict), backoff em 429, privado/público, relatório."""
import ipaddress
import time

import requests


def http_fetch(ip):
    """Retorna (status_code, json). Erros de rede viram (0, None)."""
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
        return r.status_code, (r.json() if r.status_code == 200 else None)
    except (requests.exceptions.RequestException, ValueError):
        return 0, None


def enriquecer_lista(ips, fetch=http_fetch, sleep=time.sleep, tentativas=3):
    cache, resumo, linhas = {}, {"http": 0, "cache": 0, "internos": 0, "erros": 0}, []
    for ip in ips:
        try:
            privado = ipaddress.ip_address(ip).is_private
        except ValueError:
            resumo["erros"] += 1
            linhas.append(f"{ip:15s} -> IP inválido")
            continue
        if privado:
            resumo["internos"] += 1
            linhas.append(f"{ip:15s} -> Rede Interna (não consultado)")
            continue
        if ip in cache:
            resumo["cache"] += 1
            linhas.append(f"{ip:15s} -> [CACHE] sem nova chamada HTTP")
            continue
        dados = None
        for i in range(tentativas):
            status, j = fetch(ip)
            resumo["http"] += 1
            if status == 429:
                sleep(2 ** i)  # backoff exponencial: 1s, 2s, 4s
                continue
            dados = j
            break
        if dados is None:
            resumo["erros"] += 1
            linhas.append(f"{ip:15s} -> falha na consulta")
            continue
        cache[ip] = dados
        linhas.append(f"{ip:15s} -> {dados.get('city', '?')} / {dados.get('country', '?')} / {dados.get('org', '?')} (EXTERNO)")
    return linhas, resumo


if __name__ == "__main__":
    ips = ["8.8.8.8", "1.1.1.1", "185.220.101.1", "192.168.1.10", "8.8.8.8"]
    linhas, r = enriquecer_lista(ips)
    print("\n".join(linhas))
    print(f"=== Resumo === Consultas HTTP: {r['http']} | Cache hits: {r['cache']} | Internos: {r['internos']} | Erros: {r['erros']}")
