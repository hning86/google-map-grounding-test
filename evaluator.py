import time
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from tqdm import tqdm
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configuration (Global settings)
MODELS = ["gemini-3-flash-preview", "gemini-3.1-pro-preview", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
EFFORTS = ["low", "medium", "high"]
QUERIES = [
    "Best street food spots and street food markets in Hanoi",
    "Best vegan restaurants in Berlin",
    "Top art museums and galleries in Paris",
    "Hidden specialty coffee shops in Tokyo",
    "Best rooftop bars with a view in Bangkok"
]
PROJECT_ID = os.getenv("PROJECT_ID", "ninghai-ccai")
LOCATION = os.getenv("LOCATION", "global")

# Schema definition for controlled generation
SCHEMA = {
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
                "additionalProperties": False
            }
        }
    },
    "required": ["places"],
    "additionalProperties": False
}

# Strategy 1: Strict Grounding System Instruction (Searcher Agent)
SYSTEM_INSTRUCTION_SEARCHER = """
You are a strict Point-of-Interest discovering and verifying agent. 
Your parametric memory and training data regarding candidate places, addresses, ratings, and opening hours are considered OUTDATED and STALE.

CRITICAL RULES:
1. You are FORBIDDEN from listing any place purely from your training data.
2. For every candidate place, you MUST execute a Google Maps search query to verify its current existence and retrieve active details.
3. If the Google Maps grounding search does not return a location, you MUST NOT include it in your output list.
4. You must output a clean markdown list of verified places with their verified ratings, review counts, place type, opening hours, entry price, address, and a short description.
"""

# Schema Parser System Instruction (Parser Agent)
SYSTEM_INSTRUCTION_PARSER = """
You are a strict JSON formatting parser.
Your only job is to take the unstructured input text containing a list of places and extract them into a clean JSON object matching the requested schema.
Do not add, invent, or modify any factual details from the input.
"""

# Optimized Single-Step Grounding System Instruction (Forces maps tool in single JSON schema call)
SYSTEM_INSTRUCTION_SINGLE_STEP = """
You are a strict Point-of-Interest discovering and verifying agent.
Your parametric memory and training data regarding candidate places, addresses, ratings, and opening hours are considered OUTDATED and STALE.

CRITICAL RULES:
1. You are FORBIDDEN from listing any place purely from your training data.
2. For every candidate place, you MUST execute a Google Maps search query to verify its current existence and retrieve active details.
3. If the Google Maps grounding search does not return a location, you MUST NOT include it in your output.
4. All ratings, review counts, and addresses in your final JSON response must match the Google Maps grounding results exactly.
"""

def save_as_pretty_json(jsonl_file):
    base, ext = os.path.splitext(jsonl_file)
    pretty_json_file = base + ".json"
    
    if not os.path.exists(jsonl_file):
        return
        
    records = []
    with open(jsonl_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                # Decode response_text to a nested JSON object if it's an escaped string
                if "response_text" in record and isinstance(record["response_text"], str):
                    try:
                        record["response_text"] = json.loads(record["response_text"])
                    except json.JSONDecodeError:
                        pass
                records.append(record)
            except json.JSONDecodeError:
                pass
                
    with open(pretty_json_file, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Pretty-printed results successfully saved to {pretty_json_file}")

def run_evaluation(output_file, repetitions, models, efforts, queries, use_pipeline=False, workers=5, no_schema=False, use_vertex=True, use_priority=False):
    if use_vertex:
        if use_priority:
            client = genai.Client(
                vertexai=True,
                project=PROJECT_ID,
                location=LOCATION,
                http_options=types.HttpOptions(
                    api_version="v1",
                    headers={
                        "X-Vertex-AI-LLM-Shared-Request-Type": "priority"
                    }
                )
            )
        else:
            client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        tools = [types.Tool(google_maps=types.GoogleMaps())]
        response_schema = SCHEMA
    else:
        client = genai.Client()
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        def strip_additional_properties(s):
            if isinstance(s, dict):
                return {k: strip_additional_properties(v) for k, v in s.items() if k != "additionalProperties"}
            elif isinstance(s, list):
                return [strip_additional_properties(item) for item in s]
            return s
        response_schema = strip_additional_properties(SCHEMA)
        
    system_instruction_searcher = SYSTEM_INSTRUCTION_SEARCHER
    system_instruction_single_step = SYSTEM_INSTRUCTION_SINGLE_STEP
    if not use_vertex:
        system_instruction_searcher = system_instruction_searcher.replace("Google Maps search query", "Google Search query").replace("Google Maps grounding search", "Google Search grounding")
        system_instruction_single_step = system_instruction_single_step.replace("Google Maps search query", "Google Search query").replace("Google Maps grounding search", "Google Search grounding").replace("Google Maps grounding results", "Google Search grounding results")
    
    total_calls = len(models) * len(efforts) * len(queries) * repetitions
    mode_str = "Pipeline (2-Step)" if use_pipeline else "Baseline (1-Step)"
    api_str = "Vertex AI API" if use_vertex else "Google Gemini API"
    print(f"Starting evaluation [{mode_str}] via {api_str}: {total_calls} total API calls ({repetitions} repetitions per configuration) with {workers} parallel workers")
    
    tasks = []
    for model in models:
        for effort in efforts:
            for query in queries:
                for i in range(repetitions):
                    tasks.append((model, effort, query, i))
                    
    pbar = tqdm(total=total_calls)
    lock = threading.Lock()
    
    # Open file in write mode to overwrite previous results
    if os.path.dirname(output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        def worker(task):
            model, effort, query, i = task
            record = {
                "model": model,
                "effort": effort,
                "query": query,
                "iteration": i,
                "timestamp": time.time(),
                "success": False,
                "pipeline": use_pipeline
            }
            
            try:
                if use_pipeline:
                    # --- STEP 1: SEARCHER AGENT ---
                    config_searcher = types.GenerateContentConfig(
                        tools=tools,
                        thinking_config=types.ThinkingConfig(
                            thinking_level=effort.upper()
                        ),
                        system_instruction=system_instruction_searcher
                    )
                    
                    start_time = time.time()
                    response_searcher = client.models.generate_content(
                        model=model,
                        contents=query,
                        config=config_searcher
                    )
                    latency_searcher = time.time() - start_time
                    
                    # --- STEP 2: PARSER AGENT ---
                    # Use gemini-3.5-flash to parse and structure Step 1 results rapidly
                    config_parser = types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_PARSER,
                        response_mime_type="application/json",
                        response_schema=response_schema
                    )
                    
                    start_parser = time.time()
                    response_parser = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=response_searcher.text,
                        config=config_parser
                    )
                    latency_parser = time.time() - start_parser
                    
                    record["latency"] = latency_searcher + latency_parser
                    record["response_text"] = response_parser.text
                    
                    # Extract grounding chunks from Step 1 response metadata
                    grounding_chunks = []
                    if response_searcher.candidates and response_searcher.candidates[0].grounding_metadata:
                        metadata = response_searcher.candidates[0].grounding_metadata
                        if metadata.grounding_chunks:
                            for chunk in metadata.grounding_chunks:
                                if chunk.maps:
                                    grounding_chunks.append({
                                        "title": chunk.maps.title
                                    })
                                elif chunk.web:
                                    grounding_chunks.append({
                                        "title": chunk.web.title,
                                        "uri": chunk.web.uri
                                    })
                    record["grounding_chunks"] = grounding_chunks
                    record["success"] = True
                    
                else:
                    # --- BASELINE: 1-STEP DIRECT GENERATION ---
                    if no_schema:
                        config = types.GenerateContentConfig(
                            tools=tools,
                            thinking_config=types.ThinkingConfig(
                                thinking_level=effort.upper()
                            ),
                            system_instruction=system_instruction_single_step
                        )
                    else:
                        config = types.GenerateContentConfig(
                            tools=tools,
                            thinking_config=types.ThinkingConfig(
                                thinking_level=effort.upper()
                            ),
                            system_instruction=system_instruction_single_step,
                            response_mime_type="application/json",
                            response_schema=response_schema
                        )
                    
                    start_time = time.time()
                    response = client.models.generate_content(
                        model=model,
                        contents=query,
                        config=config
                    )
                    end_time = time.time()
                    
                    record["latency"] = end_time - start_time
                    record["response_text"] = response.text
                    
                    grounding_chunks = []
                    if response.candidates and response.candidates[0].grounding_metadata:
                        metadata = response.candidates[0].grounding_metadata
                        if metadata.grounding_chunks:
                            for chunk in metadata.grounding_chunks:
                                if chunk.maps:
                                    grounding_chunks.append({
                                        "title": chunk.maps.title
                                    })
                                elif chunk.web:
                                    grounding_chunks.append({
                                        "title": chunk.web.title,
                                        "uri": chunk.web.uri
                                    })
                    record["grounding_chunks"] = grounding_chunks
                    record["success"] = True
                    
            except Exception as e:
                record["error"] = str(e)
                # Exponential backoff on error
                time.sleep(2)
            
            with lock:
                f.write(json.dumps(record) + "\n")
                f.flush()
                pbar.update(1)
            
            # Small delay to respect rate limits
            time.sleep(0.5)
            
        with ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(worker, tasks)

    pbar.close()
    print(f"Evaluation complete. Results saved to {output_file}")
    save_as_pretty_json(output_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Gemini POI Discovery benchmarks with Google Maps or Web search grounding.")
    parser.add_argument("--output", type=str, help="Path to save the output JSONL raw results file.")
    parser.add_argument("--repetitions", "-r", type=int, help="Number of repetitions per model/effort combination.")
    parser.add_argument("--quick", action="store_true", help="Shortcut to run a fast dry-run with 1 repetition.")
    parser.add_argument("--pipeline", action="store_true", help="Enable two-step agentic pipeline (Searcher + Schema Parser).")
    parser.add_argument("--workers", "-w", type=int, default=5, help="Number of concurrent workers for parallel execution.")
    parser.add_argument("--no-schema", action="store_true", help="Disable API-level JSON Schema enforcement (freeform markdown).")
    parser.add_argument("--gemini-api", action="store_true", help="Use the Google Gemini API (Developer API) instead of Vertex AI API.")
    parser.add_argument("--priority", action="store_true", help="Use Priority PayGo latency optimization (Vertex AI only).")
    
    args = parser.parse_args()
    
    suffix = ""
    if args.gemini_api:
        suffix = "_gemini_api"
    elif args.priority:
        suffix = "_priority"
    
    if args.quick:
        default_name = "pipeline_quick_results.jsonl" if args.pipeline else "quick_test_results.jsonl"
        if args.no_schema:
            base, ext = os.path.splitext(default_name)
            default_name = base + "_no_schema" + ext
        base, ext = os.path.splitext(default_name)
        default_name = base + suffix + ext
        output_file = args.output or os.path.join("results", default_name)
        repetitions = 1
        eval_models = ["gemini-3.5-flash"]
        eval_efforts = ["low"]
        eval_queries = [QUERIES[0]]
    else:
        default_name = "pipeline_eval_results.jsonl" if args.pipeline else "full_eval_results.jsonl"
        if args.no_schema:
            base, ext = os.path.splitext(default_name)
            default_name = base + "_no_schema" + ext
        base, ext = os.path.splitext(default_name)
        default_name = base + suffix + ext
        output_file = args.output or os.path.join("results", default_name)
        repetitions = args.repetitions or 18
        eval_models = MODELS
        eval_efforts = EFFORTS
        eval_queries = QUERIES
        
    run_evaluation(
        output_file, 
        repetitions, 
        eval_models, 
        eval_efforts, 
        eval_queries, 
        use_pipeline=args.pipeline, 
        workers=args.workers, 
        no_schema=args.no_schema,
        use_vertex=not args.gemini_api,
        use_priority=args.priority
    )
