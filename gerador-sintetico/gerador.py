import random
import uuid
import os
from itertools import product as produto_cartesiano
import pandas as pd

CSV_DIR = os.path.join(os.path.dirname(__file__), "csv")

produtos = ["cartoes", "emprestimos", "pagamentos", "renegociacao"]
tipos_aceita_erro_sistema = ["estado", "evento"]
tempos_de_espera = ["ontem", "duas semanas atras", "alguns dias"]


def carregar_csv(nome_arquivo):
    return pd.read_csv(os.path.join(CSV_DIR, nome_arquivo)).to_dict("records")


def separar_tipos(tipos_texto):
    return tipos_texto.split("|")


def filtrar_por_produto(registros, produto):
    return [reg for reg in registros if reg["produto"] == produto]


mensagens_sistema = carregar_csv("mensagens_sistema.csv")
templates_por_produto = carregar_csv("templates_por_produto.csv")
problemas_por_produto = carregar_csv("problemas_por_produto.csv")
templates_sentimento = carregar_csv("templates_sentimento.csv")


def gerar_relato(template, problema, tempo, sentimento):
    relato_base = template['texto'].format(problema=problema['texto'], tempo=tempo)

    if sentimento['texto'].startswith("{relato}"):
        relato_formatado = relato_base
    else:
        relato_formatado = relato_base[0].lower() + relato_base[1:]

    return sentimento['texto'].format(relato=relato_formatado)


def sortear_erro_sistema(produto, tipo_problema):
    if tipo_problema not in tipos_aceita_erro_sistema or random.random() >= 0.2:
        return ""
    erros_compativeis = [
        erro for erro in filtrar_por_produto(mensagens_sistema, produto)
        if tipo_problema in separar_tipos(erro['tipos_aceitos'])
    ]
    if not erros_compativeis:
        return ""
    return f" O sistema apresentou: {random.choice(erros_compativeis)['texto']}."


def gerar_todas_combinacoes():
    combinacoes = []
    for produto in produtos:
        templates = filtrar_por_produto(templates_por_produto, produto)
        problemas = filtrar_por_produto(problemas_por_produto, produto)
        for template, problema, tempo, sentimento in produto_cartesiano(
            templates, problemas, tempos_de_espera, templates_sentimento
        ):
            if problema['tipo'] in separar_tipos(template['tipos_aceitos']):
                combinacoes.append((produto, template, problema, tempo, sentimento))
    return combinacoes


def montar_reclamacao(produto, template, problema, tempo, sentimento):
    texto = gerar_relato(template, problema, tempo, sentimento)
    texto += sortear_erro_sistema(produto, problema['tipo'])
    return {
        "id": uuid.uuid4(),
        "produto": produto,
        "tipo_problema": problema["tipo"],
        "impacto": problema["impacto"],
        "nivel_urgencia": problema["nivel_urgencia"],
        "relato": texto,
    }


if __name__ == "__main__":
    QUANTIDADE_DESEJADA = 10000

    combinacoes = gerar_todas_combinacoes()
    amostra = random.sample(combinacoes, k=QUANTIDADE_DESEJADA)
    reclamacoes = [montar_reclamacao(*combo) for combo in amostra]

    pd.DataFrame(reclamacoes).to_csv("reclamacoes.csv", index=False)
