import os
import pandas as pd
import matplotlib.pyplot as plt

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def salvar_grafico(nome_arquivo):
    plt.savefig(os.path.join(IMG_DIR, nome_arquivo), bbox_inches="tight")
    plt.close()


def distribuicao_bar(df, coluna, titulo, xlabel, ylabel):
    df[coluna].value_counts().sort_index().plot(kind="bar")
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    salvar_grafico(f"distribuicao_{coluna}.png")


def crosstab_bar(df, coluna1, coluna2, titulo, xlabel, ylabel):
    pd.crosstab(df[coluna1], df[coluna2]).plot(kind="bar", stacked=True)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(title=coluna2)
    salvar_grafico(f"crosstab_{coluna1}_{coluna2}.png")


def distribuicao_comprimento(df, coluna_texto, titulo, xlabel, ylabel):
    df[coluna_texto].str.len().plot(kind="hist", bins=50)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    salvar_grafico("distribuicao_comprimento_relato.png")


if __name__ == "__main__":
    df = pd.read_csv("relatos.csv", sep=";")

    distribuicao_bar(df, "urgencia", "Distribuicao de Urgencia", "Urgencia", "Quantidade")
    distribuicao_bar(df, "area", "Distribuicao por Area", "Area", "Quantidade")
    crosstab_bar(df, "area", "urgencia", "Urgencia por Area", "Area", "Quantidade")
    distribuicao_comprimento(df, "relato", "Comprimento dos Relatos", "Caracteres", "Frequencia")

    print(f"Graficos salvos em {IMG_DIR}")
    print(f"Nulos: {df.isnull().sum().sum()} | Duplicados: {df.duplicated().sum()} | Unicos: {df['relato'].nunique()}/{len(df)}")
