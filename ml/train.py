# SentimentLens/ml/train.py

import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
import torch
from datasets import Dataset
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def load_and_prepare_data(filepath='ml/financial_phrasebank.csv'):
    # Download from: https://www.kaggle.com/datasets/ankurzing/sentiment-analysis-for-financial-news
    df = pd.read_csv(filepath, names=['sentiment', 'text'], encoding='latin-1')
    df = df.dropna()
    df['sentiment'] = df['sentiment'].astype('category')

    # Map sentiments to numerical labels
    label_map = {'neutral': 0, 'positive': 1, 'negative': 2}
    df['label'] = df['sentiment'].map(label_map)

    return df

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def fine_tune_finbert():
    # Load data
    df = load_and_prepare_data()
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)

    # Load tokenizer and model
    model_name = "ProsusAI/finbert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

    # Tokenize datasets
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True)

    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)

    # Set format for PyTorch
    train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
    val_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])

    # Training arguments
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    # Start training
    trainer.train()

    # Save the fine-tuned model to a clean path
    model.save_pretrained("fine_tuned_finbert")
    tokenizer.save_pretrained("fine_tuned_finbert")
    print("Model fine-tuning complete and saved to ./fine_tuned_finbert")

if __name__ == '__main__':
    fine_tune_finbert()
