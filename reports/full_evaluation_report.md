# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                  | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:-----------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3-flash-preview | low      |  18.7802  |        0.988764 |              0.0867309 |             0.0683253 |
| gemini-3-flash-preview | medium   |  23.3939  |        1        |              0.144718  |             0.129431  |
| gemini-3-flash-preview | high     |  25.5313  |        1        |              0.160179  |             0.15297   |
| gemini-3.1-flash-lite  | low      |   5.19894 |        0        |              1         |             1         |
| gemini-3.1-flash-lite  | medium   |   5.22094 |        0        |              1         |             1         |
| gemini-3.1-flash-lite  | high     |   5.7913  |        0        |              1         |             1         |
| gemini-3.1-pro-preview | low      |  18.078   |        0.955556 |              0.062963  |             0.062963  |
| gemini-3.1-pro-preview | medium   |  24.0428  |        1        |              0.0199074 |             0.0199074 |
| gemini-3.1-pro-preview | high     |  40.176   |        1        |              0.0516667 |             0.0516667 |
| gemini-3.5-flash       | low      |  14.2533  |        0.211111 |              0.805556  |             0.805556  |
| gemini-3.5-flash       | medium   |  26.0472  |        0.111111 |              0.895741  |             0.895741  |
| gemini-3.5-flash       | high     |  30.5648  |        0.155556 |              0.863757  |             0.863757  |

## Detailed Analysis

**Total calls attempted:** 1080
**Total successful calls:** 1078
**Overall Success Rate:** 99.81%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
