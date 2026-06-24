#!/usr/bin/env python3
"""
Split labeled CSV into train/val/test in data/splits/
Usage:
  python scripts/split_dataset.py data/labeled/sub_labeled.csv --seed 42 --train_frac 0.8 --val_frac 0.1
"""
import pandas as pd
import sys, os
import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input_csv")
    p.add_argument("--train_frac", type=float, default=0.8)
    p.add_argument("--val_frac", type=float, default=0.1)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    df = pd.read_csv(args.input_csv)
    df = df.sample(frac=1, random_state=args.seed).reset_index(drop=True)
    n = len(df)
    ntrain = int(n * args.train_frac)
    nval = int(n * args.val_frac)
    train = df.iloc[:ntrain]
    val = df.iloc[ntrain:ntrain+nval]
    test = df.iloc[ntrain+nval:]
    outdir = os.path.join("data","splits")
    os.makedirs(outdir, exist_ok=True)
    train.to_csv(os.path.join(outdir,"train.csv"), index=False)
    val.to_csv(os.path.join(outdir,"val.csv"), index=False)
    test.to_csv(os.path.join(outdir,"test.csv"), index=False)
    print("Split sizes:", len(train), len(val), len(test))

if __name__=="__main__":
    main()
