import pandas as pd
import torch

from datasets import Dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

tokenizer = BertTokenizer.from_pretrained(
    "neuralmind/bert-base-portuguese-cased",
)

model = BertForSequenceClassification.from_pretrained(
    "neuralmind/bert-base-portuguese-cased",
    num_labels=3
)

model.to("cuda" if torch.cuda.is_available() else "cpu")

def tokenize(values):
    return tokenizer(
        values["relato"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

if __name__ == "__main__":
    df = pd.read_csv("reclamacoes.csv")
    df['label'] = df['nivel_urgencia'] - 1
    
    train_df, test_df = train_test_split(
        df,
        test_size=0.3,
        random_state=42,
        stratify=df['label']
    )
    
    train_ds = Dataset.from_pandas(train_df[['relato', 'label']])
    test_ds = Dataset.from_pandas(test_df[['relato', 'label']])
    
    train_ds = train_ds.map(tokenize, batched=True)
    test_ds = test_ds.map(tokenize, batched=True)
    train_ds.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
    test_ds.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
    
    training_args = TrainingArguments(
        output_dir="./bert_results",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir="./bert_logs",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss"
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        processing_class=tokenizer
    )
    
    trainer.train()
    trainer.save_model("./bert_model")
    
    predictions = trainer.predict(test_ds)
    y_pred = predictions.predictions.argmax(-1)
    y_true = predictions.label_ids
    print(classification_report(y_true, y_pred))