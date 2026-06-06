# Gemini Evaluation Report: POI Discovery with Maps Grounding

## Summary Metrics

| model                         | effort   |   latency |   grounded_rate |   strict_mismatch_rate |   fuzzy_mismatch_rate |
|:------------------------------|:---------|----------:|----------------:|-----------------------:|----------------------:|
| gemini-3.1-flash-lite         | low      |   5.55287 |        0        |              1         |            1          |
| gemini-3.1-flash-lite         | medium   |   5.20979 |        0        |              1         |            1          |
| gemini-3.1-flash-lite         | high     |   6.08973 |        0        |              1         |            1          |
| gemini-3.1-flash-lite-preview | low      |   5.67987 |        1        |              0.0131746 |            0.0131746  |
| gemini-3.1-flash-lite-preview | medium   |   5.40613 |        1        |              0.0150926 |            0.0128704  |
| gemini-3.1-flash-lite-preview | high     |   6.19491 |        1        |              0.0104762 |            0.00825397 |
| gemini-3.1-pro-preview        | low      |  18.9337  |        0.988889 |              0.0207407 |            0.0207407  |
| gemini-3.1-pro-preview        | medium   |  22.8476  |        1        |              0.0212963 |            0.0194444  |
| gemini-3.1-pro-preview        | high     |  37.5588  |        1        |              0.057037  |            0.057037   |
| gemini-3.5-flash              | low      |  14.3489  |        0.288889 |              0.725556  |            0.725556   |
| gemini-3.5-flash              | medium   |  25.481   |        0.122222 |              0.882037  |            0.882037   |
| gemini-3.5-flash              | high     |  27.8822  |        0.211111 |              0.797698  |            0.797698   |

## Detailed Analysis

**Total calls attempted:** 1080
**Total successful calls:** 1080
**Overall Success Rate:** 100.00%

### Latency by Model and Reasoning Effort
Lower is better.

### Grounded Response Rate
Higher is better. Indicates how often the model successfully used the Maps tool.

### Mismatch Rate
Lower is better. Measures hallucination vs. grounded data. We track two variants:
- **Strict Mismatch Rate:** Requires an exact normalized title match.
- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.
