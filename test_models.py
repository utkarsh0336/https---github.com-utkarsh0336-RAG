import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-latest",
    "gemini-pro",
    "models/gemini-1.5-flash",
    "models/gemini-pro"
]

print("Testing models...")
for model_name in models_to_test:
    try:
        print(f"Testing {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print("SUCCESS!")
        print(f"Working model: {model_name}")
        break
    except Exception as e:
        print(f"FAILED: {e}")
