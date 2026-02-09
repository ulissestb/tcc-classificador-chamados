import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path

MODELS_DIR = Path(__file__).parent / "models"

MODELOS = [
    "regressao-logistica",
    "naive-bayes",
    "svm",
    "random-forest",
    "lstm",
    "bert",
]


def executar_modelo(nome):
    script = MODELS_DIR / nome / "main.py"
    if not script.exists():
        print(f"  SKIP: {script} nao encontrado")
        return False

    print(f"\n  [{nome.upper()}]")

    inicio = time.time()
    resultado = subprocess.run([sys.executable, str(script)])
    tempo = timedelta(seconds=int(time.time() - inicio))

    if resultado.returncode == 0:
        print(f"  {nome} finalizado em {tempo}")
        return True

    print(f"  {nome} falhou (codigo {resultado.returncode})")
    return False


if __name__ == "__main__":
    sucessos = []
    falhas = []

    for modelo in MODELOS:
        ok = executar_modelo(modelo)
        (sucessos if ok else falhas).append(modelo)

    print(f"\nSucesso: {', '.join(sucessos) if sucessos else 'nenhum'}")
    print(f"Falha:   {', '.join(falhas) if falhas else 'nenhuma'}")
