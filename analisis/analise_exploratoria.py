import os
import pandas as pd
from matplotlib import pyplot as plt

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")

def distribuicao_target_bar(df, target, title, xlabel, ylabel):
    df[target].value_counts().sort_index().plot(kind='bar')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    nome_arquivo = f"distribuicao_{target}.png"
    plt.savefig(os.path.join(IMG_DIR, nome_arquivo), bbox_inches="tight")
    plt.close()

def distribuicao_target_crosstab(df, target1, target2, title, xlabel, ylabel):
    crosstab = pd.crosstab(df[target1], df[target2])
    crosstab.plot(kind='bar', stacked=True)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    nome_arquivo = f"crosstab_{target1}_{target2}.png"
    plt.savefig(os.path.join(IMG_DIR, nome_arquivo), bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    df = pd.read_csv("reclamacoes.csv")
    distribuicao_target_bar(df, 'nivel_urgencia', 'Distribuição do Nível de Urgência', 'Nível de Urgência', 'Quantidade de Relatos')
    distribuicao_target_bar(df, 'produto', 'Distribuição por Produto', 'Produto', 'Quantidade de Relatos')
    distribuicao_target_crosstab(df, 'produto', 'nivel_urgencia', 'Nível de Urgência por Produto', 'Produto', 'Quantidade de Relatos')
    distribuicao_target_crosstab(df, 'impacto', 'nivel_urgencia', 'Nível de Urgência por Impacto', 'Impacto', 'Quantidade de Relatos')
    print(f"Quantidade de dados nulos:\n{df.isnull().sum()}")
    print(f"Quantidade de dados duplicados:\n{df.duplicated().sum()}")