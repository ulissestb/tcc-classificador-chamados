import random
import re
import csv
import os
from dataclasses import dataclass
from collections import Counter, defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AREAS = ["pix", "cartao", "conta", "emprestimo", "investimento", "atendimento"]
URGENCIAS = ["baixa", "media", "alta"]


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
    Estilo("formal",      0.85, 0.85, 0.60, 0.30, 0.05, 0.08),
    Estilo("informal",    0.35, 0.25, 0.50, 0.40, 0.45, 0.12),
    Estilo("telegrafico", 0.05, 0.05, 0.30, 0.15, 0.25, 0.05),
    Estilo("prolixo",     0.75, 0.75, 0.80, 0.60, 0.15, 0.20),
    Estilo("irritado",    0.10, 0.15, 0.50, 0.30, 0.35, 0.10),
]

ABREVIACOES = {
    "você": ["vc", "voce"], "porque": ["pq"], "também": ["tb", "tbm"],
    "não": ["nao", "ñ"], "está": ["tá", "ta"], "estou": ["tô", "to"],
    "para": ["pra"], "que": ["q"], "de": ["d"], "muito": ["mt"],
}


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


def _obter_lista(comp, tipo, chave="_all", fallback=None):
    return comp.get(tipo, {}).get(chave, fallback or [])


def _escolher(comp, tipo, chave="_all"):
    opcoes = _obter_lista(comp, tipo, chave)
    if opcoes:
        escolha = random.choice(opcoes)
        if escolha.strip():
            return escolha.strip()
    return None


def gerar_valor(faixa="medio"):
    faixas = {
        "pequeno": (10, 150),
        "medio": (150, 3000),
        "grande": (3000, 30000),
        "muito_grande": (30000, 200000),
    }
    mi, ma = faixas.get(faixa, faixas["medio"])
    v = round(random.uniform(mi, ma), 2)
    formatado = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return random.choice([
        f"R$ {formatado}", f"R${formatado}", f"R$ {v:.0f}", f"{v:.0f} reais",
    ])


def preencher(texto, comp):
    nomes = _obter_lista(comp, "nome", fallback=["João"])
    lojas = _obter_lista(comp, "loja", fallback=["uma loja"])
    investimentos = _obter_lista(comp, "investimento", fallback=["CDB"])
    tempos = _obter_lista(comp, "tempo", fallback=["ontem"])
    erros = _obter_lista(comp, "erro", fallback=["erro desconhecido"])

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


def limpar_texto(texto):
    texto = texto.replace('"', '').replace("'", '')
    texto = re.sub(r'\s+', ' ', texto).strip()
    texto = re.sub(r'\.{2,}', '.', texto)
    texto = re.sub(r'\.\s*\.', '.', texto)
    texto = re.sub(r'^\.', '', texto).strip()
    if texto and texto[0].islower():
        texto = texto[0].upper() + texto[1:]
    return texto


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
    texto_base = preencher(". ".join(partes_cenario), comp)

    estilo = random.choice(ESTILOS)
    partes = []

    saudacao = _escolher(comp, "saudacao") if random.random() < estilo.usa_saudacao else None
    if saudacao:
        partes.append(saudacao)

    partes.append(texto_base)

    if random.random() < estilo.usa_cross:
        cross = _escolher(comp, "cross_area", area)
        if cross:
            partes.append(cross)

    if random.random() < estilo.usa_complemento_urgencia:
        compl = _escolher(comp, "complemento_urgencia", urgencia)
        if compl:
            partes.append(compl)

    if random.random() < estilo.usa_complemento_compartilhado:
        compl = _escolher(comp, "complemento_compartilhado")
        if compl:
            partes.append(compl)

    fechamento = ""
    if random.random() < estilo.usa_fechamento:
        opcoes = _obter_lista(comp, "fechamento", fallback=[""])
        fechamento = random.choice(opcoes)

    texto = ". ".join(p.rstrip(".!?, ") for p in partes if p.strip())
    texto += "." + fechamento if fechamento.strip() else "."
    texto = aplicar_ruido(texto, estilo.intensidade_ruido)
    texto = limpar_texto(texto)

    return {"relato": texto, "area": area, "urgencia": urgencia}


def gerar_dataset(cenarios, comp, n=10000, seed=42):
    random.seed(seed)
    registros = []
    por_area = n // len(AREAS)
    resto = n % len(AREAS)
    for i, area in enumerate(AREAS):
        qtd = por_area + (1 if i < resto else 0)
        for _ in range(qtd):
            registros.append(gerar_relato(cenarios, comp, area=area))
    random.shuffle(registros)
    return registros


def exportar_csv(registros, caminho="relatos.csv"):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["relato", "area", "urgencia"], delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in registros:
            relato = r["relato"].replace('"', '').replace("'", '').replace(";", ",")
            w.writerow({"relato": relato, "area": r["area"], "urgencia": r["urgencia"]})
    print(f"  {len(registros)} relatos -> {caminho}")


def diagnostico(registros):
    print("\n" + "=" * 60)
    print("DIAGNOSTICO")
    print("=" * 60)

    def _limpar(p):
        return re.sub(r'[.,!?;:\'"()\[\]{}]', '', p).strip()

    def _eh_vocab(p):
        p = _limpar(p)
        return (p and len(p) > 2
                and not re.match(r'^[\d.,r$%]+$', p, re.IGNORECASE)
                and not re.match(r'^\d', p))

    for campo, valores in [("area", AREAS), ("urgencia", URGENCIAS)]:
        print(f"\n--- {campo.upper()} ---")
        por_classe = defaultdict(Counter)
        for r in registros:
            palavras = {_limpar(p) for p in r["relato"].lower().split() if _eh_vocab(p)}
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

    print("\n--- Distribuicao ---")
    for campo in ["area", "urgencia"]:
        c = Counter(r[campo] for r in registros)
        print(f"  {campo}: {dict(sorted(c.items()))}")

    unicos = len(set(r["relato"] for r in registros))
    total = len(registros)
    print(f"\n--- Diversidade ---")
    print(f"  Total: {total} | Unicos: {unicos} | Repeticao: {(1 - unicos/total)*100:.1f}%")


if __name__ == "__main__":
    print("Carregando dados...")
    cenarios = carregar_cenarios()
    comp = carregar_complementos()
    print(f"  {len(cenarios)} cenarios carregados")

    total_combos = sum(len(c["slots"][0]) * len(c["slots"][1]) for c in cenarios)
    print(f"  {total_combos} combinacoes base de cenarios")

    print("\nGerando 10.000 relatos...\n")
    registros = gerar_dataset(cenarios, comp, n=10000, seed=42)

    print("EXEMPLOS:")
    print("=" * 60)
    for i, r in enumerate(registros[:10]):
        print(f"\n[{i+1}] {r['area']} | {r['urgencia']}")
        print(f"    {r['relato']}")

    exportar_csv(registros, "relatos.csv")
    diagnostico(registros)
    print("\nConcluido!")
