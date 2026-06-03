import json
import pandas as pd
import os
from rapidfuzz import fuzz

def analyze_results(input_file, output_report):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    data = []
    with open(input_file, "r") as f:
        for line in f:
            data.append(json.loads(line))
    
    df = pd.DataFrame(data)
    
    # Filter only successful calls for metrics
    df_success = df[df["success"] == True].copy()
    
    if df_success.empty:
        print("No successful calls to analyze.")
        return

    # 1. Latency Metrics
    latency_stats = df_success.groupby(["model", "effort"])["latency"].mean().reset_index()
    
    # 2. Grounded Response Rate
    # Fraction of successful responses with at least one grounding chunk
    df_success["is_grounded"] = df_success["grounding_chunks"].apply(lambda x: len(x) > 0)
    grounded_rate = df_success.groupby(["model", "effort"])["is_grounded"].mean().reset_index()
    grounded_rate.rename(columns={"is_grounded": "grounded_rate"}, inplace=True)
    
    # 3. Strict Mismatch Rate
    def calculate_mismatch_strict(row):
        try:
            places = json.loads(row["response_text"]).get("places", [])
        except:
            return 0
        
        if not places:
            return 0
        
        grounded_titles = [c["title"].lower().strip() for c in row["grounding_chunks"]]
        
        mismatches = 0
        for p in places:
            title = p.get("title", "").lower().strip()
            if title not in grounded_titles:
                mismatches += 1
        
        return mismatches / len(places)

    # 4. Fuzzy Mismatch Rate
    def calculate_mismatch_fuzzy(row):
        try:
            places = json.loads(row["response_text"]).get("places", [])
        except:
            return 0
        
        if not places:
            return 0
        
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
    
    strict_mismatch_stats = df_success.groupby(["model", "effort"])["strict_mismatch_rate"].mean().reset_index()
    fuzzy_mismatch_stats = df_success.groupby(["model", "effort"])["fuzzy_mismatch_rate"].mean().reset_index()
    
    # Merge results
    results = latency_stats.merge(grounded_rate, on=["model", "effort"])
    results = results.merge(strict_mismatch_stats, on=["model", "effort"])
    results = results.merge(fuzzy_mismatch_stats, on=["model", "effort"])
    
    # Sort by model, then by effort (low, medium, high)
    results["effort"] = pd.Categorical(results["effort"], categories=["low", "medium", "high"], ordered=True)
    results = results.sort_values(by=["model", "effort"]).reset_index(drop=True)
    
    # Create Markdown Report
    if os.path.dirname(output_report):
        os.makedirs(os.path.dirname(output_report), exist_ok=True)
    with open(output_report, "w") as f:
        f.write("# Gemini Evaluation Report: POI Discovery with Maps Grounding\n\n")
        f.write("## Summary Metrics\n\n")
        f.write(results.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("## Detailed Analysis\n\n")
        f.write(f"**Total calls attempted:** {len(df)}\n")
        f.write(f"**Total successful calls:** {len(df_success)}\n")
        f.write(f"**Overall Success Rate:** {len(df_success)/len(df):.2%}\n\n")
        
        f.write("### Latency by Model and Reasoning Effort\n")
        f.write("Lower is better.\n\n")
        
        f.write("### Grounded Response Rate\n")
        f.write("Higher is better. Indicates how often the model successfully used the Maps tool.\n\n")
        
        f.write("### Mismatch Rate\n")
        f.write("Lower is better. Measures hallucination vs. grounded data. We track two variants:\n")
        f.write("- **Strict Mismatch Rate:** Requires an exact normalized title match.\n")
        f.write("- **Fuzzy Mismatch Rate:** Employs Levenshtein token sort ratio matching with a threshold of >= 85%.\n")

    print(f"Analysis complete. Report saved to {output_report}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze Gemini evaluation raw results and compile markdown reports.")
    parser.add_argument("--input", type=str, help="Path to the input JSONL raw results file.")
    parser.add_argument("--output", type=str, help="Path to save the output markdown report.")
    parser.add_argument("--quick", action="store_true", help="Shortcut to use quick_test_results.jsonl and quick_test_report.md.")
    parser.add_argument("--priority", action="store_true", help="Analyze Priority PayGo evaluation results.")
    
    args = parser.parse_args()
    
    suffix = ""
    if args.priority:
        suffix = "_priority"
        
    # Determine input and output files
    if args.quick:
        input_file = os.path.join("results", f"quick_test_results{suffix}.jsonl")
        output_report = os.path.join("reports", f"quick_test_report{suffix}.md")
    else:
        input_file = args.input or os.path.join("results", f"full_eval_results{suffix}.jsonl")
        output_report = args.output or os.path.join("reports", f"full_evaluation_report{suffix}.md")
        
    analyze_results(input_file, output_report)
