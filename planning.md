Label taxonomy (3 labels)

- Insightful
  - Definition: Adds evidence, synthesis, new perspective, or helpful correction. Useful, informative, and advances discussion.
  - Examples: short analyses, fact-backed claims, references, constructive clarifications.
  - Exclude: pure jokes, unverifiable claims without reasoning.

- Opinion
  - Definition: Personal preference, feelings, predictions, or subjective takes without extra evidence or deep reasoning.
  - Examples: "I love this movie", "I think X will happen".
  - Exclude: when the opinion includes reasoning/evidence -> Insightful.

- LowQuality
  - Definition: Noise: one-word replies, insults, spam, irrelevant content, repeated memes with no added content.
  - Examples: "lol", "you're dumb", off-topic copy-paste links.

Mutual exclusivity and coverage

- Each post should receive exactly one label.
- Edge cases:
  - Sarcasm with clear informative content -> Insightful.
  - Mixed: if a post has both opinion and a substantive reason, label Insightful.
  - If truly ambiguous (rare), choose the label you think the community would value more; track these in README.

Annotation notes

- Target >= 200 labeled examples.
- For each label include at least 20% of dataset to avoid heavy class imbalance when possible.
- Document three hard examples and final decision in README after annotation.

Modeling decisions

- Base model: distilbert-base-uncased (efficient & high quality).
- Fine-tune with Hugging Face Trainer.
- Zero-shot baseline: Groq llama-3.3-70b-versatile (prompt-based classification) for comparison.

Evaluation checklist

- Overall accuracy for both models.
- Per-class precision/recall/F1.
- Confusion matrix.
- At least 3 failure analyses and reflection on learned behavior vs intended.
