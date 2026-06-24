# Evaluation Report

This report summarizes the run produced by [eval/eval_models.py](eval_models.py) on [data/splits/test.csv](../data/splits/test.csv).

## Models

- Fine-tuned DistilBERT: [models/distilbert_take_meter](../models/distilbert_take_meter)
- Baseline: Groq llama-3.3-70b-versatile via [eval/groq_zero_shot.py](groq_zero_shot.py)

## Metrics

### DistilBERT

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Insightful | 0.700 | 1.000 | 0.824 |
| Opinion | 0.000 | 0.000 | 0.000 |
| LowQuality | 0.000 | 0.000 | 0.000 |

Accuracy: 0.70

Confusion matrix:

| True \ Pred | Insightful | Opinion | LowQuality |
| --- | --- | --- | --- |
| Insightful | 14 | 0 | 0 |
| Opinion | 5 | 0 | 0 |
| LowQuality | 1 | 0 | 0 |

### Groq zero-shot

| Label | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Insightful | 0.727 | 0.571 | 0.640 |
| Opinion | 0.250 | 0.400 | 0.308 |
| LowQuality | 1.000 | 1.000 | 1.000 |

Accuracy: 0.55

Confusion matrix:

| True \ Pred | Insightful | Opinion | LowQuality |
| --- | --- | --- | --- |
| Insightful | 8 | 6 | 0 |
| Opinion | 3 | 2 | 0 |
| LowQuality | 0 | 0 | 1 |

## Error Analysis

1. DistilBERT over-predicted Insightful across the test set. That is consistent with the bootstrap labels and the class imbalance in the labeled file.
2. Groq handled LowQuality well, but confused Insightful and Opinion when comments mixed technical reasoning with subjective framing.
3. The small test split means the metrics are indicative rather than stable.

## Sample Classifications

| Text excerpt | True | Predicted | Confidence |
| --- | --- | --- | --- |
| Latency? Why, they will in LEO/MEO. Neglible... | Insightful | Insightful | 0.5342 |
| I wrote an essay about how I am handling AI in my CS courses... | Insightful | Insightful | 0.5317 |
| Yeah you. Better get your printer air gapped... | Insightful | Insightful | 0.4421 |
| The problem with the term "systemic bias"... | Insightful | Insightful | 0.4989 |
| They’re valid things to be concerned about IMO... | Opinion | Insightful | 0.4908 |
