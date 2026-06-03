import os
from google import genai
from google.genai import types

import argparse
from dotenv import load_dotenv

# Load environment variables at startup (.env)
load_dotenv()

parser = argparse.ArgumentParser(description="Test Gemini Google Maps grounding.")
parser.add_argument("--vertexai", action="store_true", help="Use Vertex AI API instead of developer Gemini API.")
parser.add_argument("--model", type=str, default="gemini-3.5-flash", help="The Gemini model to use.")
parser.add_argument("--priority", action="store_true", help="Use Priority PayGo latency optimization (Vertex AI only).")
args = parser.parse_args()

if args.vertexai or args.priority:
    PROJECT_ID = os.getenv("PROJECT_ID", "ninghai-ccai")
    LOCATION = os.getenv("LOCATION", "global")
    if args.priority:
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
        print(f"Running via Vertex AI API (Priority PayGo) with project={PROJECT_ID}, location={LOCATION}, model={args.model}...\n")
    else:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        print(f"Running via Vertex AI API with project={PROJECT_ID}, location={LOCATION}, model={args.model}...\n")
else:
    # Initialize the client using the v1beta endpoint to support Google Maps grounding
    client = genai.Client(http_options={'api_version': 'v1beta'})
    print(f"Running via Google Gemini API with model {args.model}...\n")

prompt = "What are the best Chinese restaurants within a 15-minute walk from Harvard Square in Cambridge, MA?"

response = client.models.generate_content(
    model=args.model,
    contents=prompt,
    config=types.GenerateContentConfig(
        # Turn on grounding with Google Maps
        tools=[types.Tool(google_maps=types.GoogleMaps())]
    ),
)

print(f"Prompt: {prompt}\n")
print("Generated Response:")
print(response.text)

if grounding := response.candidates[0].grounding_metadata:
  print("Grounding Metadata:", grounding)
  if grounding.grounding_chunks:
    print('-' * 40)
    print("Sources:")
    for chunk in grounding.grounding_chunks:
      print(f'- [{chunk.maps.title}]({chunk.maps.uri})')
