# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                  | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:-----------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3-flash-preview | low      |  20.3325  |       0.988889  |              0.107606  |             0.0935317 |
| gemini-3-flash-preview | medium   |  26.4971  |       1         |              0.169021  |             0.156865  |
| gemini-3-flash-preview | high     |  29.1521  |       1         |              0.169715  |             0.159821  |
| gemini-3.1-pro-preview | low      |  18.727   |       0.988889  |              0.0111111 |             0.0111111 |
| gemini-3.1-pro-preview | medium   |  25.4087  |       1         |              0.0114815 |             0.0114815 |
| gemini-3.1-pro-preview | high     |  42.172   |       1         |              0.0700397 |             0.0700397 |
| gemini-3.5-flash       | low      |   6.78551 |       0.0444444 |              0.960556  |             0.960556  |
| gemini-3.5-flash       | medium   |  12.3965  |       0.188889  |              0.834074  |             0.834074  |
| gemini-3.5-flash       | high     |  26.745   |       0.111111  |              0.893333  |             0.893333  |

## Detailed Analysis

**Total calls attempted:** 810
**Total successful calls:** 808
**Overall Success Rate:** 99.75%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
