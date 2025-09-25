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
        return\n    \n    print(f\"📄 Found {len(sample_docs)} sample documents:\")\n    for doc in sample_docs:\n        print(f\"   - {os.path.basename(doc)}\")\n    print()\n    \n    # Test different extraction methods\n    methods_to_test = [\n        (\"ai\", \"🤖 AI-Powered Extraction\"),\n        (\"traditional\", \"🔍 Traditional OCR Extraction\"), \n        (\"auto\", \"🎯 Auto (AI with Traditional Fallback)\")\n    ]\n    \n    for method, description in methods_to_test:\n        print(f\"\\n{description}\")\n        print(\"-\" * 40)\n        \n        try:\n            # Create pipeline\n            pipeline = create_enhanced_pipeline(\n                use_ai=(method in [\"ai\", \"auto\"]),\n                hf_token=hf_token,\n                ai_fallback_threshold=0.5\n            )\n            \n            # Test with first sample document\n            test_doc = sample_docs[0]\n            print(f\"Testing with: {os.path.basename(test_doc)}\")\n            \n            result = pipeline.process_document(test_doc, method=method)\n            \n            print(f\"\\n📊 Results:\")\n            print(f\"   Success: {result.success}\")\n            print(f\"   Method Used: {result.method_used}\")\n            print(f\"   Document Type: {result.document_type}\")\n            print(f\"   Confidence: {result.confidence:.3f}\")\n            print(f\"   Processing Time: {result.processing_time:.2f}s\")\n            \n            if result.error:\n                print(f\"   ❌ Error: {result.error}\")\n            \n            if result.entities:\n                print(f\"\\n🎯 Extracted Entities ({len(result.entities)}):\")\n                for key, value in result.entities.items():\n                    if isinstance(value, dict):\n                        print(f\"   {key}:\")\n                        for sub_key, sub_value in value.items():\n                            print(f\"     {sub_key}: {sub_value}\")\n                    else:\n                        print(f\"   {key}: {value}\")\n            else:\n                print(\"   ❌ No entities extracted\")\n                \n            if result.metadata:\n                print(f\"\\n📈 Metadata:\")\n                for key, value in result.metadata.items():\n                    if key not in [\"ai_raw_output\", \"all_results\"]:  # Skip verbose data\n                        print(f\"   {key}: {value}\")\n                        \n        except Exception as e:\n            print(f\"❌ Test failed for {method}: {e}\")\n            import traceback\n            traceback.print_exc()\n\ndef test_ai_extractor_directly():\n    \"\"\"Test AI extractor directly with sample document\"\"\"\n    \n    print(\"\\n\" + \"=\" * 60)\n    print(\"🔬 Direct AI Extractor Testing\")\n    print(\"=\" * 60)\n    \n    hf_token = os.getenv(\"HUGGING_FACE_TOKEN\")\n    \n    try:\n        # Find a sample document\n        data_dir = os.path.join(os.path.dirname(__file__), \"data\", \"sample_documents\")\n        sample_doc = None\n        \n        if os.path.exists(data_dir):\n            for filename in os.listdir(data_dir):\n                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):\n                    sample_doc = os.path.join(data_dir, filename)\n                    break\n        \n        if not sample_doc:\n            print(\"❌ No sample document found for direct testing\")\n            return\n            \n        print(f\"📄 Testing with: {os.path.basename(sample_doc)}\")\n        \n        # Create AI extractor\n        ai_extractor = create_ai_entity_extractor(hf_token=hf_token)\n        \n        # Test extraction\n        result = ai_extractor.extract_from_image(sample_doc, \"marksheet_12th\")\n        \n        print(f\"\\n📊 AI Extraction Results:\")\n        print(f\"   Model Used: {result.model_used}\")\n        print(f\"   Confidence: {result.confidence:.3f}\")\n        print(f\"   Entities Found: {len(result.entities)}\")\n        \n        if result.entities:\n            print(f\"\\n🎯 Extracted Entities:\")\n            for key, value in result.entities.items():\n                print(f\"   {key}: {value}\")\n        \n        if result.metadata:\n            print(f\"\\n📈 Metadata:\")\n            for key, value in result.metadata.items():\n                if key != \"ai_raw_output\":  # Skip verbose raw output\n                    print(f\"   {key}: {value}\")\n                    \n    except Exception as e:\n        print(f\"❌ Direct AI test failed: {e}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    test_ai_extraction()\n    test_ai_extractor_directly()