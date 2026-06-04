# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                  | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:-----------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3-flash-preview | low      |  18.9357  |               1 |                      0 |                     0 |
| gemini-3.1-flash-lite  | low      |   6.26622 |               0 |                      1 |                     1 |
| gemini-3.1-pro-preview | low      |  22.0347  |               1 |                      0 |                     0 |
| gemini-3.5-flash       | low      |  12.7158  |               0 |                      1 |                     1 |

## Detailed Analysis

**Total calls attempted:** 4
**Total successful calls:** 4
**Overall Success Rate:** 100.00%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
