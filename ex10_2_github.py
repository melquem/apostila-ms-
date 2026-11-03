"""Exercício 10.2 — Explorador da API do GitHub (menu). Usa GITHUB_TOKEN se existir (opcional)."""
import json
import os
import re

import requests

BASE = "https://api.github.com"
RE_NOME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
RE_REPO = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


class ErroAPI(Exception):
    pass


def _get(url, params=None, get=requests.get):
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    try:
        r = get(url, params=params, headers=headers, timeout=15)
    except requests.exceptions.Timeout:
        raise ErroAPI("tempo esgotado")
    except requests.exceptions.RequestException:
        raise ErroAPI("falha de conexão")
    if r.status_code in (403, 429):
        raise ErroAPI("limite de requisições atingido (403/429). Tente mais tarde ou defina GITHUB_TOKEN")
    if r.status_code == 404:
        raise ErroAPI("não encontrado")
    if r.status_code != 200:
        raise ErroAPI(f"GitHub respondeu {r.status_code}")
    return r.json()


def buscar_usuario(nome, get=requests.get):
    if not RE_NOME.match(nome or ""):
        raise ErroAPI("nome de usuário inválido")
    return _get(f"{BASE}/users/{nome}", get=get)


def listar_repos(nome, get=requests.get, por_pagina=100, max_paginas=10):
    """Percorre as páginas até esvaziar (limite de segurança de max_paginas)."""
    if not RE_NOME.match(nome or ""):
        raise ErroAPI("nome de usuário inválido")
    repos = []
    for pagina in range(1, max_paginas + 1):
        lote = _get(f"{BASE}/users/{nome}/repos", {"page": pagina, "per_page": por_pagina}, get)
        if not lote:
            break
        repos.extend(lote)
        if len(lote) < por_pagina:
            break
    return repos


def detalhar_repo(nome, repo, get=requests.get):
    if not RE_NOME.match(nome or "") or not RE_REPO.match(repo or ""):
        raise ErroAPI("nome inválido")
    return _get(f"{BASE}/repos/{nome}/{repo}", get=get)


def salvar_json(dados, usuario):
    caminho = f"github_{usuario}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return caminho


def menu():
    ultimo = {"usuario": None, "dados": None}
    while True:
        print("\n(1) Buscar usuário (2) Listar repositórios (3) Detalhar repositório (4) Salvar JSON (5) Sair")
        op = input("Opção: ").strip()
        try:
            if op == "1":
                u = buscar_usuario(input("Usuário: ").strip())
                print(f"=== Perfil: {u['login']} ===\nNome: {u.get('name')} | Repos públicos: {u['public_repos']} | Seguidores: {u['followers']}")
                ultimo.update(usuario=u["login"], dados=u)
            elif op == "2":
                nome = input("Usuário: ").strip()
                repos = sorted(listar_repos(nome), key=lambda r: r["stargazers_count"], reverse=True)
                print("=== Repositórios ===")
                for i, r in enumerate(repos, 1):
                    print(f"{i}. {r['name']:25s} ★ {r['stargazers_count']:<7} ({r.get('language')})")
                ultimo.update(usuario=nome, dados=repos)
            elif op == "3":
                r = detalhar_repo(input("Usuário: ").strip(), input("Repositório: ").strip())
                print(f"{r['full_name']} | ★ {r['stargazers_count']} | forks {r['forks_count']} | {r.get('description')}")
                ultimo.update(usuario=r["owner"]["login"], dados=r)
            elif op == "4":
                if ultimo["dados"] is None:
                    print("Nada para salvar ainda")
                else:
                    print("Resultados salvos em", salvar_json(ultimo["dados"], ultimo["usuario"]))
            elif op == "5":
                break
            else:
                print("Opção inválida")
        except ErroAPI as e:
            print("Erro:", e)


if __name__ == "__main__":
    menu()
