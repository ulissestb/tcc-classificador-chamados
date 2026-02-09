import random
import re
import csv
import os
from dataclasses import dataclass
from collections import Counter, defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

AREAS = ["pix", "cartao", "conta", "emprestimo", "investimento", "atendimento", "seguranca", "cadastro"]
URGENCIAS = ["baixa", "media", "alta"]


def carregar_cenarios(caminho=None):
    caminho = caminho or os.path.join(SCRIPT_DIR, "csv/cenarios.csv")
    cenarios = []
    with open(caminho, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cenarios.append({
                "area": row["area"].strip(),
                "urgencias": {
                    "baixa": float(row["urgencia_baixa"]),
                    "media": float(row["urgencia_media"]),
                    "alta": float(row["urgencia_alta"]),
                },
                "slots": [
                    [s.strip() for s in row["slot_1"].split("|") if s.strip()],
                    [s.strip() for s in row["slot_2"].split("|") if s.strip()],
                ],
            })
    return cenarios


def carregar_complementos(caminho=None):
    caminho = caminho or os.path.join(SCRIPT_DIR, "csv/complementos.csv")
    dados = defaultdict(lambda: defaultdict(list))

    with open(caminho, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tipo = row["tipo"].strip()
            chave = row["chave"].strip()
            valor = row["valor"]

            if tipo in ("saudacao", "fechamento", "complemento_compartilhado"):
                dados[tipo]["_all"].append(valor)
            elif tipo in ("complemento_urgencia", "cross_area"):
                dados[tipo][chave].append(valor)
            else:
                dados[tipo]["_all"].append(valor.strip())

    return dict(dados)


def gerar_valor(faixa="medio"):
    faixas = {
        "pequeno": (10, 150), "medio": (150, 3000),
        "grande": (3000, 30000), "muito_grande": (30000, 200000),
    }
    mi, ma = faixas.get(faixa, faixas["medio"])
    v = round(random.uniform(mi, ma), 2)
    return random.choice([
        f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"R${v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"R$ {v:.0f}",
        f"{v:.0f} reais",
    ])


def preencher(texto, comp):
    nomes = comp.get("nome", {}).get("_all", ["João"])
    lojas = comp.get("loja", {}).get("_all", ["uma loja"])
    investimentos = comp.get("investimento", {}).get("_all", ["CDB"])
    tempos = comp.get("tempo", {}).get("_all", ["ontem"])
    erros = comp.get("erro", {}).get("_all", ["erro desconhecido"])

    v1 = gerar_valor(random.choice(["pequeno", "medio", "grande"]))
    v2 = gerar_valor(random.choice(["pequeno", "medio"]))

    texto = texto.replace("{valor}", v1, 1)
    texto = texto.replace("{valor2}", v2, 1)
    texto = texto.replace("{valor}", v1)
    texto = texto.replace("{nome}", random.choice(nomes))
    texto = texto.replace("{loja}", random.choice(lojas), 1)
    texto = texto.replace("{loja2}", random.choice(lojas))
    texto = texto.replace("{loja}", random.choice(lojas))
    texto = texto.replace("{investimento}", random.choice(investimentos))
    texto = texto.replace("{tempo}", random.choice(tempos))
    texto = texto.replace("{4digitos}", f"{random.randint(1000, 9999)}")
    texto = texto.replace("{nparcelas}", str(random.randint(3, 48)))
    texto = texto.replace("{taxa}", f"{random.uniform(0.8, 4.5):.1f}")
    texto = texto.replace("{taxa2}", f"{random.uniform(0.5, 3.0):.1f}")
    texto = texto.replace("{protocolo}", f"{random.randint(100000000, 999999999)}")
    texto = texto.replace("{nchamados}", str(random.randint(2, 8)))
    texto = texto.replace("{erro}", random.choice(erros))
    texto = texto.replace("{dias_uteis}", str(random.choice([3, 5, 7, 10, 15])))

    return texto


@dataclass
class Estilo:
    nome: str
    usa_saudacao: float
    usa_fechamento: float
    usa_complemento_urgencia: float
    usa_complemento_compartilhado: float
    intensidade_ruido: float
    usa_cross: float


ESTILOS = [
    Estilo("formal",      0.85, 0.85, 0.45, 0.00, 0.05, 0.02),
    Estilo("informal",    0.35, 0.25, 0.40, 0.00, 0.45, 0.03),
    Estilo("telegrafico", 0.05, 0.05, 0.30, 0.00, 0.25, 0.01),
    Estilo("prolixo",     0.75, 0.75, 0.55, 0.00, 0.15, 0.05),
    Estilo("irritado",    0.10, 0.15, 0.50, 0.00, 0.35, 0.03),
]

ABREVIACOES = {
    "você": ["vc", "voce"], "porque": ["pq"], "também": ["tb", "tbm"],
    "não": ["nao", "ñ"], "está": ["tá", "ta"], "estou": ["tô", "to"],
    "para": ["pra"], "que": ["q"], "de": ["d"], "muito": ["mt"],
}


def aplicar_ruido(texto, intensidade=0.3):
    if random.random() > intensidade:
        return texto

    if random.random() < 0.5:
        palavras = texto.split()
        aplicadas = 0
        for i, p in enumerate(palavras):
            pl = p.lower().rstrip(".,!?;:")
            if pl in ABREVIACOES and aplicadas < 2 and random.random() < 0.4:
                suf = p[len(pl):]
                palavras[i] = random.choice(ABREVIACOES[pl]) + suf
                aplicadas += 1
        texto = " ".join(palavras)

    if random.random() < 0.15:
        for ac, sem in {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','ç':'c'}.items():
            if random.random() < 0.25:
                texto = texto.replace(ac, sem)

    if random.random() < 0.12:
        texto = texto.lower()
    elif random.random() < 0.05:
        texto = texto.upper()

    return texto


def escolher_complemento(comp, tipo, chave, probabilidade):
    if random.random() >= probabilidade:
        return None
    opcoes = comp.get(tipo, {}).get(chave, [])
    if not opcoes:
        return None
    escolha = random.choice(opcoes)
    return escolha if escolha.strip() else None


def gerar_relato(cenarios, comp, area=None, urgencia=None):
    if area is None:
        area = random.choice(AREAS)

    cenarios_area = [c for c in cenarios if c["area"] == area]
    cenario = random.choice(cenarios_area)

    if urgencia is None:
        urgs = [(u, p) for u, p in cenario["urgencias"].items() if p > 0]
        us, ps = zip(*urgs)
        urgencia = random.choices(us, weights=ps, k=1)[0]

    partes_cenario = [random.choice(slot) for slot in cenario["slots"]]
    texto_base = ". ".join(partes_cenario)
    texto_base = preencher(texto_base, comp)

    estilo = random.choice(ESTILOS)
    partes = []

    saudacao = escolher_complemento(comp, "saudacao", "_all", estilo.usa_saudacao)
    if saudacao:
        partes.append(saudacao.strip())

    partes.append(texto_base)

    cross = escolher_complemento(comp, "cross_area", area, estilo.usa_cross)
    if cross:
        partes.append(cross)

    urgencia_compl = escolher_complemento(comp, "complemento_urgencia", urgencia, estilo.usa_complemento_urgencia)
    if urgencia_compl:
        partes.append(urgencia_compl)

    compartilhado = escolher_complemento(comp, "complemento_compartilhado", "_all", estilo.usa_complemento_compartilhado)
    if compartilhado:
        partes.append(compartilhado)

    fechamento = ""
    if random.random() < estilo.usa_fechamento:
        opcoes = comp.get("fechamento", {}).get("_all", [""])
        fechamento = random.choice(opcoes)

    texto = ". ".join(p.rstrip(".!?, ") for p in partes if p.strip())
    texto += "." + fechamento if fechamento.strip() else "."

    texto = aplicar_ruido(texto, estilo.intensidade_ruido)

    texto = texto.replace('"', '').replace("'", '')
    texto = re.sub(r'\s+', ' ', texto).strip()
    texto = re.sub(r'\.{2,}', '.', texto)
    texto = re.sub(r'\.\s*\.', '.', texto)
    texto = re.sub(r'^\.', '', texto).strip()
    if texto and texto[0].islower():
        texto = texto[0].upper() + texto[1:]

    return {"relato": texto, "area": area, "urgencia": urgencia}


def gerar_dataset(cenarios, comp, n=10000, seed=42):
    random.seed(seed)
    n_extra = int(n * 1.25)
    registros = []
    por_area = n_extra // len(AREAS)
    resto = n_extra % len(AREAS)
    for i, area in enumerate(AREAS):
        qtd = por_area + (1 if i < resto else 0)
        for _ in range(qtd):
            registros.append(gerar_relato(cenarios, comp, area=area))
    random.shuffle(registros)

    vistos = set()
    unicos = []
    for r in registros:
        if r["relato"] not in vistos:
            vistos.add(r["relato"])
            unicos.append(r)

    return unicos[:n]


def limpar_texto_csv(texto):
    texto = texto.replace('"', '')
    texto = texto.replace("'", '')
    texto = texto.replace(";", ",")
    return texto


def exportar_csv(registros, caminho="relatos.csv"):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["relato", "area", "urgencia"],
            delimiter=";",
            quoting=csv.QUOTE_MINIMAL,
        )
        w.writeheader()
        for r in registros:
            w.writerow({
                "relato": limpar_texto_csv(r["relato"]),
                "area": r["area"],
                "urgencia": r["urgencia"],
            })
    print(f"{len(registros)} relatos -> {caminho}")


def diagnostico(registros):
    def limpar(p):
        return re.sub(r'[.,!?;:\'"()\[\]{}]', '', p).strip()

    def eh_vocab(p):
        p = limpar(p)
        return (p and len(p) > 2
                and not re.match(r'^[\d.,r$%]+$', p, re.IGNORECASE)
                and not re.match(r'^\d', p))

    def analisar(campo, valores):
        print(f"\n--- {campo.upper()} ---")
        por_classe = defaultdict(Counter)
        for r in registros:
            palavras = {limpar(p) for p in r["relato"].lower().split() if eh_vocab(p)}
            por_classe[r[campo]].update(palavras)
        for val in valores:
            pv = set(por_classe[val].keys())
            outras = set()
            for o in set(valores) - {val}:
                outras.update(por_classe[o].keys())
            excl = {p for p in (pv - outras) if por_classe[val][p] >= 5}
            if excl:
                top = sorted(excl, key=lambda x: por_classe[val][x], reverse=True)[:8]
                info = ', '.join(f'{p}({por_classe[val][p]})' for p in top)
                print(f"  {val}: {len(excl)} exclusivas (top: {info})")
            else:
                print(f"  {val}: sem palavras exclusivas frequentes")

    analisar("area", AREAS)
    analisar("urgencia", URGENCIAS)

    print("\n--- Distribuicao ---")
    for campo, vals in [("area", AREAS), ("urgencia", URGENCIAS)]:
        c = Counter(r[campo] for r in registros)
        print(f"  {campo}: {dict(sorted(c.items()))}")

    unicos = len(set(r["relato"] for r in registros))
    total = len(registros)
    print(f"\n  Total: {total} | Unicos: {unicos} | Repeticao: {(1 - unicos/total)*100:.1f}%")


if __name__ == "__main__":
    cenarios = carregar_cenarios()
    comp = carregar_complementos()
    registros = gerar_dataset(cenarios, comp, n=10000, seed=42)
    exportar_csv(registros, "relatos.csv")
    diagnostico(registros)
