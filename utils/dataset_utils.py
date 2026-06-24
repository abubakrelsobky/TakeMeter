from datasets import Dataset
import pandas as pd

def load_split(path):
    df = pd.read_csv(path)
    return Dataset.from_pandas(df)
