"""
Quick test to see available Gemini models
"""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import google.generativeai as genai

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API key found")
    exit(1)

genai.configure(api_key=api_key)

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")