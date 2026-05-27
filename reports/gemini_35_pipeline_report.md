# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model            | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:-----------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3.5-flash | low      |   27.9973 |               1 |               0.244381 |              0.210333 |
| gemini-3.5-flash | medium   |   37.2801 |               1 |               0.12654  |              0.119873 |
| gemini-3.5-flash | high     |   56.3726 |               1 |               0.335714 |              0.335714 |

## Detailed Analysis

**Total calls attempted:** 75
**Total successful calls:** 57
**Overall Success Rate:** 76.00%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
