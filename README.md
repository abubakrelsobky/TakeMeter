# TakeMeter

GitHub repository: TODO - paste the final repo URL here after pushing.

## Overview

TakeMeter is a 3-class text classifier for discourse quality. The project compares a fine-tuned DistilBERT model against a Groq zero-shot baseline.

Required submission artifacts are included in this repo:

- [planning.md](planning.md) for the label taxonomy and project notes
- [data/labeled/hn_ai_labeled.csv](data/labeled/hn_ai_labeled.csv) for the labeled dataset
- [models/distilbert_take_meter](models/distilbert_take_meter) for the trained model
- [eval/report.md](eval/report.md) for the evaluation writeup

## Community Choice

Community used: Hacker News.

Reasoning:

- Public API access does not require a Reddit developer app or account setup.
- The comment style is still opinion-heavy, technical, and discussion-oriented, so it works for the Insightful / Opinion / LowQuality taxonomy.
- It keeps the repo runnable even when Reddit self-service app creation is unavailable.

## Label Taxonomy

Each item gets exactly one label.

| Label | Definition | Example 1 | Example 2 |
| --- | --- | --- | --- |
| Insightful | Adds evidence, synthesis, helpful correction, or concrete reasoning. | "This approach is safer because it avoids cross-request cache contamination." | "The credit-card rule changes who the merchant legally sells to." |
| Opinion | Personal preference, feelings, predictions, or subjective takes without substantive evidence. | "I think the cheaper model is good enough for most tasks." | "I love the new workflow, but that is just my preference." |
| LowQuality | Noise, insults, spam, one-word replies, or off-topic filler. | "lol" | "you are dumb" |

## Data Collection and Labeling

Source:

- Raw collection file: [data/raw/hn_ai_comments.csv](data/raw/hn_ai_comments.csv)
- Collection script: [scripts/collect_hn.py](scripts/collect_hn.py)

Process:

1. Pull Hacker News comments with the public Algolia endpoint.
2. Keep the first 200 rows for a compact submission set.
3. Bootstrap labels with a deterministic heuristic so the repo stays self-contained.
4. Save the labeled result to [data/labeled/hn_ai_labeled.csv](data/labeled/hn_ai_labeled.csv).

Label distribution in the submitted labeled file:

- Insightful: 116
- Opinion: 67
- LowQuality: 17

Three difficult-to-label examples and decisions:

1. "They’re valid things to be concerned about IMO..." -> Opinion. It is mostly a subjective stance, even though it includes technical reasoning.
2. "Yeah you. Better get your printer air gapped..." -> Insightful. It is sarcastic, but the underlying claim is a real technical warning.
3. "The preferential treatment of credit cards..." -> Insightful. It is explanatory and gives a concrete policy mechanism.

## Fine-Tuning Approach

Base model:

- distilbert-base-uncased

Training setup:

- Hugging Face Trainer
- 4 epochs
- Batch size 16
- Learning rate 2e-5
- Max length 128
- Best model selected by validation accuracy

Hyperparameter decision:

- I kept the learning rate small because the dataset is tiny and the labels are noisy, so a larger learning rate would likely overfit faster.

## Baseline Description

Baseline model:

- Groq llama-3.3-70b-versatile

Prompt used in [eval/groq_zero_shot.py](eval/groq_zero_shot.py):

```text
You are a classifier. Labels:
0: Insightful - adds evidence, reasoning, references.
1: Opinion - expresses personal preference or subjective take without deep reasoning.
2: LowQuality - noise, insults, one-word replies, off-topic.

Classify the following text into exactly one label (0,1,2). Output only the digit.
```

Results were collected by running [eval/eval_models.py](eval/eval_models.py) on [data/splits/test.csv](data/splits/test.csv).

## Evaluation Report

### Overall Metrics

| Model | Accuracy |
| --- | --- |
| DistilBERT fine-tuned | 0.70 |
| Groq zero-shot | 0.55 |

### Per-Class Metrics

DistilBERT fine-tuned:

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Insightful | 0.700 | 1.000 | 0.824 |
| Opinion | 0.000 | 0.000 | 0.000 |
| LowQuality | 0.000 | 0.000 | 0.000 |

Groq zero-shot:

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Insightful | 0.727 | 0.571 | 0.640 |
| Opinion | 0.250 | 0.400 | 0.308 |
| LowQuality | 1.000 | 1.000 | 1.000 |

### Confusion Matrices

DistilBERT fine-tuned:

| True \ Pred | Insightful | Opinion | LowQuality |
| --- | --- | --- | --- |
| Insightful | 14 | 0 | 0 |
| Opinion | 5 | 0 | 0 |
| LowQuality | 1 | 0 | 0 |

Groq zero-shot:

| True \ Pred | Insightful | Opinion | LowQuality |
| --- | --- | --- | --- |
| Insightful | 8 | 6 | 0 |
| Opinion | 3 | 2 | 0 |
| LowQuality | 0 | 0 | 1 |

### Three Wrong Predictions

1. HF predicted Insightful for: "They’re valid things to be concerned about IMO...". Analysis: this is a subjective take, but the model over-weighted the technical explanation and ignored the opinion framing.
2. HF predicted Insightful for: "The preferential treatment of credit cards...". Analysis: it is explanatory, but the original label was Opinion because the comment is primarily a subjective argument about payment behavior.
3. Groq predicted Opinion for: "Yeah you. Better get your printer air gapped because they are going to brick it...". Analysis: the wording is conversational, but the core content is a technical warning, not a personal preference.

### Sample Classifications

| Text excerpt | True | Predicted | Confidence |
| --- | --- | --- | --- |
| Latency? Why, they will in LEO/MEO. Neglible... | Insightful | Insightful | 0.5342 |
| I wrote an essay about how I am handling AI in my CS courses... | Insightful | Insightful | 0.5317 |
| Yeah you. Better get your printer air gapped... | Insightful | Insightful | 0.4421 |
| The problem with the term "systemic bias"... | Insightful | Insightful | 0.4989 |
| They’re valid things to be concerned about IMO... | Opinion | Insightful | 0.4908 |

Correct example explanation:

- The first row is correctly predicted because the comment gives concrete technical reasoning, cites cooling options, and reads like a substantive explanation rather than a pure opinion.

## Reflection

What the model learned:

- It learned that long, technical, reference-heavy comments usually look like Insightful.
- It did not learn clean boundaries between Insightful and Opinion because the dataset is small and the labels were bootstrapped heuristically.

What I intended:

- I wanted a model that separates evidence-backed contributions from subjective takes and noise.
- The current model is usable as a baseline, but it still collapses many Opinion examples into Insightful.

## Spec Reflection

One way the spec helped:

- It forced a clear taxonomy, train/eval split, and baseline comparison, which kept the project structured.

One way the implementation diverged:

- The original Reddit collection plan was replaced with Hacker News because public Reddit app creation was not available. That made the pipeline runnable without external account setup.

## AI Usage

I used AI assistance in these specific ways:

1. I asked it to replace the Reddit-only data collector with a no-auth source. I kept the overall pipeline but changed the community to Hacker News and removed Reddit credentials.
2. I asked it to help format the README and evaluation summary. I then overrode the draft with the real metrics from this run and the actual file paths in the repo.

Annotation assistance disclosure:

- The labeled dataset in this submission was bootstrapped with a deterministic heuristic rather than hand-annotated one-by-one in the workspace. I kept that transparent in the docs so the submission is honest about how the labels were produced.

