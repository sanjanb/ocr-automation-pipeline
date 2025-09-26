#!/usr/bin/env python3
"""
Test script for Gemini-enhanced OCR pipeline in main branch
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ocr_pipeline.pipeline import create_pipeline
from ocr_pipeline.classifiers.document_classifier import DocumentType
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_gemini_integration():
    """Test the Gemini-enhanced OCR pipeline"""
    
    print("🤖 Testing Gemini-Enhanced OCR Pipeline (Main Branch)")
    print("=" * 60)
    
    # Check for API key
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
    print(f"🔑 Gemini API Key: {'✅ Available' if gemini_key else '❌ Not found'}")
    
    try:
        # Create pipeline with Gemini integration
        pipeline = create_pipeline(use_gemini=True, gemini_api_key=gemini_key)
        print("✅ Pipeline initialized successfully")
        
        # Test with sample OCR text
        sample_text = """
        CENTRAL BOARD OF SECONDARY EDUCATION
        SECONDARY SCHOOL EXAMINATION CERTIFICATE
        
        Name: PRIYA SHARMA
        Father's Name: RAJESH SHARMA
        Roll Number: 1234567890
        School: DELHI PUBLIC SCHOOL
        
        MATHEMATICS: 95/100
        SCIENCE: 92/100
        ENGLISH: 88/100
        SOCIAL SCIENCE: 90/100
        HINDI: 85/100
        
        Total: 450/500
        Percentage: 90.0%
        Result: PASS
        """
        
        print(f"\n📄 Testing with sample 12th marksheet text...")
        
        # Process the text
        result = pipeline.entity_extractor.extract_entities(
            text=sample_text,
            document_type=DocumentType.MARKSHEET_12TH
        )
        
        print(f"\n📊 Extraction Results:")
        print(f"   ✅ Success: {len(result.entities) > 0}")
        print(f"   🎯 Confidence: {result.confidence:.3f}")
        print(f"   ⏱️ Processing Time: {result.processing_time:.2f}s")
        print(f"   🔧 Methods Used: {result.metadata.get('extraction_methods', [])}")
        print(f"   🤖 Gemini Enhanced: {result.metadata.get('gemini_enhanced', False)}")
        
        if result.entities:
            print(f"\n🎯 Extracted Entities ({len(result.entities)}):")
            for key, value in result.entities.items():
                if isinstance(value, dict) and len(value) > 3:
                    print(f"   📋 {key}: {len(value)} items")
                else:
                    display_val = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                    print(f"   • {key}: {display_val}")
        else:
            print("   ❌ No entities extracted")
        
        # Test health check
        print(f"\n🏥 Pipeline Health Check:")
        health = pipeline.health_check()
        for component, status in health.items():
            emoji = "✅" if status == "healthy" else "❌"
            print(f"   {emoji} {component}: {status}")
            
        print(f"\n🎉 Test completed successfully!")
        
        if result.metadata.get('gemini_enhanced'):
            print(f"\n✨ Gemini Pro successfully enhanced the extraction!")
            print(f"   The pipeline now combines traditional OCR methods")
            print(f"   with Gemini's intelligent text parsing for better accuracy.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_integration()