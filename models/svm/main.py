from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from models.base import treinar_e_avaliar


def criar_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LinearSVC(max_iter=2000, random_state=42)),
    ])


def criar_grid():
    return {
        "tfidf__max_features": [5000, 10000, 20000, None],
        "tfidf__ngram_range": [(1, 1), (1, 2), (1, 3)],
        "tfidf__min_df": [1, 2, 3],
        "tfidf__max_df": [0.85, 0.90, 0.95],
        "tfidf__sublinear_tf": [True, False],
        "clf__C": [0.01, 0.1, 1.0, 10.0],
        "clf__class_weight": [None, "balanced"],
        "clf__loss": ["hinge", "squared_hinge"],
    }


if __name__ == "__main__":
    treinar_e_avaliar(criar_pipeline(), criar_grid())
