"""Exercício 12.3 — Persistência com verificação de integridade (SHA-256)."""
import hashlib
import os

import joblib

from aula12.ex12_1_pipeline import X, criar_pipeline, y

ARQ = "modelo_seguranca.pkl"


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def salvar(modelo, caminho=ARQ):
    joblib.dump(modelo, caminho)
    h = sha256(caminho)
    with open(caminho + ".sha256", "w") as f:
        f.write(h)
    return h


def carregar_verificado(caminho=ARQ):
    """Verifica o hash ANTES de desserializar (pkl executa código ao ser carregado)."""
    esperado = open(caminho + ".sha256").read().strip()
    if sha256(caminho) != esperado:
        raise ValueError("ALERTA: arquivo do modelo foi modificado!")
    return joblib.load(caminho)


if __name__ == "__main__":
    modelo = criar_pipeline().fit(X, y)
    h = salvar(modelo)
    print(f"Modelo salvo: {ARQ}\nHash SHA-256: {h} ({len(h)} caracteres)")
    print("Recarregando e verificando integridade...")
    m2 = carregar_verificado()
    print("Hash confere: modelo íntegro. Previsão de teste:", m2.predict([[58000, 4444, 16.0]]).tolist())
    # Demonstração da adulteração
    with open(ARQ, "ab") as f:
        f.write(b"x")
    try:
        carregar_verificado()
    except ValueError as e:
        print(e)
    os.remove(ARQ); os.remove(ARQ + ".sha256")
