"""
Test MongoDB storage directly
"""
import requests
import json

def test_process_doc_endpoint_with_debug():
    """Test the new /process-doc endpoint specifically"""
    
    test_data = {
        "studentId": "DEBUG_STUDENT_123",
        "docType": "AadharCard",
        "documentPath": "assets/test_docs/aadhaar_sample.jpg"
    }
    
    print("🧪 Testing /process-doc endpoint specifically...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Test the health first
        health_response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"\n🏥 Health Check: {health_response.status_code}")
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"   Database Connected: {health.get('database_connected')}")
            print(f"   Gemini Configured: {health.get('gemini_configured')}")
        
        # Test the new endpoint
        print(f"\n📤 Calling /process-doc...")
        response = requests.post("http://localhost:8000/process-doc", json=test_data, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
            # Now test retrieval
            print(f"\n🔍 Testing document retrieval...")
            retrieval_response = requests.get(f"http://localhost:8000/students/{test_data['studentId']}/documents")
            print(f"📊 Retrieval Status: {retrieval_response.status_code}")
            
            if retrieval_response.status_code == 200:
                retrieval_result = retrieval_response.json()
                print(f"📋 Retrieved Documents: {json.dumps(retrieval_result, indent=2)}")
            else:
                print(f"❌ Retrieval failed: {retrieval_response.text}")
                
        elif response.status_code == 422:
            print(f"❌ Validation Error:")
            error_detail = response.json()
            print(f"📋 Error Details: {json.dumps(error_detail, indent=2)}")
        else:
            print(f"❌ Error {response.status_code}:")
            print(f"📋 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def test_old_process_endpoint():
    """Test the old /api/process endpoint to see what it returns"""
    print(f"\n🔍 Testing OLD /api/process endpoint for comparison...")
    
    try:
        # Upload a file to the old endpoint (if it exists)
        response = requests.get("http://localhost:8000/api/process", timeout=10)
        print(f"Old endpoint status: {response.status_code}")
        
    except Exception as e:
        print(f"Old endpoint test failed: {e}")

if __name__ == "__main__":
    print("🔍 **DEBUGGING MONGODB STORAGE ISSUE**")
    print("=" * 50)
    
    test_process_doc_endpoint_with_debug()
    test_old_process_endpoint()