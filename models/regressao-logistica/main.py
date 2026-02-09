import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

from models.base import LABEL_NAMES, carregar_dados


def criar_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.9)),
        ("clf", LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs")),
    ])


def plotar_matriz_confusao(y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=LABEL_NAMES, yticklabels=LABEL_NAMES)
    plt.xlabel("Predito")
    plt.ylabel("Real")
    plt.title("Matriz de Confusao - TF-IDF + Regressao Logistica")
    plt.savefig("matriz_confusao.png")
    plt.close()


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = carregar_dados()

    modelo = criar_pipeline()
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    print(classification_report(y_test, y_pred, target_names=LABEL_NAMES))
    plotar_matriz_confusao(y_test, y_pred)
