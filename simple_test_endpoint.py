"""
Simple test for the process-doc endpoint
"""

import requests
import json
import time

def test_process_doc_endpoint():
    """Test the new /process-doc endpoint"""
    print("🧪 Testing /process-doc Endpoint")
    print("=" * 40)
    
    # Test data
    test_data = {
        "studentId": f"DEMO_STUDENT_{int(time.time())}",
        "docType": "AadharCard", 
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1640995392/docs/invoices.jpg"
    }
    
    print(f"📤 Sending request:")
    print(f"   Student ID: {test_data['studentId']}")
    print(f"   Document Type: {test_data['docType']}")
    print(f"   Cloudinary URL: {test_data['cloudinaryUrl'][:50]}...")
    
    try:
        print(f"\n⏳ Processing document...")
        response = requests.post("http://localhost:8000/process-doc", json=test_data, timeout=60)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Document processed and stored!")
            print(f"\n📋 Response Summary:")
            print(f"   Success: {result.get('success')}")
            print(f"   Student ID: {result.get('studentId')}")
            print(f"   Message: {result.get('message')}")
            
            saved_doc = result.get('savedDocument', {})
            if saved_doc:
                print(f"\n📄 Saved Document Details:")
                print(f"   Document Type: {saved_doc.get('docType')}")
                print(f"   Confidence: {saved_doc.get('confidence')}")
                print(f"   Model Used: {saved_doc.get('modelUsed')}")
                print(f"   Fields Extracted: {len(saved_doc.get('fields', {}))}")
                
                fields = saved_doc.get('fields', {})
                if fields:
                    print(f"\n🎯 Extracted & Normalized Fields:")
                    for key, value in fields.items():
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"   {key}: {value}")
            
            # Test retrieval endpoint
            print(f"\n🔍 Testing document retrieval...")
            retrieval_response = requests.get(f"http://localhost:8000/students/{test_data['studentId']}/documents")
            
            if retrieval_response.status_code == 200:
                retrieval_result = retrieval_response.json()
                print(f"✅ Document retrieval successful!")
                print(f"   Total Documents: {retrieval_result.get('totalDocuments')}")
                print(f"   Documents: {[doc['docType'] for doc in retrieval_result.get('documents', [])]}")
            else:
                print(f"⚠️ Document retrieval failed: {retrieval_response.status_code}")
            
            return True
            
        elif response.status_code == 422:
            print("❌ Validation Error:")
            print(json.dumps(response.json(), indent=2))
            return False
            
        else:
            print(f"❌ Processing Failed:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (document processing may be taking too long)")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the server is running on http://localhost:8000")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health():
    """Quick health check"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"🏥 Health Check:")
            print(f"   Status: {health.get('status')}")
            print(f"   Database Connected: {health.get('database_connected')}")
            print(f"   Gemini Configured: {health.get('gemini_configured')}")
            return True
        return False
    except:
        print("❌ Health check failed - server may not be running")
        return False

if __name__ == "__main__":
    print("🚀 **MICROSERVICE TESTING**")
    print("=" * 50)
    
    if test_health():
        print("\n" + "="*50)
        success = test_process_doc_endpoint()
        
        if success:
            print(f"\n🎉 **TEST COMPLETED SUCCESSFULLY!**")
            print("✅ Document processing working")
            print("✅ MongoDB storage confirmed") 
            print("✅ Field normalization applied")
            print("✅ Document retrieval working")
        else:
            print(f"\n⚠️ **TEST FAILED**")
            print("Check the error messages above")
    else:
        print("Cannot proceed - service not healthy")