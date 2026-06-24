#!/usr/bin/env python3
"""
Evaluate fine-tuned HF model and Groq zero-shot on test set.
Produces metrics and prints examples of errors.
Usage:
  python eval/eval_models.py
Requires models saved in train.config.OUTPUT_DIR and data/splits/test.csv
"""
import os
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from dotenv import load_dotenv
load_dotenv()
from train.config import MODEL_NAME, OUTPUT_DIR, MAX_LEN
from eval.groq_zero_shot import classify_texts
from utils.text_utils import clean_text

def hf_predict(model, tokenizer, texts, batch_size=32):
    enc = tokenizer(texts, truncation=True, padding=True, max_length=MAX_LEN, return_tensors="pt")
    with torch.no_grad():
        out = model(**{k:v.to(model.device) for k,v in enc.items()})
        preds = np.argmax(out.logits.cpu().numpy(), axis=1)
    return preds

def print_metrics(y_true, y_pred, label_names=None):
    acc = accuracy_score(y_true, y_pred)
    p,r,f,_ = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    print("Accuracy:", acc)
    for i,name in enumerate(label_names):
        print(f"Label {i} ({name}): precision={p[i]:.3f} recall={r[i]:.3f} f1={f[i]:.3f}")
    print("Confusion matrix:\n", cm)
    return {"accuracy":acc,"precision":p,"recall":r,"f1":f,"cm":cm}

def main():
    label_names = ["Insightful","Opinion","LowQuality"]
    df = pd.read_csv("data/splits/test.csv")
    texts = [clean_text(t) for t in df["text"].astype(str).tolist()]
    y_true = df["label"].astype(int).tolist()

    # Load HF model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(OUTPUT_DIR)
    model.eval()
    preds_hf = hf_predict(model, tokenizer, texts)
    print("=== HF model metrics ===")
    res_hf = print_metrics(y_true, preds_hf, label_names)

    # Groq zero-shot
    preds_groq = classify_texts(texts)
    print("=== Groq zero-shot metrics ===")
    res_groq = print_metrics(y_true, preds_groq, label_names)

    # Print examples model got wrong (3 examples)
    print("\nSome HF errors:")
    idxs = [i for i,(a,b) in enumerate(zip(y_true,preds_hf)) if a!=b][:10]
    for i in idxs[:3]:
        print("---")
        print("text:", texts[i])
        print("true:", label_names[y_true[i]], "pred:", label_names[int(preds_hf[i])])

    print("\nSome Groq errors:")
    idxs = [i for i,(a,b) in enumerate(zip(y_true,preds_groq)) if a!=b][:10]
    for i in idxs[:3]:
        print("---")
        print("text:", texts[i])
        print("true:", label_names[y_true[i]], "pred:", label_names[int(preds_groq[i])])

if __name__=="__main__":
    main()
