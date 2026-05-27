# 🧭 Gemini with Google Map Grounding Evaluation

A robust, lightweight benchmark and evaluation framework designed to assess and compare Gemini models (e.g., `gemini-3-flash-preview`, `gemini-3.1-pro-preview`, and `gemini-3.5-flash`) on Point-of-Interest (POI) discovery tasks using [Google Map Grounding Tool](https://ai.google.dev/gemini-api/docs/maps-grounding). 

This framework specifically analyzes the interplay and impact of **Reasoning Thinking Effort** (configurable levels like `LOW`, `MEDIUM`, `HIGH`) and **Google Maps Grounding Tool** integration on model latency, grounding accuracy, and hallucination rates.

---

## 🚀 Key Features

*   **Grounding Evaluation:** Tracks how successfully the model integrates and references real-world data through the Google Maps grounding tool.
*   **Thinking Effort Controls:** Tests the effect of Gemini's reasoning configuration (`ThinkingConfig` levels: `LOW`, `MEDIUM`, `HIGH`) on output quality and latency.
*   **Structured Output Enforcement:** Leverages JSON Schema-controlled generation to guarantee that responses conform strictly to a standardized POI metadata schema.
*   **Hallucination & Mismatch Detection:** Computes a custom **Mismatch Rate** metric to measure structural and textual discrepancies between generated places and verified grounding metadata.
*   **Flexible Run Modes:** Offers a full iteration mode (`evaluator.py`) as well as a single-repetition debug setup (`dry_run.py`).
*   **Automatic Report Compiler:** An analytics script (`analyzer.py`) automatically parses raw JSONL logs to generate a rich Markdown metrics report.

---

## 📂 Repository Structure

```text
gemini-eval/
├── evaluator.py                 # Unified benchmark runner with CLI args, --quick, and --pipeline modes
├── analyzer.py                  # Unified report builder with CLI args & --quick shortcut
├── pipeline_experiment.py       # Dedicated side-experiment for gemini-3.5-flash pipeline
├── result/                      # Directory containing all raw and pretty-printed JSON/JSONL results
│   ├── full_eval_results.jsonl
│   ├── full_eval_results.json
│   ├── quick_test_results.jsonl
│   ├── quick_test_results.json
│   ├── pipeline_quick_results.jsonl
│   ├── pipeline_quick_results.json
│   └── gemini_35_pipeline_results.jsonl
├── reports/                     # Directory containing all generated markdown metrics reports
│   ├── full_evaluation_report.md
│   ├── quick_test_report.md
│   ├── pipeline_quick_report.md
│   └── gemini_35_pipeline_report.md
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

Authenticate your shell environment with GCP Application Default Credentials (ADC):

```bash
gcloud auth application-default login
```

---

## 🔧 Configuration

You can modify target evaluation behavior directly in the **Configuration** section at the top of `evaluator.py` and `dry_run.py`:

| Variable | Type | Purpose | Example Value |
| :--- | :--- | :--- | :--- |
| `MODELS` | `list` | List of Gemini models to evaluate. | `["gemini-3-flash-preview", "gemini-3.1-pro-preview", "gemini-3.5-flash"]` |
| `EFFORTS` | `list` | Target reasoning levels to test. | `["low", "medium", "high"]` |
| `QUERIES` | `list` | Custom search prompts targeting POIs. | `["Best street food spots in Hanoi", ...]` |
| `REPETITIONS` | `int` | Number of times to repeat each query per configuration. | `18` |
| `PROJECT_ID` | `str` | Your GCP Project ID. | `"your-gcp-project-id"` |
| `LOCATION` | `str` | Vertex AI API location. | `"global"` or `"us-central1"` |

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
# Baseline 1-step mode:
uv run python evaluator.py --quick

# Advanced 2-step pipeline mode (Strategy 1 + 2):
uv run python evaluator.py --quick --pipeline
```

### 2. Full Evaluation
Run the full benchmark suite across all configurations:

```bash
# Baseline 1-step mode (18 repetitions):
uv run python evaluator.py

# Advanced 2-step pipeline mode (18 repetitions):
uv run python evaluator.py --pipeline

# Customize repetitions (e.g., 5 reps):
uv run python evaluator.py --pipeline --repetitions 5
```

> [!TIP]
> The framework supports automatic failure recovery and implements exponential backoff on API rate limits or transient errors.

### 3. Generate the Report
Once evaluation/test completes, run the consolidated `analyzer.py` to process the raw results and compile the corresponding markdown report:

```bash
# Baseline 1-step Reports:
uv run python analyzer.py                    # Full evaluation -> full_evaluation_report.md
uv run python analyzer.py --quick            # Dry-run -> quick_test_report.md

# Advanced 2-step Pipeline Reports:
uv run python analyzer.py --input pipeline_eval_results.jsonl --output pipeline_evaluation_report.md
uv run python analyzer.py --input pipeline_quick_results.jsonl --output pipeline_quick_report.md
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

Here are the actual consolidated metrics compiled from our comprehensive evaluation suite (810 total runs):

| Model | Effort | Latency (s) | Grounded Rate | Strict Mismatch | Fuzzy Mismatch |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **gemini-3-flash-preview** | `low` | 20.33s | 98.89% | 10.76% | 9.35% |
| **gemini-3-flash-preview** | `medium` | 26.50s | 100.00% | 16.90% | 15.69% |
| **gemini-3-flash-preview** | `high` | 29.15s | 100.00% | 16.97% | 15.98% |
| **gemini-3.1-pro-preview** | `low` | 18.73s | 98.89% | 1.11% | 1.11% |
| **gemini-3.1-pro-preview** | `medium` | 25.41s | 100.00% | 1.15% | 1.15% |
| **gemini-3.1-pro-preview** | `high` | 42.17s | 100.00% | 7.00% | 7.00% |
| **gemini-3.5-flash** | `low` | **6.79s** | 4.44% | 96.06% | 96.06% |
| **gemini-3.5-flash** | `medium` | 12.40s | 18.89% | 83.41% | 83.41% |
| **gemini-3.5-flash** | `high` | 26.75s | 11.11% | 89.33% | 89.33% |

> [!NOTE]
> Higher thinking effort directly increases request latency across all models, while also altering how aggressively a model relies on active grounding tools versus its internal parametric weights.

### 📊 Actual Key Observations (810 Runs)

Based on the empirical findings, we observe the following model profiles:

1. **🏆 The Grounding Gold Standard: `gemini-3.1-pro-preview`**
   * **Factual Precision:** Achieves an outstanding mismatch rate of **~1.11%** at `low` and `medium` efforts, representing near-perfect grounding precision.
   * **The High Effort Penalty:** Increasing effort to `high` increases latency to **42.17s** and actually degrades mismatch rate to **7.00%**. `low` or `medium` are the optimal configurations for production.

2. **⚡ Reliable & Sturdy: `gemini-3-flash-preview`**
   * **Strong Consistency:** Maintains a **99% to 100%** grounding rate across all configurations.
   * **Optimal Setup:** At `low` effort, it yields a strong strict mismatch rate of **10.76%** in only **20.33s**—making it the best balanced option for real-time applications.

3. **⚠️ The Grounding Exception: `gemini-3.5-flash`**
   * **Super Fast but Bypasses Grounding:** While incredibly fast at `low` effort (**6.79s**), it has a critically low grounding rate (**4.44%**) and a massive mismatch rate of **96.06%**.
   * **Why?** It prioritizes JSON schema compliance and speedy internal generation, electing to skip multi-step external tool grounding in favor of parametric memory.

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

---

## 🧪 Side-Experiment: Resolving `gemini-3.5-flash` Grounding Failure with a 2-Stage Pipeline

During our 810 baseline runs, we observed a critical anomaly: **`gemini-3.5-flash` bypassed the Google Maps Grounding Tool** almost entirely, resulting in a grounded rate of only **4.44%** and an alarming mismatch/hallucination rate of **96.06%** at `low` effort. 

To investigate and resolve this, we designed and executed a dedicated side-experiment using a **2-Stage Agentic Pipeline**.

### 1. Why `gemini-3.5-flash` Bypassed Grounding in 1-Step Baseline
When a model is forced to use external tools *and* strictly adhere to a complex JSON `SCHEMA` in a single API call, it suffers from severe cognitive load. To guarantee 100% formatting correctness and avoid structural validation failures on live, unstructured search data, the model becomes highly conservative. It elects to bypass external multi-step tool calls entirely, generating the structured JSON payload rapidly from its pre-trained parametric weights.

### 2. The 2-Stage Pipeline Solution
We decoupled the cognitive task into two distinct stages:
1. **Stage 1 (Searcher Agent):** We tasked `gemini-3.5-flash` with finding candidate places and outputting them in raw, unstructured Markdown. **No JSON schema was enforced in this call.** The model was completely free to query and verify data using the Google Maps tool.
2. **Stage 2 (Parser Agent):** We took the raw Markdown output from Stage 1 and passed it to a fast, schema-constrained parser (running standard `gemini-3.5-flash`) whose only job was to extract that data into the target JSON Schema.

### 3. Empirical Results
Running the 2-stage pipeline side-experiment (5 repetitions across all efforts and queries) yielded dramatic improvements:

| Model & Setup | Effort | Avg Latency (s) | Grounded Rate | Strict Mismatch | Fuzzy Mismatch |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **gemini-3.5-flash (1-Step Baseline)** | `low` | 6.79s | 4.44% | 96.06% | 96.06% |
| **gemini-3.5-flash (2-Step Pipeline)** | `low` | 27.99s | **100.00%** | **24.44%** | **21.03%** |
| **gemini-3.5-flash (1-Step Baseline)** | `medium` | 12.40s | 18.89% | 83.41% | 83.41% |
| **gemini-3.5-flash (2-Step Pipeline)** | `medium` | 37.28s | **100.00%** | **12.65%** (Best) | **11.99%** |
| **gemini-3.5-flash (1-Step Baseline)** | `high` | 26.75s | 11.11% | 89.33% | 89.33% |
| **gemini-3.5-flash (2-Step Pipeline)** | `high` | 56.37s | **100.00%** | **33.57%** | **33.57%** |

* **Grounding Rate Spikes to 100.00%:** Removing the schema constraints in the initial call completely unblocked the model's tool usage. It invoked the Google Maps tool for 100% of the tasks.
* **Hallucinations Drop to 12.65%:** At `medium` effort, the factual mismatch rate dropped from a massive **83.41%** down to just **12.65%**, proving that the model can be highly precise when structured properly.

### 4. Latency Implications
The pipeline introduces a critical tradeoff between **latency** and **precision**:
* **Sequential Overhead:** Executing two sequential API calls (Searcher $\rightarrow$ Parser) and waiting for active Google Maps search results significantly increases individual request latency (e.g., from **6.79s** to **27.99s** at `low` effort).
* **Recommendation:** For fast-turnaround UX, the 1-step baseline model is preferred, but for tasks requiring strict real-world factuality and verification, the 2-stage pipeline is mandatory.

---

## 🧪 Side-Experiment 2: The Impact of Schema Enforcement on Multi-Model Latency & Grounding

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


