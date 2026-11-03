"""Exercício 12.1 — Pipeline (StandardScaler + RandomForest) com validação cruzada de 5 folds."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X = np.array([
    [500, 80, 0.1], [1200, 80, 0.5], [64, 22, 0.02], [64000, 4444, 10.0], [45000, 8080, 15.0],
    [60000, 31337, 20.0], [800, 443, 0.3], [300, 53, 0.05], [55000, 9999, 18.0], [200, 25, 0.2],
    [700, 443, 0.2], [52000, 6666, 17.0], [150, 53, 0.03], [58000, 4444, 19.0], [900, 80, 0.4],
])
y = np.array([0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0])


def criar_pipeline():
    return Pipeline([("scaler", StandardScaler()),
                     ("clf", RandomForestClassifier(n_estimators=100, random_state=42))])


if __name__ == "__main__":
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    s = cross_val_score(criar_pipeline(), X, y, cv=cv)
    print(f"Scores por fold: {np.round(s, 2).tolist()}")
    print(f"Acurácia: {s.mean():.2f} (+/- {s.std():.2f})")
