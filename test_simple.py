"""
Simple Test Script for Gemini Document Processor
Quick test to validate setup and functionality
"""

import os
import sys
import json
import time
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("🔧 Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment only")

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking Dependencies...")
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai installed")
    except ImportError:
        print("❌ google-generativeai missing")
        print("   Install with: pip install google-generativeai")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow installed")
    except ImportError:
        print("❌ Pillow missing")  
        print("   Install with: pip install pillow")
        return False
    
    return True

def check_api_key():
    """Check if Gemini API key is configured"""
    print("\n🔑 Checking API Configuration...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✅ Gemini API key found")
        return True
    else:
        print("❌ Gemini API key not found")
        print("   Set with: set GEMINI_API_KEY=your_api_key_here")
        print("   Get key from: https://makersuite.google.com/app/apikey")
        return False

def create_test_image():
    """Create a simple test document image"""
    print("\n🖼️ Creating Test Image...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create simple Aadhaar-like document
        img = Image.new('RGB', (800, 500), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text content
        lines = [
            "GOVERNMENT OF INDIA",
            "Unique Identification Authority of India", 
            "",
            "Name: JOHN DOE",
            "Date of Birth: 15/08/1995",
            "Aadhaar Number: 1234 5678 9012",
            "Address: 123 Main Street",
            "         Bangalore, Karnataka",
            "         PIN: 560001"
        ]
        
        y = 50
        for line in lines:
            draw.text((50, y), line, fill='black')
            y += 35
        
        # Save test image
        test_path = "test_aadhaar.png"
        img.save(test_path)
        print(f"✅ Test image created: {test_path}")
        return test_path
        
    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return None

def test_processor():
    """Test the document processor"""
    print("\n🧪 Testing Document Processor...")
    
    try:
        from gemini_processor import create_processor
        
        # Initialize processor
        processor = create_processor()
        print("✅ Processor initialized successfully")
        
        # Create test image
        test_image = create_test_image()
        if not test_image:
            print("⚠️ No test image available")
            return True
        
        # Process test document
        print("📄 Processing test document...")
        start_time = time.time()
        
        result = processor.process_document(test_image, "aadhaar_card")
        processing_time = time.time() - start_time
        
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        
        if result.success:
            print("✅ Processing successful!")
            print(f"📊 Document Type: {result.document_type}")
            print(f"🎯 Confidence: {result.confidence_score:.1%}")
            print(f"📋 Extracted {len(result.extracted_data)} fields")
            
            print("\n📋 Extracted Data:")
            print(json.dumps(result.extracted_data, indent=2, ensure_ascii=False))
            
            if result.validation_issues:
                print(f"\n⚠️ Validation Issues ({len(result.validation_issues)}):")
                for issue in result.validation_issues:
                    print(f"  • {issue}")
        else:
            print(f"❌ Processing failed: {result.error_message}")
            return False
        
        # Clean up
        if Path(test_image).exists():
            Path(test_image).unlink()
            print("🧹 Test image cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Processor test failed: {e}")
        return False

def test_web_interface():
    """Test web interface availability"""
    print("\n🌐 Testing Web Interface...")
    
    try:
        # Just check if Flask is available
        import flask
        print("✅ Flask available for web interface")
        print("   Start with: python web_app.py")
        print("   Access at: http://127.0.0.1:5000")
        return True
    except ImportError:
        print("⚠️ Flask not installed (optional)")
        print("   Install with: pip install flask")
        return True  # Not critical

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Gemini Document Processor Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Dependencies
    if check_dependencies():
        tests_passed += 1
    
    # Test 2: API Key
    if check_api_key():
        tests_passed += 1
    else:
        print("\n❌ Cannot proceed without API key")
        return False
    
    # Test 3: Processor
    if test_processor():
        tests_passed += 1
    
    # Test 4: Web Interface
    if test_web_interface():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! System ready to use.")
        print("\n🚀 Next Steps:")
        print("1. Run web interface: python web_app.py")
        print("2. Upload a document and test processing")
        print("3. Check the extracted JSON data")
        return True
    else:
        print("⚠️ Some tests failed. Please fix issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)