# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                         | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:------------------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3.1-flash-lite         | low      |   4.97269 |               0 |             1          |            1          |
| gemini-3.1-flash-lite         | medium   |   5.38961 |               0 |             1          |            1          |
| gemini-3.1-flash-lite         | high     |   6.00241 |               0 |             1          |            1          |
| gemini-3.1-flash-lite-preview | low      |   5.33227 |               1 |             0.0206614  |            0.00777778 |
| gemini-3.1-flash-lite-preview | medium   |   5.69022 |               1 |             0.0139815  |            0.00583333 |
| gemini-3.1-flash-lite-preview | high     |   5.79782 |               1 |             0.00185185 |            0.00185185 |

## Detailed Analysis

**Total calls attempted:** 540
**Total successful calls:** 539
**Overall Success Rate:** 99.81%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
