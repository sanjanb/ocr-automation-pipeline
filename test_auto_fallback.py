#!/usr/bin/env python3
"""
Test script for AI-powered OCR with graceful fallback to traditional OCR
This demonstrates the 'auto' method that tries AI first, then falls back to traditional OCR
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ocr_pipeline.enhanced_pipeline import create_enhanced_pipeline
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_auto_fallback():
    """Test auto method (AI with traditional fallback)"""
    
    print("🎯 Testing AUTO Method (AI with Traditional Fallback)")
    print("=" * 65)
    
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
    
    # Test auto method
    hf_token = os.getenv("HUGGING_FACE_TOKEN")
    print(f"🔑 Using Hugging Face token: {'✅ Set' if hf_token else '❌ Not set'}")
    
    try:
        # Create enhanced pipeline with auto fallback
        pipeline = create_enhanced_pipeline(
            use_ai=True,
            hf_token=hf_token,
            ai_fallback_threshold=0.3  # Lower threshold for demo
        )
        
        print("\\n🚀 Processing with AUTO method (AI → Traditional Fallback)")
        print("-" * 50)
        
        # Test with first sample document
        test_doc = sample_docs[0]
        print(f"📄 Testing with: {os.path.basename(test_doc)}")
        
        result = pipeline.process_document(test_doc, method="auto")
        
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
                        print(f"      • {sub_key}: {sub_value}")
                else:
                    display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"   • {key}: {display_value}")
        else:
            print("   ❌ No entities extracted")
                
        if result.metadata:
            print(f"\\n📈 Processing Metadata:")
            for key, value in result.metadata.items():
                if key not in ["ai_raw_output", "all_results", "raw_ocr_text"]:  # Skip verbose data
                    print(f"   • {key}: {value}")
        
        # Show the magic of fallback
        if result.method_used == "traditional":
            print(f"\\n🔄 **Fallback Success!**")
            print(f"   AI models experienced issues but traditional OCR saved the day!")
        elif result.method_used == "ai":
            print(f"\\n🤖 **AI Success!**")
            print(f"   AI models worked perfectly!")
                        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_traditional_only():
    """Test traditional OCR method only"""
    
    print("\\n" + "=" * 65)
    print("🔍 Testing TRADITIONAL OCR Method")
    print("=" * 65)
    
    sample_docs = []
    data_dir = os.path.join(os.path.dirname(__file__), "data", "sample_documents")
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                sample_docs.append(os.path.join(data_dir, filename))
    
    if not sample_docs:
        print("❌ No sample documents found")
        return
        
    try:
        # Create pipeline without AI
        pipeline = create_enhanced_pipeline(
            use_ai=False,
            hf_token=None
        )
        
        print("\\n🔍 Processing with TRADITIONAL method")
        print("-" * 40)
        
        # Test with first sample document
        test_doc = sample_docs[0]
        print(f"📄 Testing with: {os.path.basename(test_doc)}")
        
        result = pipeline.process_document(test_doc, method="traditional")
        
        print(f"\\n📊 Results:")
        print(f"   ✅ Success: {result.success}")
        print(f"   🔧 Method Used: {result.method_used}")
        print(f"   📑 Document Type: {result.document_type}")
        print(f"   🎯 Confidence: {result.confidence:.3f}")
        print(f"   ⏱️  Processing Time: {result.processing_time:.2f}s")
        
        if result.entities:
            print(f"\\n🎯 Extracted Entities ({len(result.entities)}):")
            for key, value in result.entities.items():
                if isinstance(value, dict):
                    print(f"   📋 {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"      • {sub_key}: {sub_value}")
                else:
                    display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"   • {key}: {display_value}")
        else:
            print("   ❌ No entities extracted")
                        
    except Exception as e:
        print(f"❌ Traditional test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_traditional_only()  # Test traditional first (should always work)
    test_auto_fallback()     # Test auto with fallback
    
    print("\\n" + "🎉" * 20)
    print("✅ Testing Complete!")
    print("🎉" * 20)
    print("\\n💡 Key Takeaways:")
    print("   • Traditional OCR provides reliable baseline extraction")
    print("   • AUTO method tries AI first, gracefully falls back to traditional")
    print("   • Both methods extract structured data from student documents")
    print("   • Perfect for hackathon demo showing robustness!")