#!/usr/bin/env python3
"""
Train script using HuggingFace Trainer
Usage:
  python train/train_distilbert.py
Ensure data/splits/train.csv, val.csv exist.
"""
import os
import random
import numpy as np
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from dotenv import load_dotenv
load_dotenv()
from train.config import *

def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
set_seed(SEED)

def preprocess(examples, tokenizer):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=MAX_LEN)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    p,r,f,_ = precision_recall_fscore_support(labels, preds, average=None, zero_division=0)
    return {"accuracy": acc, "precision_per_class": p.tolist(), "recall_per_class": r.tolist(), "f1_per_class": f.tolist()}

def main():
    data_files = {"train":"data/splits/train.csv", "validation":"data/splits/val.csv"}
    dataset = load_dataset("csv", data_files=data_files)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    dataset = dataset.map(lambda x: preprocess(x, tokenizer), batched=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=NUM_LABELS)
    training_args = TrainingArguments(
        OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy"
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=dataset["train"], eval_dataset=dataset["validation"], processing_class=tokenizer, compute_metrics=compute_metrics)
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    print("Saved model to", OUTPUT_DIR)

if __name__=="__main__":
    main()
