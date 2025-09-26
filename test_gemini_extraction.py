#!/usr/bin/env python3
"""
Test script for Gemini-powered OCR entity extraction
This demonstrates the OCR + Gemini Pro approach for better accuracy
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ocr_pipeline.enhanced_pipeline import create_enhanced_pipeline
from ocr_pipeline.extractors.gemini_entity_extractor import create_gemini_entity_extractor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_gemini_extraction():
    """Test Gemini-powered extraction (OCR + AI parsing)"""
    
    print("🤖 Testing GEMINI-Powered OCR Entity Extraction")
    print("=" * 65)
    print("💡 Approach: Traditional OCR → Gemini Pro AI Parsing → Structured JSON")
    print()
    
    # Check for sample documents
    sample_docs = []
    data_dir = os.path.join(os.path.dirname(__file__), "data", "sample_documents")
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                sample_docs.append(os.path.join(data_dir, filename))
    
    if not sample_docs:
        print("❌ No sample documents found in data/sample_documents/")
        return
    
    print(f"📄 Found {len(sample_docs)} sample documents:")
    for doc in sample_docs:
        print(f"   - {os.path.basename(doc)}")
    print()
    
    # Check API keys
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
    hf_token = os.getenv("HUGGING_FACE_TOKEN")
    
    print("🔑 API Status:")
    print(f"   Gemini API Key: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"   HuggingFace Token: {'✅ Set' if hf_token else '❌ Not set'}")
    print()
    
    if not gemini_key:
        print("❌ Gemini API key not found. Please set GEMINI_API_KEY in .env file")
        return
    
    # Test different methods
    methods_to_test = [
        ("gemini", "🤖 Gemini Pro (OCR + AI Parsing)", "The hybrid approach!"),
        ("traditional", "🔍 Traditional OCR Only", "Baseline comparison"),
        ("auto", "🎯 AUTO (Smart Selection)", "Best available method")
    ]
    
    for method, title, description in methods_to_test:
        print(f"\\n{title}")
        print(f"💭 {description}")
        print("-" * 50)
        
        try:
            # Create enhanced pipeline
            pipeline = create_enhanced_pipeline(
                use_ai=True,
                hf_token=hf_token,
                gemini_api_key=gemini_key,
                ai_fallback_threshold=0.3  # Lower threshold for demo
            )
            
            # Test with first sample document
            test_doc = sample_docs[0]
            print(f"📄 Processing: {os.path.basename(test_doc)}")
            
            result = pipeline.process_document(test_doc, method=method)
            
            print(f"\\n📊 Results:")
            print(f"   ✅ Success: {result.success}")
            print(f"   🔧 Method Used: {result.method_used}")
            print(f"   📑 Document Type: {result.document_type}")
            print(f"   🎯 Confidence: {result.confidence:.3f}")
            print(f"   ⏱️  Processing Time: {result.processing_time:.2f}s")
            
            if result.error:
                print(f"   ❌ Error: {result.error}")
            else:
                print(f"   ✅ No errors")
            
            if result.entities:
                print(f"\\n🎯 Extracted Entities ({len(result.entities)}):")
                for key, value in result.entities.items():
                    if isinstance(value, dict):
                        print(f"   📋 {key}:")
                        for sub_key, sub_value in value.items():
                            display_value = str(sub_value)[:80] + "..." if len(str(sub_value)) > 80 else str(sub_value)
                            print(f"      • {sub_key}: {display_value}")
                    else:
                        display_value = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
                        print(f"   • {key}: {display_value}")
            else:
                print("   ❌ No entities extracted")
                
            if result.metadata:
                print(f"\\n📈 Processing Details:")
                for key, value in result.metadata.items():
                    if key not in ["gemini_raw_output", "ai_raw_output", "raw_ocr_text"]:  # Skip verbose data
                        if isinstance(value, dict):
                            print(f"   • {key}: [complex data - {len(value)} items]")
                        else:
                            print(f"   • {key}: {value}")
                            
            # Special message for Gemini
            if result.method_used == "gemini":
                print(f"\\n🌟 **Gemini Magic!**")
                print(f"   ✨ Traditional OCR extracted raw text")
                print(f"   🤖 Gemini Pro structured it into perfect JSON")
                print(f"   🎯 Best of both worlds: reliable OCR + smart AI parsing!")
                        
        except Exception as e:
            print(f"❌ Test failed for {method}: {e}")
            import traceback
            traceback.print_exc()

def test_gemini_direct():
    """Test Gemini extractor directly with OCR text"""
    
    print("\\n" + "=" * 65)
    print("🔬 Direct Gemini Pro Testing")
    print("=" * 65)
    
    # Sample OCR text for testing
    sample_ocr_text = """
CENTRAL BOARD OF SECONDARY EDUCATION
SECONDARY SCHOOL EXAMINATION
CERTIFICATE - 2023

Name: RAHUL KUMAR SHARMA
Father's Name: SURESH KUMAR SHARMA
Mother's Name: PRIYA SHARMA
Roll Number: 12345678
School: ST. MARY'S CONVENT SCHOOL

SUBJECT        MARKS    MAX MARKS
English        95       100
Mathematics    98       100
Science        96       100
Social Science 94       100
Hindi          92       100

Total: 475/500
Percentage: 95.0%
Result: PASS
"""
    
    try:
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
        if not gemini_key:
            print("❌ Gemini API key not found")
            return
            
        print("📄 Testing with sample OCR text")
        print(f"📏 Text length: {len(sample_ocr_text)} characters")
        
        # Create Gemini extractor
        gemini_extractor = create_gemini_entity_extractor(api_key=gemini_key)
        
        # Test extraction
        result = gemini_extractor.extract_from_ocr_text(sample_ocr_text, "marksheet_12th")
        
        print(f"\\n📊 Gemini Parsing Results:")
        print(f"   Model Used: {result.model_used}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Entities Found: {len(result.entities)}")
        
        if result.entities:
            print(f"\\n🎯 Parsed Entities:")
            for key, value in result.entities.items():
                if isinstance(value, dict):
                    print(f"   📋 {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"      • {sub_key}: {sub_value}")
                else:
                    print(f"   • {key}: {value}")
        
        if result.metadata:
            print(f"\\n📈 Metadata:")
            for key, value in result.metadata.items():
                if key != "gemini_raw_output":  # Skip verbose raw output
                    print(f"   • {key}: {value}")
                    
        print("\\n✨ This shows how Gemini Pro can intelligently parse")
        print("   unstructured OCR text into perfect JSON structure!")
                    
    except Exception as e:
        print(f"❌ Direct Gemini test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_extraction()
    test_gemini_direct()
    
    print("\\n" + "🎉" * 25)
    print("✅ Gemini Testing Complete!")
    print("🎉" * 25)
    print("\\n💡 Key Benefits of Gemini Approach:")
    print("   🔄 Combines reliable OCR with smart AI parsing")
    print("   🎯 Better accuracy than pure OCR pattern matching")
    print("   🚀 Faster than heavy computer vision models")
    print("   💰 Cost-effective compared to specialized AI models")
    print("   🌟 Perfect for hackathon demos!")