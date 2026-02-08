import pandas as pd
import numpy as np
import torch
import time
from datetime import timedelta

from datasets import Dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight

MODEL_NAME = "neuralmind/bert-base-portuguese-cased"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LABEL_MAP = {"baixa": 0, "media": 1, "alta": 2}
LABEL_NAMES = ["baixa", "media", "alta"]


class WeightedTrainer(Trainer):
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if class_weights is not None:
            self.class_weights = torch.tensor(class_weights, dtype=torch.float32).to(DEVICE)
        else:
            self.class_weights = None

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fn = torch.nn.CrossEntropyLoss(weight=self.class_weights)
        loss = loss_fn(logits, labels)
        return (loss, outputs) if return_outputs else loss


def treinar_config(config, train_df, test_df, class_weights):
    nome = config["nome"]
    print(f"\n{'='*60}")
    print(f"  {nome}")
    print(
        f"  lr={config['lr']}, epochs={config['epochs']}, "
        f"batch={config['batch_size']}, warmup={config['warmup_ratio']}, "
        f"max_len={config['max_len']}, weight_decay={config['weight_decay']}"
    )
    print(f"{'='*60}")

    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(LABEL_NAMES)).to(DEVICE)

    max_len = config["max_len"]

    def tokenize(values):
        return tokenizer(values["relato"], truncation=True, padding="max_length", max_length=max_len)

    train_ds = Dataset.from_pandas(train_df[["relato", "label"]].reset_index(drop=True))
    test_ds = Dataset.from_pandas(test_df[["relato", "label"]].reset_index(drop=True))
    train_ds = train_ds.map(tokenize, batched=True)
    test_ds = test_ds.map(tokenize, batched=True)

    torch_columns = ["input_ids", "attention_mask", "label"]
    train_ds.set_format(type="torch", columns=torch_columns)
    test_ds.set_format(type="torch", columns=torch_columns)

    training_args = TrainingArguments(
        output_dir=f"./bert_results_{nome}",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=config["lr"],
        per_device_train_batch_size=config["batch_size"],
        per_device_eval_batch_size=32,
        num_train_epochs=config["epochs"],
        weight_decay=config["weight_decay"],
        warmup_ratio=config["warmup_ratio"],
        logging_dir=f"./bert_logs_{nome}",
        logging_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        fp16=torch.cuda.is_available(),
        seed=42,
        save_total_limit=2,
    )

    use_weights = config.get("use_class_weights", True)

    trainer = WeightedTrainer(
        class_weights=class_weights if use_weights else None,
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        processing_class=tokenizer,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=config.get("patience", 2))],
    )

    inicio = time.time()
    trainer.train()
    tempo = time.time() - inicio

    predictions = trainer.predict(test_ds)
    y_pred = predictions.predictions.argmax(-1)
    y_true = predictions.label_ids

    report = classification_report(y_true, y_pred, target_names=LABEL_NAMES)
    report_dict = classification_report(y_true, y_pred, target_names=LABEL_NAMES, output_dict=True)

    print(f"\n  Resultado ({nome}):")
    print(report)

    del model, trainer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return {
        "nome": nome,
        "f1_macro": report_dict["macro avg"]["f1-score"],
        "accuracy": report_dict["accuracy"],
        "tempo": tempo,
        "report": report,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  TREINAMENTO BERT")
    print("=" * 60)

    df = pd.read_csv("relatos.csv", sep=";")
    df["label"] = df["urgencia"].map(LABEL_MAP)
    print(f"Dataset: {len(df)} registros\n")

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])

    cw = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=train_df["label"].values)
    print(f"Class weights: {dict(zip(LABEL_NAMES, cw))}\n")

    configs = [
        {
            "nome": "bert-base",
            "lr": 2e-5, "epochs": 8, "batch_size": 16,
            "warmup_ratio": 0.1, "max_len": 256, "weight_decay": 0.01,
            "patience": 2, "use_class_weights": True,
        },
        {
            "nome": "bert-lr-baixo",
            "lr": 1e-5, "epochs": 10, "batch_size": 16,
            "warmup_ratio": 0.1, "max_len": 256, "weight_decay": 0.01,
            "patience": 3, "use_class_weights": True,
        },
        {
            "nome": "bert-sem-weights",
            "lr": 2e-5, "epochs": 8, "batch_size": 16,
            "warmup_ratio": 0.1, "max_len": 256, "weight_decay": 0.01,
            "patience": 2, "use_class_weights": False,
        },
        {
            "nome": "bert-batch32",
            "lr": 3e-5, "epochs": 8, "batch_size": 32,
            "warmup_ratio": 0.15, "max_len": 256, "weight_decay": 0.02,
            "patience": 2, "use_class_weights": True,
        },
        {
            "nome": "bert-agressivo",
            "lr": 5e-5, "epochs": 6, "batch_size": 16,
            "warmup_ratio": 0.05, "max_len": 200, "weight_decay": 0.01,
            "patience": 2, "use_class_weights": True,
        },
    ]

    resultados = []
    for config in configs:
        r = treinar_config(config, train_df, test_df, cw)
        resultados.append(r)

    print("\n" + "=" * 60)
    print("  RESUMO BERT")
    print("=" * 60)
    print(f"\n  {'Config':<25} {'Accuracy':>10} {'F1 Macro':>10} {'Tempo':>10}")
    print("  " + "-" * 55)
    for r in sorted(resultados, key=lambda x: x["f1_macro"], reverse=True):
        t = timedelta(seconds=int(r["tempo"]))
        print(f"  {r['nome']:<25} {r['accuracy']:>10.4f} {r['f1_macro']:>10.4f} {str(t):>10}")

    melhor = max(resultados, key=lambda x: x["f1_macro"])
    print(f"\n  Melhor: {melhor['nome']} (F1={melhor['f1_macro']:.4f})")
