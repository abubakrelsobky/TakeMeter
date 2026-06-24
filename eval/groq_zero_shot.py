"""
Minimal wrapper to send prompts to Groq API for zero-shot classification.
Uses Groq's OpenAI-compatible chat/completions endpoint.
This file defines classify_texts(texts) -> list of predicted label indices.
"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
API_URL = os.getenv("GROQ_API_URL")
MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

PROMPT_TEMPLATE = """
You are a classifier. Labels:
0: Insightful - adds evidence, reasoning, references.
1: Opinion - expresses personal preference or subjective take without deep reasoning.
2: LowQuality - noise, insults, one-word replies, off-topic.

Classify the following text into exactly one label (0,1,2). Output only the digit.

Text:
\"\"\"{text}\"\"\"
"""

def classify_texts(texts, batch_size=16):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    preds = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        for t in batch:
            prompt = PROMPT_TEMPLATE.format(text=t.replace('"', '\\"'))
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "Return only the label digit."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": 4,
            }
            resp = requests.post(f"{API_URL.rstrip('/')}/chat/completions", headers=headers, json=payload, timeout=30)
            if resp.status_code!=200:
                preds.append(1)  # fallback to Opinion
                continue
            data = resp.json()
            out = data["choices"][0]["message"]["content"].strip()
            # Try to extract a digit
            d = None
            for ch in out:
                if ch in "012":
                    d = int(ch); break
            if d is None:
                preds.append(1)
            else:
                preds.append(d)
    return preds
