import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

LABEL_NAMES = ["baixa", "media", "alta"]


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
    df = pd.read_csv("relatos.csv", sep=";")

    X_train, X_test, y_train, y_test = train_test_split(
        df["relato"].values, df["urgencia"].values,
        test_size=0.2, random_state=42, stratify=df["urgencia"],
    )

    modelo = criar_pipeline()
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    print(classification_report(y_test, y_pred, target_names=LABEL_NAMES))
    plotar_matriz_confusao(y_test, y_pred)
