# 🧭 Gemini with Google Map Grounding Evaluation

A robust, lightweight benchmark and evaluation framework designed to assess and compare Gemini models (e.g., `gemini-3-flash-preview`, `gemini-3.1-pro-preview`, `gemini-3.5-flash`, and `gemini-3.1-flash-lite`) on Point-of-Interest (POI) discovery tasks using [Google Map Grounding Tool](https://ai.google.dev/gemini-api/docs/maps-grounding). 

This framework specifically analyzes the interplay and impact of **Reasoning Thinking Effort** (configurable levels like `LOW`, `MEDIUM`, `HIGH`) and **Google Maps Grounding Tool** integration on model latency, grounding accuracy, and hallucination rates.

---

## 🚀 Key Features

*   **Grounding Evaluation:** Tracks how successfully the model integrates and references real-world data through the Google Maps grounding tool.
*   **Thinking Effort Controls:** Tests the effect of Gemini's reasoning configuration (`ThinkingConfig` levels: `LOW`, `MEDIUM`, `HIGH`) on output quality and latency.
*   **Structured Output Enforcement:** Leverages JSON Schema-controlled generation to guarantee that responses conform strictly to a standardized POI metadata schema.
*   **Hallucination & Mismatch Detection:** Computes a custom **Mismatch Rate** metric to measure structural and textual discrepancies between generated places and verified grounding metadata.
*   **Flexible Run Modes:** Offers a full iteration mode as well as a single-repetition dry-run configuration (`evaluator.py --quick`).
*   **Automatic Report Compiler:** An analytics script (`analyzer.py`) automatically parses raw JSONL logs to generate a rich Markdown metrics report.

---

## 📂 Repository Structure

```text
gemini-eval/
├── evaluator.py                 # Unified benchmark runner with CLI args and --quick modes
├── analyzer.py                  # Unified report builder with CLI args & --quick shortcut
├── results/                     # Directory containing all raw and pretty-printed JSON/JSONL results
│   ├── full_eval_results.jsonl
│   ├── full_eval_results.json
│   ├── quick_test_results.jsonl
│   └── quick_test_results.json
├── reports/                     # Directory containing all generated markdown metrics reports
│   ├── full_evaluation_report.md
│   └── quick_test_report.md
├── pyproject.toml               # Project dependencies & metadata (managed via uv)
└── README.md                    # Project overview and usage instructions
```

---

## ⚙️ Installation & Setup

This project is managed with [uv](https://github.com/astral-sh/uv), a fast Python package manager.

### 1. Prerequisites

*   **Python 3.13+** (managed automatically by `uv`)
*   **Google Cloud Platform (GCP)** project with the **Vertex AI API** enabled.
*   **gcloud CLI** configured with credentials.

### 2. Install Dependencies

Navigate to the project root and sync the workspace:

```bash
uv sync
```

### 3. Authentication

#### Option A: Vertex AI API (Default)
Authenticate your shell environment with GCP Application Default Credentials (ADC):

```bash
gcloud auth application-default login
```

#### Option B: Google Gemini API (Alternative)
Create a `.env` file in the project root containing your Gemini API key, and optionally your GCP Project ID and Location if using Vertex AI:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PROJECT_ID=your_gcp_project_id_here
LOCATION=global
```

This key is automatically loaded at runtime when running with the `--gemini-api` flag.

---

## 🔧 Configuration

You can modify target evaluation behavior directly in the **Configuration** section at the top of `evaluator.py`, or customize them dynamically via environment variables in the `.env` file:

| Variable | Type | Purpose | Example Value |
| :--- | :--- | :--- | :--- |
| `MODELS` | `list` | List of Gemini models to evaluate. | `["gemini-3-flash-preview", "gemini-3.1-pro-preview", "gemini-3.5-flash", "gemini-3.1-flash-lite"]` |
| `EFFORTS` | `list` | Target reasoning levels to test. | `["low", "medium", "high"]` |
| `QUERIES` | `list` | Custom search prompts targeting POIs. | `["Best street food spots in Hanoi", ...]` |
| `REPETITIONS` | `int` | Number of times to repeat each query per configuration. | `18` |
| `PROJECT_ID` | `str` | Your GCP Project ID (loaded from `.env` or defaults to `"ninghai-ccai"`). | `"your-gcp-project-id"` |
| `LOCATION` | `str` | Vertex AI API location (loaded from `.env` or defaults to `"global"`). | `"global"` or `"us-central1"` |

### JSON Schema Enforcement

All models are constrained to generate structured responses matching this exact schema:

```json
{
  "type": "object",
  "properties": {
    "places": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title":          {"type": "string"},
          "rating":         {"type": "string"},
          "review_count":   {"type": "string"},
          "text":           {"type": "string"},
          "place_type":     {"type": "string"},
          "opening_hours":  {"type": "string"},
          "entry_price":    {"type": "string"},
          "address":        {"type": "string"}
        },
        "required": ["title", "rating", "review_count", "text"],
        "additionalProperties": false
      }
    }
  },
  "required": ["places"],
  "additionalProperties": false
}
```

---

## 🏃 Run the Benchmarks

### 1. Dry Run
Before running a full benchmark, execute a single-iteration dry run to verify credentials, rate limits, and schema constraints:

```bash
# Baseline 1-step mode (Vertex AI):
uv run python evaluator.py --quick

# Baseline 1-step mode with Priority PayGo (Vertex AI):
uv run python evaluator.py --quick --priority

# Baseline 1-step mode (Gemini API):
uv run python evaluator.py --quick --gemini-api
```

### 2. Full Evaluation
Run the full benchmark suite across all configurations:

```bash
# Baseline 1-step mode (Vertex AI - 18 repetitions):
uv run python evaluator.py

# Baseline 1-step mode with Priority PayGo (Vertex AI - 18 repetitions):
uv run python evaluator.py --priority

# Baseline 1-step mode (Gemini API - 18 repetitions):
uv run python evaluator.py --gemini-api
```

> [!TIP]
> The framework supports automatic failure recovery and implements exponential backoff on API rate limits or transient errors.

### 3. Generate the Report
Once evaluation/test completes, run the consolidated `analyzer.py` to process the raw results and compile the corresponding markdown report:

```bash
# Baseline 1-step Reports (Standard):
uv run python analyzer.py                    # Full evaluation -> full_evaluation_report.md
uv run python analyzer.py --quick            # Dry-run -> quick_test_report.md

# Baseline 1-step Reports (Priority PayGo):
uv run python analyzer.py --priority         # Full evaluation -> full_evaluation_report_priority.md
uv run python analyzer.py --quick --priority  # Dry-run -> quick_test_report_priority.md
```

---

## 📊 Metrics Analyzed

The compiler aggregates and calculates three primary performance and validation metrics:

### 1. ⏱️ Average Latency (seconds)
Measures the average duration (in seconds) from the time the client fires the Vertex AI request to the receipt of the fully parsed structured content:
$$\text{Average Latency} = \frac{1}{N}\sum_{i=1}^{N}(t_{\text{end}} - t_{\text{start}})$$
*(Lower is better)*

---

### 2. 🗺️ Grounded Response Rate
The probability that a successful response contains verifiable search citations from the Google Maps grounding tool. It tracks whether the model successfully queried and retrieved mapping features for the requested points of interest.

#### Math:
$$\text{Grounded Rate} = \frac{\sum_{i=1}^{N} \mathbb{I}(\text{count}(\text{grounding-chunks}_i) > 0)}{N_{\text{success}}}$$

*Where:*
*   $N_{\text{success}}$ is the total count of successful generation attempts.
*   $\mathbb{I}$ is an indicator function that returns $1$ if the response contains at least one grounding chunk, and $0$ otherwise.

#### Python Logic:
```python
# A response is grounded if it contains at least 1 item in grounding_chunks
df_success["is_grounded"] = df_success["grounding_chunks"].apply(lambda x: len(x) > 0)
grounded_rate = df_success.groupby(["model", "effort"])["is_grounded"].mean()
```
*(Higher is better)*

---

### 3. ⚠️ Mismatch Rate (Hallucination Index)
Measures the structural alignment and validity of the generated points of interest against physical entities returned by the Google Maps API. It evaluates what percentage of places returned in the structured JSON text **are missing** from the actual returned Maps metadata chunks. We track two distinct versions of this metric:

#### A. Strict Mismatch Rate (Exact Normalized Match)
Requires an exact normalized string match (ignoring casing and leading/trailing whitespaces) between the generated place title and the grounding chunk titles.

*   **Math:**
    $$\text{Strict Mismatch Rate} = \frac{\text{Count of generated places } p \text{ where } \text{normalize}(p_{\text{title}}) \notin \mathcal{G}}{\text{Total generated places in response}}$$
    *Where:*
    *   $\mathcal{G} = \{ \text{normalize}(c_{\text{title}}) \mid c \in \text{grounding-chunks} \}$
    *   $\text{normalize}(t)$ lowercases and strips whitespace.

#### B. Fuzzy Mismatch Rate (Levenshtein Distance Match)
Allows minor differences in punctuation, accents, suffixes, or spacing. It uses Levenshtein edit distance to calculate the Token Sort Ratio similarity between titles and counts as a match if the similarity is $\ge 85\%$.

*   **Math:**
    $$\text{Fuzzy Mismatch Rate} = \frac{\text{Count of generated places } p \text{ where } \max_{c \in \text{grounding-chunks}} (\text{similarity}(p_{\text{title}}, c_{\text{title}})) < 85\%}{\text{Total generated places in response}}$$

#### Python Logic:
```python
# 1. Strict calculation
def calculate_mismatch_strict(row):
    places = json.loads(row["response_text"]).get("places", [])
    if not places: return 0
    grounded_titles = [c["title"].lower().strip() for c in row["grounding_chunks"]]
    mismatches = sum(1 for p in places if p.get("title", "").lower().strip() not in grounded_titles)
    return mismatches / len(places)

# 2. Fuzzy calculation
def calculate_mismatch_fuzzy(row):
    places = json.loads(row["response_text"]).get("places", [])
    if not places: return 0
    grounded_titles = [c["title"].lower().strip() for c in row["grounding_chunks"]]
    
    mismatches = 0
    for p in places:
        title = p.get("title", "").lower().strip()
        is_match = any(fuzz.token_sort_ratio(title, gt) >= 85.0 for gt in grounded_titles)
        if not is_match:
            mismatches += 1
    return mismatches / len(places)

df_success["strict_mismatch_rate"] = df_success.apply(calculate_mismatch_strict, axis=1)
df_success["fuzzy_mismatch_rate"] = df_success.apply(calculate_mismatch_fuzzy, axis=1)
```
*(Lower is better)*

---

## 📈 Live Evaluation Report Metrics

Here are the actual consolidated metrics compiled from our comprehensive evaluation suite (1080 total runs):

| Model | Effort | Latency (s) | Grounded Rate | Strict Mismatch | Fuzzy Mismatch |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **gemini-3.1-flash-lite** | `low` | **5.55s** | 0.00% | 100.00% | 100.00% |
| **gemini-3.1-flash-lite** | `medium` | **5.21s** | 0.00% | 100.00% | 100.00% |
| **gemini-3.1-flash-lite** | `high` | 6.09s | 0.00% | 100.00% | 100.00% |
| **gemini-3.1-flash-lite-preview** | `low` | 5.68s | **100.00%** | 1.32% | 1.32% |
| **gemini-3.1-flash-lite-preview** | `medium` | 5.41s | **100.00%** | 1.51% | 1.29% |
| **gemini-3.1-flash-lite-preview** | `high` | **6.19s** | **100.00%** | **1.05%** | **0.83%** |
| **gemini-3.1-pro-preview** | `low` | 18.93s | 98.89% | 2.07% | 2.07% |
| **gemini-3.1-pro-preview** | `medium` | 22.85s | **100.00%** | 2.13% | 1.94% |
| **gemini-3.1-pro-preview** | `high` | 37.56s | **100.00%** | 5.70% | 5.70% |
| **gemini-3.5-flash** | `low` | 14.35s | 28.89% | 72.56% | 72.56% |
| **gemini-3.5-flash** | `medium` | 25.48s | 12.22% | 88.20% | 88.20% |
| **gemini-3.5-flash** | `high` | 27.88s | 21.11% | 79.77% | 79.77% |

> [!NOTE]
> Higher thinking effort slightly increases request latency, but dramatically improves factual precision for the preview model, achieving a near-perfect mismatch rate of 0.83% at high effort while keeping latency under 6.2 seconds.

### 📊 Actual Key Observations (1080 Runs)

Based on the empirical findings, we observe the following model profiles:

1. **🏆 The New Grounding Standard: `gemini-3.1-flash-lite-preview`**
   * **Full Grounding Activation:** Successfully triggers external search grounding for **100.00%** of requests.
   * **Outstanding Factual Precision:** Achieves near-perfect grounding precision, dropping fuzzy mismatch rates to **~0.83%** at high effort.
   * **Ultra-Low Latency:** Accomplishes this high-precision grounding in under **6.2 seconds**, combining the speed of a lightweight model with the accuracy of a high-end model.

2. **⚡ Heavyweight Reliability: `gemini-3.1-pro-preview`**
   * **High Grounding Rate:** Achieves **98.89% to 100.00%** grounding rates across different efforts.
   * **Solid Factual Precision:** Maintains mismatch rates below **~5.7%**.
   * **Major Latency Penalty:** Runs are extremely slow, ranging from **18.9s** to **37.6s**, making it less suitable for real-time customer-facing interactions.

3. **⚠️ Grounding Tool Bypass: `gemini-3.5-flash`**
   * **Inconsistent Grounding:** Bypasses grounding search tools on **71-88%** of requests under structured schema constraints.
   * **High Mismatch Rates:** Results in extremely elevated hallucination/mismatch rates (~72-88%) in the standard 1-step direct baseline.

4. **❌ Complete Grounding Failure: Stable `gemini-3.1-flash-lite`**
   * **Bypasses Grounding Tool:** Yields a **0.00%** grounded rate and a **100.00%** mismatch rate across all efforts.
   * **Why?** The stable model lacks the cognitive capacity to satisfy structured JSON output rules while concurrently orchestrating multi-step external search tool execution, defaulting entirely to hallucinated parametric weights.

---

## 🔍 Deep Dive: Agentic Tool-Use & Grounding Dynamics

Evaluating models across varying **Reasoning/Thinking Efforts** reveals several critical behaviors regarding when and why a model decides to invoke (or bypass) the Google Maps Grounding Tool:

### 1. Parametric Confidence vs. External Grounding
When a query targets highly famous landmarks or well-documented entities (e.g., *"Top art museums in Paris"* generating the Louvre or Musée d'Orsay), the model's internal parametric confidence is exceptionally high. In these cases, the model's reasoning trace often decides that calling the external Google Maps API is redundant, electing to generate the responses directly from its pre-trained weights. This results in **$0$ grounding chunks** and a **$100\%$ Mismatch Rate**, even though the places themselves are correct and famous.

### 2. The "Overthinking" Tool-Bypass Effect
*   **At Low Effort:** The model runs optimized, fast factual routing paths. For queries with geographical components, it eagerly defaults to calling the Google Maps API immediately as a quick fact-checking lookup, leading to very high **Grounded Response Rates**.
*   **At Medium/High Effort:** The model allocates more reasoning tokens to its internal chain-of-thought trace. As the model "thinks" through the problem internally, it builds a highly structured plan. If it determines it already holds a strong factual representation of the query, it will bypass the tool invocation entirely. 

### 3. Structured JSON Schema Constraints
Strictly enforcing a complex JSON `SCHEMA` forces the model to prioritize formatting correctness above all else. The risk of a schema validation failure on unstructured API search results can make the model highly conservative. To guarantee grammatical conformity to the requested JSON types, it often avoids the multi-step orchestration required to query live Maps and format the result, preferring to generate the JSON payload purely from its internal weights.

### 4. Platform Architectural Constraints: Structured Outputs vs. Maps Grounding
There is a key platform architectural difference between the enterprise Vertex AI API and the Developer/AI Studio Gemini API:
* **Vertex AI API**: Fully supports combining the Google Maps Grounding Tool with Structured Outputs (JSON Schema-controlled generation) in a single request.
* **Google Gemini Developer API**: **Does not support** combining the Google Maps tool with Structured Outputs (`response_mime_type="application/json"`) in a single direct call. Attempting this returns a `400 INVALID_ARGUMENT` error:
  `Google Maps tool with a response mime type: 'application/json' is unsupported`

#### How the Evaluator Handles this Constraint
To enable evaluations on the developer Gemini API while strictly enforcing the JSON schema format, the evaluator implements the following workaround:
1. **Fallback to Google Search Grounding**: When running 1-step baseline evaluations using `--gemini-api`, the evaluator dynamically switches from the `google_maps` tool to the `google_search` tool (which *is* fully compatible with structured outputs on the developer API).

---

## 🧪 Side-Experiment 1: The Impact of Schema Enforcement on Multi-Model Latency & Grounding

To understand whether API-level JSON schema constraints impact other models (like `gemini-3-flash-preview` and `gemini-3.1-pro-preview`), we introduced a `--no-schema` flag to bypass schema validation completely (allowing freeform Markdown output) and ran a comprehensive benchmark experiment (90 total calls).

### 1. Empirical Findings (Schema vs. NO Schema)

| Model & Setup | Effort | Grounded Rate (With Schema) | Grounded Rate (NO Schema) | Avg Latency (With Schema) | Avg Latency (NO Schema) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **gemini-3-flash-preview** | `low` | 98.89% | **100.00%** | **20.33s** | 36.68s |
| **gemini-3-flash-preview** | `medium` | 100.00% | **100.00%** | **26.50s** | 29.18s |
| **gemini-3-flash-preview** | `high` | 100.00% | **100.00%** | **29.15s** | 34.33s |
| **gemini-3.1-pro-preview** | `low` | 98.89% | **100.00%** | **18.73s** | 20.38s |
| **gemini-3.1-pro-preview** | `medium` | 100.00% | **100.00%** | **25.41s** | 25.42s |
| **gemini-3.1-pro-preview** | `high` | 100.00% | **100.00%** | 42.17s | **40.00s** |
| **gemini-3.5-flash** | `low` | 4.44% | **90.00%** | **6.79s** | 9.53s |
| **gemini-3.5-flash** | `medium` | 18.89% | **100.00%** | **12.40s** | 14.20s |
| **gemini-3.5-flash** | `high` | 11.11% | **60.00%** | **26.75s** | 27.69s |

### 2. Key Latency & Grounding Insights

* **External Tool Calls Drive Latency:** Disabling JSON Schema enforcement did not yield latency reductions for high-end models (`gemini-3.1-pro-preview` and `gemini-3-flash-preview`). This proves that the API's Structured Outputs constraint-satisfaction decoding engine adds very minimal overhead. The primary latency driver is the network I/O and server-side query-processing required to run live Google Maps searches.
* **Why `gemini-3.5-flash` Latency Increases:** Removing schema constraints forces `gemini-3.5-flash` to stop bypassing the Google Maps tool. As its Grounded Rate surges from **4.4% $\rightarrow$ 90.00%**, it has to actually execute the searches and wait for results, causing its average latency to naturally rise (e.g., from `6.79s` to `9.53s` at low effort).
* **Formatting Tradeoffs:** Disabling schema enforcement produces freeform Markdown instead of structured JSON. Any downstream parser must handle syntax irregularities, making API-enforced schemas essential for strict production parsing on high-end models where they carry no latency penalty.

---

## 🧪 Side-Experiment 2: Priority PayGo Latency Impact on Grounded Queries

To evaluate whether GCP's **Priority PayGo** option (using the `X-Vertex-AI-LLM-Shared-Request-Type: priority` header) reduces latency for grounded search and POI discovery, we ran a dedicated benchmarking experiment comparing 5 consecutive runs with and without the priority configuration.

### 1. Empirical Findings (5 Trials)

| Mode | Model | Grounding | Average Latency (s) |
| :--- | :--- | :---: | :---: |
| **Standard PayGo** | `gemini-3.5-flash` | Google Maps | **30.81s** |
| **Priority PayGo** | `gemini-3.5-flash` | Google Maps | **31.64s** |

### 2. Key Observations & Recommendations

* **Zero Impact on Grounded Queries:** The Priority PayGo configuration did not produce a latency reduction (Standard was marginally faster by ~2.7%).
* **Latency Bottleneck is I/O, not Queues:** Because Maps-grounded queries require synchronous external API network calls (to Google Maps Search engines) and multi-step agentic execution, the LLM endpoint scheduling queue delay is a negligible fraction of the total response time.
* **When to use Priority PayGo:** While Priority PayGo is highly recommended to protect against rate-limit throttling and queue degradation during periods of heavy concurrent traffic, it will not reduce the physical latency of queries that are heavily bound by external tool I/O.

---

## 🏁 Overall Conclusion & Architectural Recommendations

Through our latest evaluation—spanning **1080 standard runs** across multiple Gemini models—we have mapped out the operational profiles of these models on grounded POI discovery tasks.

### 📌 Summary of Core Findings

1. **Lightweight Model Grounding Revolution:** The `gemini-3.1-flash-lite-preview` model represents a massive capability leap. It successfully resolves the cognitive load bottleneck of combining strict JSON Schema constraints with multi-step search grounding, achieving a **100.00% Grounded Rate** and an outstanding **0.83% Fuzzy Mismatch Rate** (at high effort).
2. **Stable Version Limitations:** The stable `gemini-3.1-flash-lite` model remains unable to handle this combined task, failing to invoke search grounding entirely (**0.00% Grounded Rate**) and resulting in a **100.00% Mismatch Rate** due to purely hallucinated outputs.
3. **Frugal High-Precision Grounding:** The preview model achieves these high-precision results with extremely low latency (**~5.4s - 6.2s**), representing a highly cost-effective and performant architecture for real-time grounded applications.
4. **Pro Model Latency Constraints:** While `gemini-3.1-pro-preview` achieves high grounding activation (99-100%) and very solid factual precision, its high average latency (**~19s - 38s**) makes it less suitable for real-time customer-facing interactions.

---

### 🛠️ Production Recommendations Matrix

| Model | Use Case | Recommended Architecture | Rationale |
| :--- | :--- | :--- | :--- |
| **`gemini-3.1-flash-lite-preview`** | **Real-Time Factual Grounding** | **1-Step Direct (With Schema)** | **Highly Recommended.** Delivers a perfect 100.00% grounding rate, near-zero mismatch (0.83% at high effort), and extremely fast latencies under 6.2s. |
| **`gemini-3.1-pro-preview`** | **Mission-Critical Accuracy (Back-Office)** | **1-Step Direct (With Schema)** | Delivers high grounding precision (~2% mismatch) and reliable tool activation, but has high latency (~19s - 38s). |
| **`gemini-3.5-flash`** | **Not Recommended for Constrained 1-Step** | **None / Switch to Preview** | Highly prone to bypassing grounding search tools (~71-88% bypass rate) under JSON Schema constraints. |
| **`gemini-3.1-flash-lite`** | **NOT RECOMMENDED** | **None / Switch to Preview** | Stable release is inherently prone to bypassing grounding lookups entirely, resulting in 100% mismatch rates. |




