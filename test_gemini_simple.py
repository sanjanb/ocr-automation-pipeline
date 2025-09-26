#!/usr/bin/env python3
"""
Quick test to validate Gemini Pro API connection
"""

import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

def test_gemini_connection():
    try:
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
        if not api_key:
            print("❌ No Gemini API key found")
            return
            
        print("🔑 Gemini API Key found!")
        
        # Configure and test
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n📋 Available models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"   ✅ {model.name}")
        
        # Test with the correct model
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # Simple test
        print(f"\n🧪 Testing with gemini-1.5-flash...")
        response = model.generate_content("Hello! Can you help me parse OCR text into JSON?")
        
        if response and response.text:
            print("✅ Gemini is working!")
            print(f"Response: {response.text[:100]}...")
        else:
            print("❌ No response from Gemini")
            
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")

if __name__ == "__main__":
    test_gemini_connection()