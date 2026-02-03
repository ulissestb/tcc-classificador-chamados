import random
import uuid
import pandas as pd

produtos = ["cartoes", "emprestimos", "pagamentos", "renegociacao"]

mensagens_sistema = [
    "nenhuma oferta disponível",
    "tente novamente mais tarde",
    "serviço indisponível no momento",
    "erro inesperado",
    "falha temporária no sistema",
    "operação indisponível",
]


templates_por_produto = {
    "cartoes": [
        {
            "texto": "Estou com um problema no meu cartão, pois ocorreu {problema} e não consigo utilizá-lo normalmente.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Desde {tempo}, meu cartão apresenta {problema} e não tive retorno do banco.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Ao tentar realizar uma compra, identifiquei {problema} no cartão.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Meu cartão apresentou {problema} recentemente e isso está me prejudicando.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Estou enfrentando dificuldades com meu cartão devido a {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Já tentei resolver, mas o cartão continua com {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "O cartão ficou indisponível após ocorrer {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Identifiquei {problema} no cartão e preciso de uma solução.",
            "tipos_aceitos": ["estado", "evento", "acao_errada"],
        },
        {
            "texto": "Meu cartão está com {problema} e não consigo fazer compras.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Desde {tempo}, o cartão vem apresentando {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Estou insatisfeito, pois meu cartão apresentou {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "O banco ainda não resolveu o {problema} do meu cartão.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Após uma tentativa de uso, o cartão passou a apresentar {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Não consigo utilizar meu cartão corretamente por causa de {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Meu cartão apresentou {problema} sem aviso prévio.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Estou aguardando solução para {problema} relacionado ao cartão.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O cartão apresentou erro recorrente de {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Desde {tempo}, tento resolver {problema} no cartão sem sucesso.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O cartão está com {problema} e o atendimento não solucionou.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Meu cartão apresentou {problema} e isso gerou transtornos.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Identifiquei {problema} ao tentar utilizar o cartão.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "O cartão não está funcionando corretamente devido a {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Preciso de ajuda para resolver {problema} no cartão.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Estou tendo problemas frequentes no cartão relacionados a {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Solicito a regularização do {problema} apresentado no cartão.",
            "tipos_aceitos": ["acao_errada"],
        },
    ],
    "emprestimos": [
        {
            "texto": "Estou enfrentando um problema no meu empréstimo, pois ocorreu {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Desde {tempo}, meu empréstimo apresenta {problema} e não foi resolvido.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Ao consultar meu empréstimo, identifiquei {problema}.",
            "tipos_aceitos": ["estado", "evento", "acao_errada"],
        },
        {
            "texto": "Meu empréstimo apresentou {problema} e isso está me causando dificuldades.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "O valor do empréstimo está incorreto devido a {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Estou com dificuldades para lidar com o empréstimo por causa de {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Já tentei contato, mas o problema de {problema} no empréstimo persiste.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O empréstimo apresenta inconsistências relacionadas a {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Desde a contratação, percebi {problema} no empréstimo.",
            "tipos_aceitos": ["estado", "evento"],
        },
        {
            "texto": "Meu empréstimo foi afetado por {problema} sem explicação clara.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Identifiquei {problema} no contrato do empréstimo.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "O banco ainda não solucionou {problema} referente ao empréstimo.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O empréstimo gerou transtornos devido a {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Estou aguardando retorno sobre {problema} no empréstimo.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Não consigo obter informações corretas por causa de {problema} no empréstimo.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O empréstimo apresentou erro relacionado a {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Meu empréstimo está com status incorreto devido a {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Estou insatisfeito com o empréstimo, pois ocorreu {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Preciso de esclarecimentos sobre {problema} no empréstimo.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Solicito uma solução para {problema} relacionado ao empréstimo.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "O empréstimo apresentou falhas causadas por {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Identifiquei {problema} ao tentar acompanhar o empréstimo.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "O empréstimo não está conforme o contratado por causa de {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Meu empréstimo está gerando dificuldades devido a {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Peço a regularização do {problema} no meu empréstimo.",
            "tipos_aceitos": ["acao_errada"],
        },
    ],
    "pagamentos": [
        {
            "texto": "Estou com um problema em um pagamento, pois ocorreu {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Desde {tempo}, um pagamento apresenta {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Ao realizar um pagamento, identifiquei {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Meu pagamento não foi concluído corretamente devido a {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "O pagamento apresentou {problema} e não foi regularizado.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Estou enfrentando dificuldades em pagamentos por causa de {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Já tentei resolver, mas o pagamento continua com {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "O sistema registrou {problema} em um pagamento recente.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Desde {tempo}, aguardo solução para {problema} no pagamento.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "O pagamento não foi processado corretamente por causa de {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Houve erro no pagamento relacionado a {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "O valor do pagamento está incorreto devido a {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "O pagamento foi afetado por {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Estou insatisfeito com o pagamento, pois ocorreu {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "O banco ainda não resolveu {problema} em um pagamento.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Identifiquei {problema} ao consultar um pagamento realizado.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Não consigo realizar pagamentos normalmente por causa de {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "O pagamento apresentou falhas recorrentes de {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Houve atraso no pagamento devido a {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "O pagamento gerou transtornos por conta de {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Estou aguardando retorno sobre {problema} em um pagamento.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "O pagamento não foi compensado corretamente devido a {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Preciso de ajuda para resolver {problema} em um pagamento.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O pagamento apresentou inconsistência relacionada a {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Solicito esclarecimentos sobre {problema} em um pagamento.",
            "tipos_aceitos": ["estado"],
        },
    ],
    "renegociacao": [
        {
            "texto": "Estou tentando renegociar minha dívida, mas ocorreu {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Desde {tempo}, percebi {problema} na renegociação solicitada.",
            "tipos_aceitos": ["estado", "evento"],
        },
        {
            "texto": "A renegociação apresenta {problema} e não consigo prosseguir.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Solicitei a renegociação, porém houve {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Estou enfrentando dificuldades na renegociação devido a {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O processo de renegociação está com {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Identifiquei {problema} ao tentar renegociar minha dívida.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "A renegociação não ocorreu corretamente por causa de {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "O valor apresentado na renegociação está incorreto devido a {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Desde {tempo}, aguardo solução para {problema} na renegociação.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "A renegociação foi afetada por {problema}.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "Não obtive retorno do banco sobre {problema} na renegociação.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Estou insatisfeito com a renegociação por conta de {problema}.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "O banco não resolveu {problema} relacionado à renegociação.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "A renegociação apresentou falhas relacionadas a {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Preciso de ajuda para resolver {problema} na renegociação.",
            "tipos_aceitos": ["estado", "acao_errada"],
        },
        {
            "texto": "Identifiquei {problema} após concluir a renegociação.",
            "tipos_aceitos": ["evento"],
        },
        {
            "texto": "A renegociação não refletiu corretamente por causa de {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Houve inconsistência na renegociação devido a {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "O processo de renegociação está parado por conta de {problema}.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "A renegociação gerou transtornos em função de {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "Solicitei renegociação, mas encontrei {problema}.",
            "tipos_aceitos": ["evento", "acao_errada"],
        },
        {
            "texto": "O acordo de renegociação apresenta {problema}.",
            "tipos_aceitos": ["acao_errada"],
        },
        {
            "texto": "Desde {tempo}, tento resolver {problema} na renegociação.",
            "tipos_aceitos": ["estado"],
        },
        {
            "texto": "Solicito a correção do {problema} identificado na renegociação.",
            "tipos_aceitos": ["acao_errada"],
        },
    ],
}

problemas_por_produto = {
    "cartoes": [
        {"texto": "cartão bloqueado", "tipo": "estado"},
        {"texto": "limite incorreto", "tipo": "estado"},
        {"texto": "cartão recusado", "tipo": "evento"},
        {"texto": "compra não reconhecida", "tipo": "evento"},
        {"texto": "lançamento não autorizado", "tipo": "evento"},
        {"texto": "bloqueio indevido do cartão", "tipo": "acao_errada"},
        {"texto": "cobrança indevida", "tipo": "acao_errada"},
        {"texto": "pagamento duplicado no cartão", "tipo": "acao_errada"},
        {"texto": "estorno não realizado", "tipo": "acao_errada"},
    ],
    "emprestimos": [
        {"texto": "empréstimo não liberado", "tipo": "estado"},
        {"texto": "saldo devedor incorreto", "tipo": "estado"},
        {"texto": "erro no contrato do empréstimo", "tipo": "evento"},
        {"texto": "cobrança antes do vencimento", "tipo": "evento"},
        {"texto": "valor do empréstimo incorreto", "tipo": "acao_errada"},
        {"texto": "juros acima do contratado", "tipo": "acao_errada"},
        {"texto": "parcelas divergentes", "tipo": "acao_errada"},
        {"texto": "desconto indevido", "tipo": "acao_errada"},
    ],
    "pagamentos": [
        {"texto": "pagamento pendente", "tipo": "estado"},
        {"texto": "pagamento realizado e não compensado", "tipo": "estado"},
        {"texto": "pagamento não processado", "tipo": "evento"},
        {"texto": "falha na confirmação do pagamento", "tipo": "evento"},
        {"texto": "pagamento duplicado", "tipo": "acao_errada"},
        {"texto": "cobrança duplicada", "tipo": "acao_errada"},
        {"texto": "erro no estorno do pagamento", "tipo": "acao_errada"},
        {"texto": "pagamento para destinatário errado", "tipo": "acao_errada"},
    ],
    "renegociacao": [
        {"texto": "parcelamento não registrado", "tipo": "estado"},
        {"texto": "dívida renegociada ainda constando em aberto", "tipo": "estado"},
        {"texto": "renegociação não aplicada", "tipo": "evento"},
        {"texto": "renegociação cancelada sem aviso", "tipo": "evento"},
        {"texto": "pagamento da renegociação não reconhecido", "tipo": "evento"},
        {"texto": "proposta de renegociação incorreta", "tipo": "acao_errada"},
        {"texto": "valor renegociado divergente", "tipo": "acao_errada"},
        {"texto": "condições divergentes da proposta", "tipo": "acao_errada"},
    ],
}

tempos_de_espera = ["ontem", "duas semanas atras", "alguns dias"]


if __name__ == "__main__":
    reclamacoes = []
    for i in range(0, 10000):
        produto = random.choice(produtos)
        problema = random.choice(problemas_por_produto[produto])
        tempo = random.choice(tempos_de_espera)
        template = random.choice(templates_por_produto[produto])
        
        if problema['tipo'] not in template['tipos_aceitos']:
            continue
        
        texto = template['texto'].format(problema=problema['texto'], tempo=tempo)
        
        if random.random() < 0.2:
            texto = f"{texto} aparecendo o erro {random.choice(mensagens_sistema)}"

        reclamacoes.append({"id": uuid.uuid4(), "produto": produto, "relato": texto})

    pd.DataFrame(reclamacoes).to_csv("reclamacoes.csv")
