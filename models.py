import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

try:
    client = Client(api_key=os.environ.get("GEMINI_API_KEY"))
    print("--- FETCHING MODELS ---")
    
    # Simple loop to print ONLY the name
    for model in client.models.list():
        # The new SDK might allow direct access or require .name
        print(f"Found Model: {model.name}")

except Exception as e:
    print(f"\n❌ Error: {e}")