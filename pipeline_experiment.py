import os
from evaluator import run_evaluation
from analyzer import analyze_results

if __name__ == "__main__":
    output_file = os.path.join("result", "gemini_35_pipeline_results.jsonl")
    report_file = os.path.join("reports", "gemini_35_pipeline_report.md")
    
    # Clean up any previous results
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except:
            pass
            
    # Run for gemini-3.5-flash only across all efforts and queries, with 5 repetitions
    run_evaluation(
        output_file=output_file,
        repetitions=5,
        models=["gemini-3.5-flash"],
        efforts=["low", "medium", "high"],
        queries=[
            "Best street food spots and street food markets in Hanoi",
            "Best vegan restaurants in Berlin",
            "Top art museums and galleries in Paris",
            "Hidden specialty coffee shops in Tokyo",
            "Best rooftop bars with a view in Bangkok"
        ],
        use_pipeline=True,
        workers=8
    )
    
    print("Running analysis on pipeline results...")
    analyze_results(output_file, report_file)
    print(f"Side experiment complete! Report generated at {report_file}")
