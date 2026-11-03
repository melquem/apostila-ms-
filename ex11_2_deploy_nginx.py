"""Exercício 11.2 — Deploy automatizado de Nginx na porta 8080 + verificação + limpeza."""
import socket
import sys
import time

import docker
import requests

PORTA, NOME = 8080, "nginx_deploy_lab"


def porta_em_uso(porta):
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", porta)) == 0


def main():
    if porta_em_uso(PORTA):
        print(f"Erro: porta {PORTA} em uso")
        return 1
    try:
        client = docker.from_env()
        print("Subindo Nginx...")
        container = client.containers.run("nginx:latest", detach=True, name=NOME, ports={"80/tcp": PORTA})
    except docker.errors.APIError as e:
        print(f"Erro: porta {PORTA} em uso" if "port is already allocated" in str(e).lower() or "address already in use" in str(e).lower()
              else "Erro ao subir o contêiner (nome já existe ou imagem indisponível?)")
        return 1
    except docker.errors.DockerException:
        print("Erro: não foi possível conectar ao Docker")
        return 1
    codigo = 0
    try:
        for _ in range(15):  # aguarda o Nginx responder (até ~15s)
            try:
                r = requests.get(f"http://localhost:{PORTA}", timeout=2)
                print(f"Nginx respondeu: {r.status_code} {r.reason}")
                break
            except requests.exceptions.RequestException:
                time.sleep(1)
        else:
            print("Erro: o Nginx não respondeu a tempo")
            codigo = 1
    finally:
        print("Derrubando e removendo contêiner...")
        container.stop()
        container.remove()
        print("Concluído. Ambiente limpo.")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
