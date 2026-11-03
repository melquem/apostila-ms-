"""Exercício 4.2 — Acessos anômalos com Isolation Forest."""
import numpy as np
from sklearn.ensemble import IsolationForest

# [hora_do_dia, tentativas_login, bytes_baixados]
acessos = np.array([
    [9, 1, 200], [10, 1, 500], [14, 2, 300], [11, 1, 250], [16, 1, 400],
    [3, 40, 900000], [10, 1, 350], [15, 2, 280], [2, 55, 800000],
])


def detectar(dados=acessos, contaminacao=0.25):
    return IsolationForest(contamination=contaminacao, random_state=42).fit_predict(dados)


if __name__ == "__main__":
    res = detectar()
    for i, (a, r) in enumerate(zip(acessos, res)):
        print(f"Amostra {i}: {a.tolist()} -> {'ANOMALIA' if r == -1 else 'Normal'}")
