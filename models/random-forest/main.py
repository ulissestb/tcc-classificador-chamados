from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from models.base import treinar_e_avaliar


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
    treinar_e_avaliar(criar_pipeline(), criar_grid())
