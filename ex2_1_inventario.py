"""Exercício 2.1 — CRUD de inventário de ativos no MongoDB (menu).
Execução: python -m aula02.ex2_1_inventario   (precisa de MongoDB; MONGO_URI opcional)
"""
from pymongo.errors import DuplicateKeyError

import comum

ATIVOS_INICIAIS = [
    {"nome": "SRV-WEB01", "tipo": "servidor", "ip": "192.168.1.10", "status": "ativo"},
    {"nome": "PC-RH03",   "tipo": "estacao",  "ip": "192.168.1.45", "status": "ativo"},
    {"nome": "SW-CORE01", "tipo": "switch",   "ip": "192.168.1.1",  "status": "inativo"},
]


def preparar(col):
    col.create_index("ip", unique=True)  # impede IPs duplicados
    for a in ATIVOS_INICIAIS:
        try:
            col.insert_one(dict(a))
        except DuplicateKeyError:
            pass


def cadastrar(col, nome, tipo, ip, status="ativo"):
    try:
        col.insert_one({"nome": nome, "tipo": tipo, "ip": ip, "status": status})
        return "Ativo cadastrado!"
    except DuplicateKeyError:
        return "Erro: IP já cadastrado!"


def listar(col):
    docs = list(col.find({}, {"_id": 0}))
    print(f"{'NOME':12s} {'TIPO':10s} {'IP':15s} STATUS")
    for d in docs:
        print(f"{d['nome']:12s} {d['tipo']:10s} {d['ip']:15s} {d['status']}")
    return docs


def buscar_por_ip(col, ip):
    return col.find_one({"ip": ip}, {"_id": 0})


def atualizar_status(col, ip, status):
    r = col.update_one({"ip": ip}, {"$set": {"status": status}})
    return "Status atualizado!" if r.matched_count else "Erro: IP não encontrado"


def remover(col, ip):
    return "Ativo removido!" if col.delete_one({"ip": ip}).deleted_count else "Erro: IP não encontrado"


def menu(col):
    while True:
        print("\n[1] Cadastrar  [2] Listar  [3] Buscar por IP  [4] Atualizar status  [5] Remover  [6] Sair")
        op = input("Opção: ").strip()
        if op == "1":
            print(cadastrar(col, input("Nome: "), input("Tipo: "), input("IP: ").strip()))
        elif op == "2":
            listar(col)
        elif op == "3":
            print(buscar_por_ip(col, input("IP: ").strip()) or "Não encontrado")
        elif op == "4":
            print(atualizar_status(col, input("IP: ").strip(), input("Novo status: ").strip()))
        elif op == "5":
            print(remover(col, input("IP: ").strip()))
        elif op == "6":
            break
        else:
            print("Opção inválida")


if __name__ == "__main__":
    colecao = comum.mongo_db().ativos
    preparar(colecao)
    menu(colecao)
