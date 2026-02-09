import time
import warnings
from datetime import timedelta

import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)

warnings.filterwarnings("ignore")

LABEL_NAMES = ["baixa", "media", "alta"]
LABEL_MAP = {"baixa": 0, "media": 1, "alta": 2}


def carregar_dados(caminho="relatos.csv", test_size=0.2, random_state=42):
    df = pd.read_csv(caminho, sep=";")
    return train_test_split(
        df["relato"].values, df["urgencia"].values,
        test_size=test_size, random_state=random_state, stratify=df["urgencia"],
    )


def executar_grid_search(pipeline, grid, X_train, y_train, max_iter=200):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    total_combinacoes = 1
    for v in grid.values():
        total_combinacoes *= len(v)

    if total_combinacoes > max_iter:
        search = RandomizedSearchCV(
            pipeline, grid, n_iter=max_iter, cv=cv,
            scoring="f1_macro", n_jobs=-1, random_state=42,
        )
    else:
        search = GridSearchCV(pipeline, grid, cv=cv, scoring="f1_macro", n_jobs=-1)

    inicio = time.time()
    search.fit(X_train, y_train)
    tempo = timedelta(seconds=int(time.time() - inicio))

    return search, tempo


def treinar_e_avaliar(pipeline, grid, max_iter=200):
    X_train, X_test, y_train, y_test = carregar_dados()
    search, tempo = executar_grid_search(pipeline, grid, X_train, y_train, max_iter)
    y_pred = search.predict(X_test)

    print(f"Tempo: {tempo} | Melhor F1 macro (CV): {search.best_score_:.4f}\n")
    print(classification_report(y_test, y_pred, target_names=LABEL_NAMES))
