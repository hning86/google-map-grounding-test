# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model            | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:-----------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3.5-flash | low      |   18.5391 |               0 |                      1 |                     1 |

## Detailed Analysis

**Total calls attempted:** 1
**Total successful calls:** 1
**Overall Success Rate:** 100.00%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
