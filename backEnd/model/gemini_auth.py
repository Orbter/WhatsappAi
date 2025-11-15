import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

try:
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    sys.exit(1)