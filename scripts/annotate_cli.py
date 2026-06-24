#!/usr/bin/env python3
"""
Simple CLI to annotate raw CSV -> labeled CSV
Usage:
  python scripts/annotate_cli.py data/raw/sub_comments.csv data/labeled/sub_labeled.csv
Labels: 0=Insightful, 1=Opinion, 2=LowQuality
"""
import csv
import sys
import os
from tqdm import tqdm

LABELS = {"0":"Insightful","1":"Opinion","2":"LowQuality"}

def prompt_label(text):
    print("\n----\n")
    print(text)
    print("\nLabels: 0=Insightful, 1=Opinion, 2=LowQuality, s=skip, q=quit")
    while True:
        r = input("label> ").strip()
        if r in LABELS: return int(r)
        if r=="s": return None
        if r=="q": exit(0)
        print("invalid")

def main():
    if len(sys.argv)<3:
        print("Usage: annotate_cli.py input.csv output.csv")
        return
    inp, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(inp, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)]
    labeled = []
    for r in tqdm(rows):
        text = r.get("text") or r.get("body") or r.get("title") or ""
        lab = prompt_label(text)
        if lab is None: continue
        labeled.append({"id": r.get("id",""), "text": text, "label": lab})
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id","text","label"])
        writer.writeheader()
        writer.writerows(labeled)
    print("Wrote", out)

if __name__=="__main__":
    main()
