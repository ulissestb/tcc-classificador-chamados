import pandas as pd
import numpy as np
import time
import warnings
import re
from datetime import timedelta
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight

warnings.filterwarnings("ignore")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LABEL_MAP = {"baixa": 0, "media": 1, "alta": 2}
LABEL_NAMES = ["baixa", "media", "alta"]


def tokenizar(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\sáéíóúãõâêîôûç]', ' ', texto)
    return texto.split()


def construir_vocabulario(textos, min_freq=2, max_vocab=20000):
    counter = Counter()
    for texto in textos:
        counter.update(tokenizar(texto))

    vocab = {"<PAD>": 0, "<UNK>": 1}
    idx = 2
    for palavra, freq in counter.most_common(max_vocab):
        if freq >= min_freq:
            vocab[palavra] = idx
            idx += 1

    print(f"  Vocabulario: {len(vocab)} tokens (min_freq={min_freq})")
    return vocab


def texto_para_indices(texto, vocab, max_len=200):
    tokens = tokenizar(texto)[:max_len]
    indices = [vocab.get(t, vocab["<UNK>"]) for t in tokens]
    if len(indices) < max_len:
        indices += [vocab["<PAD>"]] * (max_len - len(indices))
    return indices


class RelatoDataset(Dataset):
    def __init__(self, textos, labels, vocab, max_len=200):
        self.textos = textos
        self.labels = labels
        self.vocab = vocab
        self.max_len = max_len

    def __len__(self):
        return len(self.textos)

    def __getitem__(self, idx):
        indices = texto_para_indices(self.textos[idx], self.vocab, self.max_len)
        return (
            torch.tensor(indices, dtype=torch.long),
            torch.tensor(self.labels[idx], dtype=torch.long),
        )


class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, num_classes, dropout=0.3, bidirectional=True):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
        )
        direction_mult = 2 if bidirectional else 1
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * direction_mult, num_classes)

    def forward(self, x):
        embedded = self.dropout(self.embedding(x))
        _, (hidden, _) = self.lstm(embedded)

        if self.lstm.bidirectional:
            hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        else:
            hidden = hidden[-1]

        return self.fc(self.dropout(hidden))


def treinar_lstm(X_train, y_train, X_val, y_val, X_test, y_test, config, class_weights=None):
    vocab = construir_vocabulario(X_train, min_freq=config.get("min_freq", 2), max_vocab=config.get("max_vocab", 20000))
    max_len = config.get("max_len", 200)

    train_ds = RelatoDataset(X_train, y_train, vocab, max_len)
    val_ds = RelatoDataset(X_val, y_val, vocab, max_len)
    test_ds = RelatoDataset(X_test, y_test, vocab, max_len)

    batch_size = config.get("batch_size", 32)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    test_loader = DataLoader(test_ds, batch_size=batch_size)

    model = LSTMClassifier(
        vocab_size=len(vocab),
        embed_dim=config.get("embed_dim", 128),
        hidden_dim=config.get("hidden_dim", 128),
        num_layers=config.get("num_layers", 2),
        num_classes=len(LABEL_NAMES),
        dropout=config.get("dropout", 0.3),
        bidirectional=config.get("bidirectional", True),
    ).to(DEVICE)

    if class_weights is not None:
        weights = torch.tensor(class_weights, dtype=torch.float32).to(DEVICE)
        criterion = nn.CrossEntropyLoss(weight=weights)
    else:
        criterion = nn.CrossEntropyLoss()

    optimizer = Adam(model.parameters(), lr=config.get("lr", 1e-3), weight_decay=config.get("weight_decay", 1e-4))
    scheduler = ReduceLROnPlateau(optimizer, mode="min", patience=2, factor=0.5)

    epochs = config.get("epochs", 20)
    patience = config.get("patience", 5)
    best_val_loss = float("inf")
    epochs_sem_melhora = 0
    best_state = None

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(DEVICE), batch_y.to(DEVICE)
            optimizer.zero_grad()
            output = model(batch_x)
            loss = criterion(output, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(DEVICE), batch_y.to(DEVICE)
                val_loss += criterion(model(batch_x), batch_y).item()

        train_loss = total_loss / len(train_loader)
        val_loss = val_loss / len(val_loader)
        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_sem_melhora = 0
            best_state = model.state_dict().copy()
        else:
            epochs_sem_melhora += 1

        if (epoch + 1) % 5 == 0 or epoch == 0:
            lr_atual = optimizer.param_groups[0]["lr"]
            print(
                f"    Epoch {epoch+1:>3}/{epochs} | "
                f"Train: {train_loss:.4f} | Val: {val_loss:.4f} | "
                f"LR: {lr_atual:.6f} | Patience: {epochs_sem_melhora}/{patience}"
            )

        if epochs_sem_melhora >= patience:
            print(f"    Early stopping na epoch {epoch+1}")
            break

    model.load_state_dict(best_state)
    model.eval()
    all_preds = []
    all_true = []
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(DEVICE)
            preds = model(batch_x).argmax(dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_true.extend(batch_y.numpy())

    return np.array(all_true), np.array(all_preds)


if __name__ == "__main__":
    print("=" * 60)
    print("  TREINAMENTO LSTM")
    print("=" * 60)

    df = pd.read_csv("relatos.csv", sep=";")

    X = df["relato"].values
    y = df["urgencia"].map(LABEL_MAP).values

    print(f"Device: {DEVICE}")
    print(f"Dataset: {len(df)} registros\n")

    X_trainval, X_test, y_trainval, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_trainval, y_trainval, test_size=0.125, random_state=42, stratify=y_trainval)
    print(f"Treino: {len(X_train)} | Validacao: {len(X_val)} | Teste: {len(X_test)}")

    cw = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=y_train)
    print(f"Class weights: {dict(zip(LABEL_NAMES, cw))}\n")

    configs = [
        {
            "nome": "LSTM-base",
            "embed_dim": 128, "hidden_dim": 128, "num_layers": 2,
            "dropout": 0.3, "bidirectional": True,
            "lr": 1e-3, "batch_size": 32, "max_len": 200,
            "epochs": 30, "patience": 5,
        },
        {
            "nome": "LSTM-grande",
            "embed_dim": 256, "hidden_dim": 256, "num_layers": 2,
            "dropout": 0.4, "bidirectional": True,
            "lr": 5e-4, "batch_size": 32, "max_len": 256,
            "epochs": 30, "patience": 5,
        },
        {
            "nome": "LSTM-leve",
            "embed_dim": 64, "hidden_dim": 64, "num_layers": 1,
            "dropout": 0.2, "bidirectional": True,
            "lr": 2e-3, "batch_size": 64, "max_len": 150,
            "epochs": 30, "patience": 5,
        },
        {
            "nome": "LSTM-profundo",
            "embed_dim": 128, "hidden_dim": 128, "num_layers": 3,
            "dropout": 0.4, "bidirectional": True,
            "lr": 5e-4, "batch_size": 32, "max_len": 200,
            "epochs": 30, "patience": 7,
        },
    ]

    resultados = []
    for config in configs:
        nome = config.pop("nome")
        print(f"\n{'='*60}")
        print(f"  {nome}")
        print(f"  {config}")
        print(f"{'='*60}")

        inicio = time.time()
        y_true, y_pred = treinar_lstm(X_train, y_train, X_val, y_val, X_test, y_test, config, class_weights=cw)
        tempo = time.time() - inicio

        report = classification_report(y_true, y_pred, target_names=LABEL_NAMES)
        report_dict = classification_report(y_true, y_pred, target_names=LABEL_NAMES, output_dict=True)

        print(f"\n  Resultado ({nome}):")
        print(report)

        resultados.append({
            "nome": nome,
            "f1_macro": report_dict["macro avg"]["f1-score"],
            "accuracy": report_dict["accuracy"],
            "tempo": tempo,
            "report": report,
        })
        config["nome"] = nome

    print("\n" + "=" * 60)
    print("  RESUMO LSTM")
    print("=" * 60)
    print(f"\n  {'Config':<20} {'Accuracy':>10} {'F1 Macro':>10} {'Tempo':>10}")
    print("  " + "-" * 50)
    for r in sorted(resultados, key=lambda x: x["f1_macro"], reverse=True):
        t = timedelta(seconds=int(r["tempo"]))
        print(f"  {r['nome']:<20} {r['accuracy']:>10.4f} {r['f1_macro']:>10.4f} {str(t):>10}")
