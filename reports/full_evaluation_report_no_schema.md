# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                  | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:-----------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3-flash-preview | low      |  36.6846  |             1   |                      0 |                     0 |
| gemini-3-flash-preview | medium   |  29.1757  |             1   |                      0 |                     0 |
| gemini-3-flash-preview | high     |  34.3319  |             1   |                      0 |                     0 |
| gemini-3.1-pro-preview | low      |  20.3753  |             1   |                      0 |                     0 |
| gemini-3.1-pro-preview | medium   |  25.4237  |             1   |                      0 |                     0 |
| gemini-3.1-pro-preview | high     |  40.0013  |             1   |                      0 |                     0 |
| gemini-3.5-flash       | low      |   9.53231 |             0.9 |                      0 |                     0 |
| gemini-3.5-flash       | medium   |  14.2038  |             1   |                      0 |                     0 |
| gemini-3.5-flash       | high     |  27.6908  |             0.6 |                      0 |                     0 |

## Detailed Analysis

**Total calls attempted:** 90
**Total successful calls:** 90
**Overall Success Rate:** 100.00%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
