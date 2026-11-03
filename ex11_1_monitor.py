"""Exercício 11.1 — Monitor de contêineres (rodando e parados) em tabela alinhada. Requer Docker local."""
import docker


def coletar(client=None):
    client = client or docker.from_env()
    return [{"nome": c.name, "status": c.status, "imagem": (c.image.tags or [c.image.short_id])[0]}
            for c in client.containers.list(all=True)]


def imprimir(containers):
    print(f"{'NOME':16s}{'STATUS':10s}IMAGEM")
    for c in containers:
        aviso = "   <- ⚠️ PARADO" if c["status"] != "running" else ""
        print(f"{c['nome']:16s}{c['status']:10s}{c['imagem']}{aviso}")
    rodando = sum(c["status"] == "running" for c in containers)
    print(f"Total: {len(containers)} | Rodando: {rodando} | Parados: {len(containers) - rodando}")


if __name__ == "__main__":
    try:
        imprimir(coletar())
    except docker.errors.DockerException:
        print("Erro: não foi possível conectar ao Docker (o daemon está rodando?)")
