"""
Gerador de Relatos v3 - Motor
==============================
Lê dados de:
  - cenarios.csv     → cenários composicionais (slots de frases)
  - complementos.csv → saudações, fechamentos, nomes, lojas, etc.

Para alterar conteúdo: edite os CSVs.
Para alterar lógica: edite este script.
"""

import random
import re
import csv
import json
import os
from dataclasses import dataclass
from collections import Counter, defaultdict

# =============================================================================
# CARREGAMENTO DOS CSVs
# =============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def carregar_cenarios(caminho=None):
    """Carrega cenarios.csv → lista de dicts com slots"""
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
    """Carrega complementos.csv → dict agrupado por tipo e chave"""
    caminho = caminho or os.path.join(SCRIPT_DIR, "csv/complementos.csv")
    dados = defaultdict(lambda: defaultdict(list))

    with open(caminho, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tipo = row["tipo"].strip()
            chave = row["chave"].strip()
            valor = row["valor"]  # NÃO strip — espaços em saudação/fechamento são intencionais

            if tipo in ("saudacao", "fechamento", "complemento_compartilhado"):
                dados[tipo]["_all"].append(valor)
            elif tipo in ("complemento_urgencia", "cross_area"):
                dados[tipo][chave].append(valor)
            else:
                # nome, loja, investimento, tempo, erro
                dados[tipo]["_all"].append(valor.strip())

    return dict(dados)


# =============================================================================
# PREENCHIMENTO DE VARIÁVEIS
# =============================================================================

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
    """Substitui placeholders usando dados do complementos.csv"""
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


# =============================================================================
# ESTILOS E RUÍDO
# =============================================================================

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


# =============================================================================
# GERADOR
# =============================================================================

AREAS = ["pix", "cartao", "conta", "emprestimo", "investimento", "atendimento"]
URGENCIAS = ["baixa", "media", "alta"]


def gerar_relato(cenarios, comp, area=None, urgencia=None):
    """Gera um relato coerente a partir dos dados carregados dos CSVs."""

    if area is None:
        area = random.choice(AREAS)

    # Filtrar cenários da área
    cenarios_area = [c for c in cenarios if c["area"] == area]
    cenario = random.choice(cenarios_area)

    # Urgência baseada nos pesos do cenário
    if urgencia is None:
        urgs = [(u, p) for u, p in cenario["urgencias"].items() if p > 0]
        us, ps = zip(*urgs)
        urgencia = random.choices(us, weights=ps, k=1)[0]

    # Montar texto base: 1 frase de cada slot
    partes_cenario = [random.choice(slot) for slot in cenario["slots"]]
    texto_base = ". ".join(partes_cenario)
    texto_base = preencher(texto_base, comp)

    # Estilo
    estilo = random.choice(ESTILOS)

    # Montar relato
    partes = []

    # Saudação
    if random.random() < estilo.usa_saudacao:
        s = random.choice(comp.get("saudacao", {}).get("_all", [""]))
        if s.strip():
            partes.append(s.strip())

    # Corpo principal
    partes.append(texto_base)

    # Cross-area
    if random.random() < estilo.usa_cross:
        opcoes = comp.get("cross_area", {}).get(area, [])
        if opcoes:
            ctx = random.choice(opcoes)
            if ctx.strip():
                partes.append(ctx)

    # Complemento de urgência
    if random.random() < estilo.usa_complemento_urgencia:
        opcoes = comp.get("complemento_urgencia", {}).get(urgencia, [])
        if opcoes:
            c = random.choice(opcoes)
            if c.strip():
                partes.append(c)

    # Complemento compartilhado
    if random.random() < estilo.usa_complemento_compartilhado:
        opcoes = comp.get("complemento_compartilhado", {}).get("_all", [])
        if opcoes:
            partes.append(random.choice(opcoes))

    # Fechamento
    fechamento = ""
    if random.random() < estilo.usa_fechamento:
        opcoes = comp.get("fechamento", {}).get("_all", [""])
        fechamento = random.choice(opcoes)

    # Juntar
    texto = ". ".join(p.rstrip(".!?, ") for p in partes if p.strip())
    texto += "." + fechamento if fechamento.strip() else "."

    # Ruído
    texto = aplicar_ruido(texto, estilo.intensidade_ruido)

    # Limpeza
    texto = texto.replace('"', '').replace("'", '')
    texto = re.sub(r'\s+', ' ', texto).strip()
    texto = re.sub(r'\.{2,}', '.', texto)
    texto = re.sub(r'\.\s*\.', '.', texto)
    texto = re.sub(r'^\.', '', texto).strip()
    if texto and texto[0].islower():
        texto = texto[0].upper() + texto[1:]

    return {"relato": texto, "area": area, "urgencia": urgencia}


# =============================================================================
# GERAÇÃO EM LOTE
# =============================================================================

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


def limpar_texto_csv(texto):
    """Remove/substitui caracteres que quebram parsing de CSV."""
    texto = texto.replace('"', '')
    texto = texto.replace("'", '')
    texto = texto.replace(";", ",")  # semicolon é nosso separador
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
    print(f"✓ {len(registros)} relatos → {caminho} (separador: ;)")


# =============================================================================
# DIAGNÓSTICO
# =============================================================================

def diagnostico(registros):
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO")
    print("=" * 60)

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
                print(f"  ⚠️  {val}: {len(excl)} exclusivas (top: {info})")
            else:
                print(f"  ✓  {val}: sem palavras exclusivas frequentes")

    analisar("area", AREAS)
    analisar("urgencia", URGENCIAS)

    # Distribuição
    print("\n--- Distribuição ---")
    for campo, vals in [("area", AREAS), ("urgencia", URGENCIAS)]:
        c = Counter(r[campo] for r in registros)
        print(f"  {campo}: {dict(sorted(c.items()))}")

    # Diversidade
    unicos = len(set(r["relato"] for r in registros))
    total = len(registros)
    print(f"\n--- Diversidade ---")
    print(f"  Total: {total} | Únicos: {unicos} | Repetição: {(1 - unicos/total)*100:.1f}%")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("Carregando dados...")
    cenarios = carregar_cenarios()
    comp = carregar_complementos()
    print(f"  {len(cenarios)} cenários carregados")

    # Contar combinações
    total_combos = sum(len(c["slots"][0]) * len(c["slots"][1]) for c in cenarios)
    print(f"  {total_combos} combinações base de cenários")

    print("\nGerando 10.000 relatos...\n")
    registros = gerar_dataset(cenarios, comp, n=10000, seed=42)

    print("EXEMPLOS:")
    print("=" * 60)
    for i, r in enumerate(registros[:10]):
        print(f"\n[{i+1}] {r['area']} | {r['urgencia']}")
        print(f"    {r['relato']}")

    exportar_csv(registros, "relatos.csv")
    diagnostico(registros)
    print("\n✓ Concluído!")