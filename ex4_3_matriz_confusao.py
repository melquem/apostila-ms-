"""Exercício 4.3 — Avaliação honesta com matriz de confusão."""
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

y_verdadeiro = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]  # 8 normais, 2 ataques
y_previsto = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]    # o modelo perdeu 1 ataque


def metricas(yv=y_verdadeiro, yp=y_previsto):
    return {"matriz": confusion_matrix(yv, yp).tolist(),
            "precisao": precision_score(yv, yp), "recall": recall_score(yv, yp),
            "f1": f1_score(yv, yp), "acuracia": accuracy_score(yv, yp)}


if __name__ == "__main__":
    m = metricas()
    print("Matriz:", m["matriz"], "  ([[VN, FP], [FN, VP]])")
    print(f"Precisão: {m['precisao']:.2f} | Recall: {m['recall']:.2f} | F1: {m['f1']:.2f} | Acurácia: {m['acuracia']:.2f}")
    print("""
Interpretação:
1. A acurácia de 90% parece ótima, mas é inflada pelas 8 amostras normais fáceis.
2. O recall de 0,50 mostra que METADE dos ataques reais passou despercebida (1 falso negativo).
3. Em segurança um falso negativo é um ataque em andamento sem alerta, muito pior que um falso
   positivo (alarme extra). Por isso, com classes desbalanceadas, recall importa mais que acurácia.""")
