import pandas as pd
import numpy as np
import torch

from datasets import Dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight

# =============================================================================
# MODELO
# =============================================================================

MODEL_NAME = "neuralmind/bert-base-portuguese-cased"

tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

model = BertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=3
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


def tokenize(values):
    return tokenizer(
        values["relato"],
        truncation=True,
        padding="max_length",
        max_length=256  # ← aumentado de 128 pra não cortar relatos longos
    )


# =============================================================================
# TRAINER COM CLASS WEIGHTS
# =============================================================================

class WeightedTrainer(Trainer):
    """Trainer com pesos por classe pra lidar com desbalanceamento."""

    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if class_weights is not None:
            self.class_weights = torch.tensor(
                class_weights, dtype=torch.float32
            ).to(device)
        else:
            self.class_weights = None

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self.class_weights is not None:
            loss_fn = torch.nn.CrossEntropyLoss(weight=self.class_weights)
        else:
            loss_fn = torch.nn.CrossEntropyLoss()

        loss = loss_fn(logits, labels)
        return (loss, outputs) if return_outputs else loss


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    df = pd.read_csv("relatos.csv", sep=";")
    df["label"] = df["urgencia"].map({
        "baixa": 0, "media": 1, "alta": 2
    })

    print(f"Dataset: {len(df)} registros")
    print(f"Distribuição:\n{df['urgencia'].value_counts()}\n")

    # Split estratificado
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["label"]
    )

    # ---- Class weights (compensa desbalanceamento) ----
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.array([0, 1, 2]),
        y=train_df["label"].values
    )
    print(f"Class weights: {dict(zip(['baixa','media','alta'], class_weights))}\n")

    # ---- Datasets ----
    train_ds = Dataset.from_pandas(train_df[["relato", "label"]].reset_index(drop=True))
    test_ds = Dataset.from_pandas(test_df[["relato", "label"]].reset_index(drop=True))

    train_ds = train_ds.map(tokenize, batched=True)
    test_ds = test_ds.map(tokenize, batched=True)

    train_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
    test_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

    # ---- Training args ----
    training_args = TrainingArguments(
        output_dir="./bert_results",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=8,              # ← mais épocas (early stopping para quando convergir)
        weight_decay=0.01,
        warmup_ratio=0.1,               # ← warmup de 10% dos steps
        logging_dir="./bert_logs",
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        fp16=torch.cuda.is_available(),  # ← mixed precision se tiver GPU
        seed=42,
    )

    # ---- Trainer ----
    trainer = WeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        processing_class=tokenizer,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    trainer.train()

    # ---- Avaliação ----
    predictions = trainer.predict(test_ds)
    y_pred = predictions.predictions.argmax(-1)
    y_true = predictions.label_ids

    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(classification_report(
        y_true, y_pred,
        target_names=["baixa", "media", "alta"]
    ))