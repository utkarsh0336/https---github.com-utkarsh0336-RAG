import os
from google import generativeai as genai

# Set your API key
api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBQk3frcdxKVB6v46tKfOOOotqeNnW0ppQ")
genai.configure(api_key=api_key)

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
