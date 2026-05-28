# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                  | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:-----------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3-flash-preview | low      |  17.2982  |             1   |               0.04     |              0.04     |
| gemini-3-flash-preview | medium   |  31.2713  |             1   |               0.116667 |              0.116667 |
| gemini-3-flash-preview | high     |  39.1011  |             1   |               0.232143 |              0.207143 |
| gemini-3.1-flash-lite  | low      |   5.09673 |             0   |               1        |              1        |
| gemini-3.1-flash-lite  | medium   |   7.95718 |             0   |               1        |              1        |
| gemini-3.1-flash-lite  | high     |   8.82634 |             0   |               1        |              1        |
| gemini-3.1-pro-preview | low      |  18.3985  |             1   |               0        |              0        |
| gemini-3.1-pro-preview | medium   |  23.3665  |             1   |               0.1      |              0.1      |
| gemini-3.1-pro-preview | high     |  37.7372  |             1   |               0.166667 |              0.166667 |
| gemini-3.5-flash       | low      |   9.30674 |             0   |               1        |              1        |
| gemini-3.5-flash       | medium   |  16.532   |             0.2 |               0.84     |              0.84     |
| gemini-3.5-flash       | high     |  32.5527  |             0   |               1        |              1        |

## Detailed Analysis

**Total calls attempted:** 60
**Total successful calls:** 60
**Overall Success Rate:** 100.00%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
