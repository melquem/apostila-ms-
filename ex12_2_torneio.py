"""Exercício 12.2 — Torneio RandomForest x SVM x KNN + GridSearch no vencedor.
SVM e KNN dependem de escala, então todos entram num Pipeline com StandardScaler (comparação justa)."""
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from aula12.ex12_1_pipeline import X, y

CV = StratifiedKFold(5, shuffle=True, random_state=42)


def pipe(clf):
    return Pipeline([("scaler", StandardScaler()), ("clf", clf)])


def torneio():
    modelos = {"RandomForest": RandomForestClassifier(random_state=42), "SVM": SVC(), "KNN": KNeighborsClassifier(n_neighbors=3)}
    return {n: cross_val_score(pipe(m), X, y, cv=CV).mean() for n, m in modelos.items()}, modelos


if __name__ == "__main__":
    notas, modelos = torneio()
    for n, v in notas.items():
        print(f"{n:13s}: {v:.2f}")
    vencedor = max(notas, key=notas.get)  # empate: o primeiro na ordem do dicionário
    print("Vencedor:", vencedor)
    grade = {"clf__n_estimators": [50, 100, 200], "clf__max_depth": [None, 5, 10]} if vencedor == "RandomForest" else \
            {"clf__C": [0.1, 1, 10]} if vencedor == "SVM" else {"clf__n_neighbors": [1, 3, 5]}
    busca = GridSearchCV(pipe(modelos[vencedor]), grade, cv=CV).fit(X, y)
    print("Melhores parâmetros:", busca.best_params_)
    print(f"Melhor score: {busca.best_score_:.2f}")
