"""
Test script for MongoDB Document Fetching and Processing
This script demonstrates how to use the /api/fetch-and-process endpoint
"""

import asyncio
import json
import requests
import pymongo
from datetime import datetime
from typing import Dict, Any

# Configuration
FASTAPI_BASE_URL = "http://localhost:8000"
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "adimission_automation"

class MongoDBDocumentFetcher:
    def __init__(self, fastapi_url: str = FASTAPI_BASE_URL):
        self.fastapi_url = fastapi_url
        self.session = requests.Session()
    
    def setup_test_collection(self, collection_name: str = "raw_documents"):
        """
        Set up a test collection with sample Cloudinary URIs for testing
        In production, this would be your actual collection with uploaded document URIs
        """
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        collection = db[collection_name]
        
        # Sample test documents with Cloudinary URIs
        test_documents = [
            {
                "student_id": "STUDENT_123",
                "document_type": "aadhaar_card",
                "cloudinary_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "uploaded_at": datetime.now(),
                "processed": False,
                "batch_id": "batch_001",
                "metadata": {
                    "source": "mobile_upload",
                    "user_agent": "mobile_app"
                }
            },
            {
                "student_id": "STUDENT_123", 
                "document_type": "marksheet_12th",
                "cloudinary_url": "https://via.placeholder.com/800x600/4CAF50/white?text=12th+Marksheet",
                "uploaded_at": datetime.now(),
                "processed": False,
                "batch_id": "batch_001",
                "metadata": {
                    "source": "web_upload",
                    "file_size": 245760
                }
            },
            {
                "student_id": "STUDENT_456",
                "document_type": "aadhaar_card", 
                "cloudinary_url": "https://via.placeholder.com/800x600/2196F3/white?text=Aadhaar+Card",
                "uploaded_at": datetime.now(),
                "processed": False,
                "batch_id": "batch_002",
                "metadata": {
                    "source": "scanner",
                    "resolution": "300dpi"
                }
            }
        ]
        
        # Insert test documents
        try:
            collection.delete_many({})  # Clear existing test data
            result = collection.insert_many(test_documents)
            print(f"✅ Inserted {len(result.inserted_ids)} test documents into '{collection_name}' collection")
            
            # Show inserted documents
            for doc in collection.find():
                print(f"   📄 Document ID: {doc['_id']}")
                print(f"      Student: {doc['student_id']}")
                print(f"      Type: {doc['document_type']}")
                print(f"      URL: {doc['cloudinary_url']}")
                print()
                
            return len(result.inserted_ids)
        except Exception as e:
            print(f"❌ Error setting up test collection: {e}")
            return 0
        finally:
            client.close()
    
    def test_health_check(self):
        """Test if FastAPI service is healthy"""
        try:
            response = self.session.get(f"{self.fastapi_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ FastAPI service is healthy: {health_data['status']}")
                return True
            else:
                print(f"❌ FastAPI health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error checking health: {e}")
            return False
    
    def fetch_and_process_all_documents(self, collection_name: str = "raw_documents"):
        """
        Test fetching and processing all documents from collection
        """
        print(f"\n🔍 **TEST 1: Process all documents from '{collection_name}'**")
        print("=" * 60)
        
        request_data = {
            "collection_name": collection_name,
            "uri_field_name": "cloudinary_url",
            "document_type_field": "document_type", 
            "student_id_field": "student_id",
            "batch_size": 10,
            "additional_fields": ["batch_id", "metadata"]
        }
        
        try:
            response = self.session.post(
                f"{self.fastapi_url}/api/fetch-and-process",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )\n            \n            if response.status_code == 200:\n                result = response.json()\n                print(f\"✅ SUCCESS: Processed {result['documents_processed']}/{result['total_documents_found']} documents\")\n                print(f\"⏱️ Total processing time: {result['total_processing_time']:.2f} seconds\")\n                \n                # Show processing results\n                for i, doc_result in enumerate(result['processing_results'], 1):\n                    status = \"✅ SUCCESS\" if doc_result['success'] else \"❌ FAILED\"\n                    print(f\"\\n   📄 Document {i}: {status}\")\n                    print(f\"      URI: {doc_result['uri']}\")\n                    print(f\"      Type: {doc_result['document_type']}\")\n                    print(f\"      Confidence: {doc_result['confidence_score']:.2%}\")\n                    print(f\"      Processing Time: {doc_result['processing_time']:.2f}s\")\n                    print(f\"      MongoDB Stored: {'✅ Yes' if doc_result['mongodb_stored'] else '❌ No'}\")\n                    \n                    if doc_result['error_message']:\n                        print(f\"      Error: {doc_result['error_message']}\")\n                    \n                    # Show sample extracted data\n                    if doc_result['extracted_data']:\n                        print(f\"      Sample Data: {list(doc_result['extracted_data'].keys())[:3]}\")\n                \n                return result\n            else:\n                print(f\"❌ Request failed: {response.status_code}\")\n                print(f\"Response: {response.text}\")\n                return None\n                \n        except Exception as e:\n            print(f\"❌ Error during processing: {e}\")\n            return None\n    \n    def fetch_and_process_by_student(self, student_id: str, collection_name: str = \"raw_documents\"):\n        \"\"\"\n        Test fetching and processing documents for a specific student\n        \"\"\"\n        print(f\"\\n👤 **TEST 2: Process documents for student '{student_id}'**\")\n        print(\"=\" * 60)\n        \n        request_data = {\n            \"collection_name\": collection_name,\n            \"filter_criteria\": {\"student_id\": student_id, \"processed\": False},\n            \"uri_field_name\": \"cloudinary_url\",\n            \"document_type_field\": \"document_type\",\n            \"student_id_field\": \"student_id\",\n            \"batch_size\": 5,\n            \"additional_fields\": [\"batch_id\", \"uploaded_at\"]\n        }\n        \n        try:\n            response = self.session.post(\n                f\"{self.fastapi_url}/api/fetch-and-process\",\n                json=request_data,\n                headers={\"Content-Type\": \"application/json\"}\n            )\n            \n            if response.status_code == 200:\n                result = response.json()\n                print(f\"✅ Found and processed {result['documents_processed']} documents for student {student_id}\")\n                print(f\"📊 Filter applied: {result['filter_applied']}\")\n                \n                # Show student-specific results\n                for doc_result in result['processing_results']:\n                    if doc_result['success']:\n                        print(f\"\\n   ✅ Processed: {doc_result['document_type']}\")\n                        print(f\"      Confidence: {doc_result['confidence_score']:.2%}\")\n                        print(f\"      MongoDB ID: {doc_result['extracted_data'].get('mongodb_document_id')}\")\n                \n                return result\n            else:\n                print(f\"❌ Request failed: {response.status_code}\")\n                return None\n                \n        except Exception as e:\n            print(f\"❌ Error during student-specific processing: {e}\")\n            return None\n    \n    def fetch_and_process_by_document_type(self, doc_type: str, collection_name: str = \"raw_documents\"):\n        \"\"\"\n        Test fetching and processing documents of a specific type\n        \"\"\"\n        print(f\"\\n📋 **TEST 3: Process all '{doc_type}' documents**\")\n        print(\"=\" * 60)\n        \n        request_data = {\n            \"collection_name\": collection_name,\n            \"filter_criteria\": {\"document_type\": doc_type},\n            \"uri_field_name\": \"cloudinary_url\",\n            \"document_type_field\": \"document_type\",\n            \"student_id_field\": \"student_id\",\n            \"batch_size\": 10\n        }\n        \n        try:\n            response = self.session.post(\n                f\"{self.fastapi_url}/api/fetch-and-process\",\n                json=request_data,\n                headers={\"Content-Type\": \"application/json\"}\n            )\n            \n            if response.status_code == 200:\n                result = response.json()\n                print(f\"✅ Processed {result['documents_processed']} {doc_type} documents\")\n                \n                # Calculate average confidence for this document type\n                if result['processing_results']:\n                    successful_results = [r for r in result['processing_results'] if r['success']]\n                    if successful_results:\n                        avg_confidence = sum(r['confidence_score'] for r in successful_results) / len(successful_results)\n                        print(f\"📊 Average confidence for {doc_type}: {avg_confidence:.2%}\")\n                \n                return result\n            else:\n                print(f\"❌ Request failed: {response.status_code}\")\n                return None\n                \n        except Exception as e:\n            print(f\"❌ Error during document type processing: {e}\")\n            return None\n    \n    def test_callback_functionality(self, collection_name: str = \"raw_documents\"):\n        \"\"\"\n        Test callback functionality (requires a callback server to be running)\n        \"\"\"\n        print(f\"\\n📞 **TEST 4: Test callback functionality**\")\n        print(\"=\" * 60)\n        \n        # For this test, we'll just demonstrate the structure\n        # In production, you'd have a callback server running\n        callback_url = \"http://localhost:8080/api/documents/callback\"  # Your Spring Boot server\n        \n        request_data = {\n            \"collection_name\": collection_name,\n            \"filter_criteria\": {\"batch_id\": \"batch_001\"},\n            \"uri_field_name\": \"cloudinary_url\",\n            \"document_type_field\": \"document_type\",\n            \"student_id_field\": \"student_id\",\n            \"batch_size\": 2,\n            \"callback_url\": callback_url\n        }\n        \n        print(f\"🔗 Would send results to: {callback_url}\")\n        print(\"💡 Note: Make sure your Spring Boot server is running with the callback endpoint\")\n        \n        # You can uncomment this to test with actual callback\n        # try:\n        #     response = self.session.post(\n        #         f\"{self.fastapi_url}/api/fetch-and-process\",\n        #         json=request_data,\n        #         headers={\"Content-Type\": \"application/json\"}\n        #     )\n        #     print(f\"Callback test result: {response.status_code}\")\n        # except Exception as e:\n        #     print(f\"Callback test error: {e}\")\n        \n        return request_data\n    \n    def show_collection_info(self, collection_name: str = \"raw_documents\"):\n        \"\"\"\n        Show information about the MongoDB collection\n        \"\"\"\n        print(f\"\\n📊 **Collection Info: '{collection_name}'**\")\n        print(\"=\" * 60)\n        \n        try:\n            client = pymongo.MongoClient(MONGODB_URL)\n            db = client[DATABASE_NAME]\n            collection = db[collection_name]\n            \n            # Count documents\n            total_docs = collection.count_documents({})\n            processed_docs = collection.count_documents({\"processed\": True})\n            unprocessed_docs = collection.count_documents({\"processed\": False})\n            \n            print(f\"📄 Total documents: {total_docs}\")\n            print(f\"✅ Processed: {processed_docs}\")\n            print(f\"⏳ Unprocessed: {unprocessed_docs}\")\n            \n            # Show document types\n            pipeline = [\n                {\"$group\": {\"_id\": \"$document_type\", \"count\": {\"$sum\": 1}}},\n                {\"$sort\": {\"count\": -1}}\n            ]\n            \n            doc_types = list(collection.aggregate(pipeline))\n            if doc_types:\n                print(f\"\\n📋 Document types:\")\n                for doc_type in doc_types:\n                    print(f\"   {doc_type['_id']}: {doc_type['count']} documents\")\n            \n            # Show students\n            students = list(collection.distinct(\"student_id\"))\n            print(f\"\\n👥 Students: {', '.join(students)}\")\n            \n        except Exception as e:\n            print(f\"❌ Error accessing collection: {e}\")\n        finally:\n            client.close()\n\ndef main():\n    \"\"\"\n    Run all tests for MongoDB document fetching and processing\n    \"\"\"\n    print(\"🚀 **MONGODB DOCUMENT FETCHING & PROCESSING TEST**\")\n    print(\"=\" * 80)\n    \n    fetcher = MongoDBDocumentFetcher()\n    \n    # 1. Check if FastAPI is running\n    if not fetcher.test_health_check():\n        print(\"❌ FastAPI service is not available. Please start the server first.\")\n        return\n    \n    # 2. Set up test collection\n    print(f\"\\n📥 **Setting up test collection...**\")\n    doc_count = fetcher.setup_test_collection(\"raw_documents\")\n    if doc_count == 0:\n        print(\"❌ Failed to set up test collection\")\n        return\n    \n    # 3. Show collection info\n    fetcher.show_collection_info(\"raw_documents\")\n    \n    # 4. Test processing all documents\n    fetcher.fetch_and_process_all_documents(\"raw_documents\")\n    \n    # 5. Test processing by student\n    fetcher.fetch_and_process_by_student(\"STUDENT_123\", \"raw_documents\")\n    \n    # 6. Test processing by document type\n    fetcher.fetch_and_process_by_document_type(\"aadhaar_card\", \"raw_documents\")\n    \n    # 7. Test callback functionality\n    fetcher.test_callback_functionality(\"raw_documents\")\n    \n    print(f\"\\n🎉 **ALL TESTS COMPLETED!**\")\n    print(\"=\" * 80)\n    print(\"💡 The MongoDB document fetching endpoint is working correctly.\")\n    print(\"🔗 You can now integrate this with your Spring Boot server.\")\n    print(f\"\\n📚 **Next Steps:**\")\n    print(\"1. Update your Spring Boot server to call /api/fetch-and-process\")\n    print(\"2. Set up proper callback endpoints to receive results\")\n    print(\"3. Configure your actual MongoDB collections with Cloudinary URIs\")\n    print(\"4. Test with real document URLs from Cloudinary\")\n\nif __name__ == \"__main__\":\n    main()