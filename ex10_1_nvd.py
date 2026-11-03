"""Exercício 10.1 — Cliente da API do NVD (CVE: descrição, CVSS, severidade).
Uso: python -m aula10.ex10_1_nvd CVE-2021-44228      (NVD_API_KEY opcional, aumenta o rate limit)"""
import os
import re
import sys

import requests

URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
RE_CVE = re.compile(r"^CVE-\d{4}-\d{4,}$", re.I)


def extrair(vuln):
    """Extrai descrição, score e severidade do JSON do NVD (prefere CVSS v3.1 > v3.0 > v2)."""
    cve = vuln["cve"]
    desc = next((d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"), "(sem descrição)")
    score = sev = None
    for chave in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        m = cve.get("metrics", {}).get(chave)
        if m:
            score = m[0]["cvssData"]["baseScore"]
            sev = m[0]["cvssData"].get("baseSeverity") or m[0].get("baseSeverity")
            break
    return {"id": cve["id"], "cvss": score, "severidade": sev, "descricao": desc}


def buscar_cve(cve_id, get=requests.get):
    if not RE_CVE.match(cve_id or ""):
        return {"erro": "formato de CVE inválido (ex.: CVE-2021-44228)"}
    headers = {"apiKey": os.environ["NVD_API_KEY"]} if os.environ.get("NVD_API_KEY") else {}
    try:
        r = get(URL, params={"cveId": cve_id.upper()}, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        return {"erro": "tempo esgotado ao consultar o NVD"}
    except requests.exceptions.RequestException:
        return {"erro": "falha de conexão com o NVD"}
    if r.status_code in (403, 429):
        return {"erro": "limite de requisições do NVD atingido; aguarde ou use NVD_API_KEY"}
    if r.status_code == 404:
        return {"erro": "CVE não encontrada"}
    if r.status_code != 200:
        return {"erro": f"NVD respondeu {r.status_code}"}
    try:
        vulns = r.json().get("vulnerabilities", [])
    except ValueError:
        return {"erro": "resposta inválida do NVD"}
    return extrair(vulns[0]) if vulns else {"erro": "CVE não encontrada"}


if __name__ == "__main__":
    res = buscar_cve(sys.argv[1] if len(sys.argv) > 1 else "CVE-2021-44228")
    if "erro" in res:
        print(res["erro"])
    else:
        print(res["id"])
        print(f"  CVSS: {res['cvss']} ({res['severidade']})")
        print(f"  Descrição: {res['descricao'][:300]}")
