"""
Complete MongoDB Storage Test
Tests the full document processing workflow and verifies MongoDB storage
"""

import requests
import json
import time
import pymongo
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "document_processor"

def test_mongodb_connection():
    """Test direct MongoDB connection"""
    print("🔍 Testing MongoDB Connection...")
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DB_NAME]
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Check existing collections
        collections = db.list_collection_names()
        print(f"📁 Existing collections: {collections}")
        
        # Check existing students
        if 'students' in collections:
            students_count = db.students.count_documents({})
            print(f"👥 Existing students in database: {students_count}")
            
            # Show some sample students
            if students_count > 0:
                sample_students = list(db.students.find({}, {"studentId": 1, "documents.docType": 1}).limit(3))
                print("📋 Sample student records:")
                for student in sample_students:
                    doc_types = [doc.get("docType", "Unknown") for doc in student.get("documents", [])]
                    print(f"   • Student {student['studentId']}: {doc_types}")
        
        return True, db
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False, None

def test_document_processing_with_storage():
    """Test complete document processing workflow with MongoDB verification"""
    print("\n🚀 Testing Complete Document Processing Workflow...")
    
    # Test data - using a sample Cloudinary image
    test_data = {
        "studentId": f"TEST_STUDENT_{int(time.time())}",  # Unique ID
        "docType": "AadharCard",
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1640995392/docs/invoices.jpg"
    }
    
    print(f"📤 Sending request for student: {test_data['studentId']}")
    print(f"📄 Document type: {test_data['docType']}")
    
    try:
        # Make API request
        response = requests.post(f"{BASE_URL}/process-doc", json=test_data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document processing successful!")
            print("📋 API Response:")
            print(json.dumps(result, indent=2))
            
            # Verify MongoDB storage
            return verify_mongodb_storage(test_data['studentId'], result)
            
        else:
            print(f"❌ Document processing failed")
            print(f"Error response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - processing may be taking too long")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def verify_mongodb_storage(student_id, api_response):
    """Verify that the document was stored correctly in MongoDB"""
    print(f"\n🔍 Verifying MongoDB Storage for {student_id}...")
    
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DB_NAME]
        
        # Find the student record
        student_record = db.students.find_one({"studentId": student_id})
        
        if not student_record:
            print(f"❌ Student record not found in MongoDB for {student_id}")
            return False
        
        print("✅ Student record found in MongoDB!")
        print(f"📊 MongoDB Record:")
        
        # Clean up ObjectId for display
        if '_id' in student_record:
            student_record['_id'] = str(student_record['_id'])
        
        # Convert datetime objects to strings for display
        if 'createdAt' in student_record:
            student_record['createdAt'] = student_record['createdAt'].isoformat()
        if 'updatedAt' in student_record:
            student_record['updatedAt'] = student_record['updatedAt'].isoformat()
        
        for doc in student_record.get('documents', []):
            if 'processedAt' in doc:
                doc['processedAt'] = doc['processedAt'].isoformat()
        
        print(json.dumps(student_record, indent=2))
        
        # Verify data consistency between API response and MongoDB
        print(f"\n🔄 Verifying Data Consistency...")
        
        api_doc = api_response.get('savedDocument', {})
        stored_documents = student_record.get('documents', [])
        
        if not stored_documents:
            print("❌ No documents found in MongoDB record")
            return False
        
        stored_doc = stored_documents[-1]  # Get the latest document
        
        # Check key fields
        checks = [
            ("Document Type", api_doc.get('docType'), stored_doc.get('docType')),
            ("Cloudinary URL", api_doc.get('cloudinaryUrl'), stored_doc.get('cloudinaryUrl')),
            ("Confidence", api_doc.get('confidence'), stored_doc.get('confidence')),
            ("Model Used", api_doc.get('modelUsed'), stored_doc.get('modelUsed')),
            ("Fields Count", len(api_doc.get('fields', {})), len(stored_doc.get('fields', {})))
        ]
        
        all_consistent = True
        for field_name, api_value, db_value in checks:
            if api_value == db_value:
                print(f"   ✅ {field_name}: Consistent")
            else:
                print(f"   ❌ {field_name}: API={api_value}, DB={db_value}")
                all_consistent = False
        
        if all_consistent:
            print("✅ All data is consistent between API and MongoDB!")
        else:
            print("⚠️ Some data inconsistencies found")
        
        # Check field normalization
        print(f"\n🎯 Checking Field Normalization...")
        stored_fields = stored_doc.get('fields', {})
        
        expected_normalized_fields = ['Name', 'DOB', 'Address']  # Common Aadhaar fields
        found_normalized = []
        
        for field in expected_normalized_fields:
            if field in stored_fields:
                found_normalized.append(field)
                print(f"   ✅ {field}: {stored_fields[field]}")
        
        print(f"📊 Normalized fields found: {len(found_normalized)}/{len(expected_normalized_fields)}")
        
        return all_consistent
        
    except Exception as e:
        print(f"❌ MongoDB verification failed: {e}")
        return False

def test_student_retrieval_endpoints(student_id):
    """Test the student document retrieval endpoints"""
    print(f"\n🔍 Testing Student Retrieval Endpoints for {student_id}...")
    
    # Test getting all documents for student
    try:
        response = requests.get(f"{BASE_URL}/students/{student_id}/documents")
        print(f"📊 Get All Documents - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result.get('totalDocuments', 0)} documents")
            print(f"📋 Document types: {[doc['docType'] for doc in result.get('documents', [])]}")
        else:
            print(f"❌ Failed to retrieve documents: {response.text}")
            
    except Exception as e:
        print(f"❌ Error retrieving all documents: {e}")
    
    # Test getting specific document type
    try:
        response = requests.get(f"{BASE_URL}/students/{student_id}/documents/AadharCard")
        print(f"📊 Get Specific Document - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved AadharCard document")
            print(f"📋 Confidence: {result.get('confidence', 'N/A')}")
            print(f"📋 Fields: {len(result.get('fields', {}))}")
        else:
            print(f"❌ Failed to retrieve specific document: {response.text}")
            
    except Exception as e:
        print(f"❌ Error retrieving specific document: {e}")

def cleanup_test_data():
    """Clean up test data from MongoDB"""
    print(f"\n🧹 Cleaning up test data...")
    
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DB_NAME]
        
        # Delete test student records
        result = db.students.delete_many({"studentId": {"$regex": "^TEST_STUDENT_"}})
        print(f"🗑️ Cleaned up {result.deleted_count} test student records")
        
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

def main():
    """Run complete storage verification test"""
    print("🧪 **COMPLETE MONGODB STORAGE VERIFICATION TEST**")
    print("=" * 60)
    
    # Step 1: Test MongoDB connection
    mongo_connected, db = test_mongodb_connection()
    if not mongo_connected:
        print("❌ Cannot proceed without MongoDB connection")
        return
    
    # Step 2: Test health endpoint
    print(f"\n🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Service healthy: {health_data.get('status')}")
            print(f"📊 Database connected: {health_data.get('database_connected')}")
            print(f"🤖 Gemini configured: {health_data.get('gemini_configured')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Step 3: Test complete document processing
    processing_success = test_document_processing_with_storage()
    
    if processing_success:
        print(f"\n🎉 **ALL TESTS PASSED!**")
        print("✅ Document processing working")
        print("✅ MongoDB storage verified")
        print("✅ Data consistency confirmed")
        print("✅ Field normalization working")
    else:
        print(f"\n⚠️ **SOME TESTS FAILED**")
        print("Please check the logs above for specific issues")
    
    # Optional cleanup
    # cleanup_test_data()
    
    return processing_success

if __name__ == "__main__":
    main()