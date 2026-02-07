import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.metrics import classification_report, confusion_matrix


def pipeline():
    return Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=3,
            max_df=0.9
        )),
        ('clf', LogisticRegression(
            max_iter=1000,
            multi_class='multinomial',
            solver='lbfgs'
        ))
    ])

def plot_result(y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=[1, 2, 3],
                yticklabels=[1, 2, 3])
    plt.xlabel('Predito')
    plt.ylabel('Real')
    plt.title('Matriz de Confusão - TF-IDF + Regressão Logística')
    #TODO: Salvar a imagem da matriz de confusão
    plt.show()
    
if __name__ == "__main__":
    df = pd.read_csv("reclamacoes.csv")
    X = df['relato']
    y = df['nivel_urgencia']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = pipeline()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print(classification_report(y_test, y_pred))
    plot_result(y_test, y_pred)