import pandas as pd
import time
import warnings
from datetime import timedelta

from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
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


if __name__ == "__main__":
    print("=" * 60)
    print("  TREINAMENTO RANDOM FOREST")
    print("=" * 60)

    df = pd.read_csv("relatos.csv", sep=";")
    print(f"Dataset: {len(df)} registros")
    print(f"Distribuicao:\n{df['urgencia'].value_counts().to_string()}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        df["relato"].values, df["urgencia"].values,
        test_size=0.2, random_state=42, stratify=df["urgencia"],
    )
    print(f"Treino: {len(X_train)} | Teste: {len(X_test)}")

    pipeline = criar_pipeline()
    grid = criar_grid()

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    total_combinacoes = 1
    for v in grid.values():
        total_combinacoes *= len(v)
    print(f"Combinacoes no grid: {total_combinacoes}")

    if total_combinacoes > 200:
        print(f"Grid grande, usando RandomizedSearchCV com 200 iteracoes")
        search = RandomizedSearchCV(
            pipeline, grid, n_iter=200, cv=cv,
            scoring="f1_macro", n_jobs=-1, random_state=42,
        )
    else:
        search = GridSearchCV(pipeline, grid, cv=cv, scoring="f1_macro", n_jobs=-1)

    inicio = time.time()
    search.fit(X_train, y_train)
    tempo = timedelta(seconds=int(time.time() - inicio))

    y_pred = search.predict(X_test)

    print(f"\nTempo: {tempo}")
    print(f"Melhor F1 macro (CV): {search.best_score_:.4f}")
    print(f"\nMelhores hiperparametros:")
    for param, val in sorted(search.best_params_.items()):
        print(f"  {param}: {val}")

    print(f"\nResultados no teste:")
    print(classification_report(y_test, y_pred, target_names=LABEL_NAMES))
