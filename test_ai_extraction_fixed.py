#!/usr/bin/env python3
"""
Test script for AI-powered OCR entity extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ocr_pipeline.enhanced_pipeline import create_enhanced_pipeline
from ocr_pipeline.extractors.ai_entity_extractor import create_ai_entity_extractor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_ai_extraction():
    """Test AI-powered extraction with sample documents"""
    
    print("🤖 Testing AI-Powered OCR Entity Extraction")
    print("=" * 60)
    
    # Check for Hugging Face token
    hf_token = os.getenv("HUGGING_FACE_TOKEN")
    if not hf_token:
        print("⚠️  Warning: HUGGING_FACE_TOKEN environment variable not set.")
        print("   You can still test but API calls might be rate limited.")
        print("   Set token with: set HUGGING_FACE_TOKEN=your_token_here")
        print()
    
    # Find sample documents
    sample_docs = []
    data_dir = os.path.join(os.path.dirname(__file__), "data", "sample_documents")
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                sample_docs.append(os.path.join(data_dir, filename))
    
    if not sample_docs:
        print("❌ No sample documents found in data/sample_documents/")
        print("   Available files:")
        if os.path.exists(data_dir):
            for f in os.listdir(data_dir):
                print(f"   - {f}")
        return
    
    print(f"📄 Found {len(sample_docs)} sample documents:")
    for doc in sample_docs:
        print(f"   - {os.path.basename(doc)}")
    print()
    
    # Test different extraction methods
    methods_to_test = [
        ("ai", "🤖 AI-Powered Extraction"),
        ("traditional", "🔍 Traditional OCR Extraction"), 
        ("auto", "🎯 Auto (AI with Traditional Fallback)")
    ]
    
    for method, description in methods_to_test:
        print(f"\\n{description}")
        print("-" * 40)
        
        try:
            # Create pipeline
            pipeline = create_enhanced_pipeline(
                use_ai=(method in ["ai", "auto"]),
                hf_token=hf_token,
                ai_fallback_threshold=0.5
            )
            
            # Test with first sample document
            test_doc = sample_docs[0]
            print(f"Testing with: {os.path.basename(test_doc)}")
            
            result = pipeline.process_document(test_doc, method=method)
            
            print(f"\\n📊 Results:")
            print(f"   Success: {result.success}")
            print(f"   Method Used: {result.method_used}")
            print(f"   Document Type: {result.document_type}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Processing Time: {result.processing_time:.2f}s")
            
            if result.error:
                print(f"   ❌ Error: {result.error}")
            
            if result.entities:
                print(f"\\n🎯 Extracted Entities ({len(result.entities)}):")
                for key, value in result.entities.items():
                    if isinstance(value, dict):
                        print(f"   {key}:")
                        for sub_key, sub_value in value.items():
                            print(f"     {sub_key}: {sub_value}")
                    else:
                        print(f"   {key}: {value}")
            else:
                print("   ❌ No entities extracted")
                
            if result.metadata:
                print(f"\\n📈 Metadata:")
                for key, value in result.metadata.items():
                    if key not in ["ai_raw_output", "all_results"]:  # Skip verbose data
                        print(f"   {key}: {value}")
                        
        except Exception as e:
            print(f"❌ Test failed for {method}: {e}")
            import traceback
            traceback.print_exc()

def test_ai_extractor_directly():
    """Test AI extractor directly with sample document"""
    
    print("\\n" + "=" * 60)
    print("🔬 Direct AI Extractor Testing")
    print("=" * 60)
    
    hf_token = os.getenv("HUGGING_FACE_TOKEN")
    
    try:
        # Find a sample document
        data_dir = os.path.join(os.path.dirname(__file__), "data", "sample_documents")
        sample_doc = None
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    sample_doc = os.path.join(data_dir, filename)
                    break
        
        if not sample_doc:
            print("❌ No sample document found for direct testing")
            return
            
        print(f"📄 Testing with: {os.path.basename(sample_doc)}")
        
        # Create AI extractor
        ai_extractor = create_ai_entity_extractor(hf_token=hf_token)
        
        # Test extraction
        result = ai_extractor.extract_from_image(sample_doc, "marksheet_12th")
        
        print(f"\\n📊 AI Extraction Results:")
        print(f"   Model Used: {result.model_used}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Entities Found: {len(result.entities)}")
        
        if result.entities:
            print(f"\\n🎯 Extracted Entities:")
            for key, value in result.entities.items():
                print(f"   {key}: {value}")
        
        if result.metadata:
            print(f"\\n📈 Metadata:")
            for key, value in result.metadata.items():
                if key != "ai_raw_output":  # Skip verbose raw output
                    print(f"   {key}: {value}")
                    
    except Exception as e:
        print(f"❌ Direct AI test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_extraction()
    test_ai_extractor_directly()