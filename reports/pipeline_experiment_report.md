# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                 | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:----------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3.1-flash-lite | low      |   22.8091 |            0.4  |               0.617381 |              0.611667 |
| gemini-3.1-flash-lite | medium   |   20.6739 |            0.64 |               0.465    |              0.423333 |
| gemini-3.1-flash-lite | high     |   21.4143 |            0.16 |               0.855    |              0.855    |
| gemini-3.5-flash      | low      |   33.4281 |            1    |               0.181143 |              0.165143 |
| gemini-3.5-flash      | medium   |   37.2824 |            1    |               0.247667 |              0.239667 |
| gemini-3.5-flash      | high     |   59.7445 |            1    |               0.285334 |              0.258433 |

## Detailed Analysis

**Total calls attempted:** 150
**Total successful calls:** 149
**Overall Success Rate:** 99.33%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
