import time
import warnings
from datetime import timedelta

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

LABEL_NAMES = ["baixa", "media", "alta"]


def criar_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", RandomForestClassifier(random_state=42)),
    ])


def criar_grid():
    return {
        "tfidf__max_features": [5000, 10000, 20000],
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "tfidf__min_df": [2, 3],
        "tfidf__max_df": [0.90, 0.95],
        "tfidf__sublinear_tf": [True],
        "clf__n_estimators": [100, 200, 300],
        "clf__max_depth": [None, 50, 100],
        "clf__min_samples_split": [2, 5],
        "clf__class_weight": [None, "balanced"],
    }


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


if __name__ == "__main__":
    df = pd.read_csv("relatos.csv", sep=";")

    X_train, X_test, y_train, y_test = train_test_split(
        df["relato"].values, df["urgencia"].values,
        test_size=0.2, random_state=42, stratify=df["urgencia"],
    )

    search, tempo = executar_grid_search(criar_pipeline(), criar_grid(), X_train, y_train)
    y_pred = search.predict(X_test)

    print(f"Tempo: {tempo} | Melhor F1 macro (CV): {search.best_score_:.4f}\n")
    print(classification_report(y_test, y_pred, target_names=LABEL_NAMES))
