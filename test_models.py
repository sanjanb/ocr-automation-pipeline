import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment")
    exit(1)

print(f"Using API key: {api_key[:20]}...")
genai.configure(api_key=api_key)

try:
    print("Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name} (supports generateContent)")
except Exception as e:
    print(f"ERROR listing models: {e}")
    
# Test specific models
test_models = [
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-pro',
    'gemini-pro-vision',
    'models/gemini-1.5-pro',
    'models/gemini-1.5-flash'
]

print("\nTesting model availability:")
for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        print(f"  ✅ {model_name} - Available")
    except Exception as e:
        print(f"  ❌ {model_name} - Error: {e}")