# 📥 MongoDB Document Fetching & Processing Guide

## 🎯 **Overview**

Your FastAPI OCR service now includes the ability to **fetch documents directly from MongoDB collections** and process their Cloudinary URIs. This is perfect for:

- Processing documents that were uploaded to a staging/raw collection
- Batch processing unprocessed documents
- Re-processing documents with updated AI models
- Processing specific students' documents or document types

## 🚀 **New Endpoint: `/api/fetch-and-process`**

### **Basic Usage**

```http
POST /api/fetch-and-process
Content-Type: application/json

{
  "collection_name": "raw_documents",
  "filter_criteria": {"student_id": "STUDENT_123", "processed": false},
  "uri_field_name": "cloudinary_url",
  "document_type_field": "document_type",
  "student_id_field": "student_id",
  "batch_size": 10
}
```

### **Complete Request Schema**

```json
{
  "collection_name": "raw_documents", // Required: MongoDB collection name
  "filter_criteria": {
    // Optional: MongoDB query filter
    "student_id": "STUDENT_123",
    "processed": false,
    "document_type": { "$in": ["aadhaar_card", "marksheet_12th"] }
  },
  "uri_field_name": "cloudinary_url", // Field containing Cloudinary URI
  "document_type_field": "document_type", // Field containing document type
  "student_id_field": "student_id", // Field containing student ID
  "batch_size": 10, // Max documents to process at once
  "callback_url": "http://your-server/callback", // Optional: callback URL
  "additional_fields": ["batch_id", "metadata"] // Optional: extra fields to include
}
```

### **Response Format**

```json
{
  "success": true,
  "total_documents_found": 5,
  "documents_processed": 4,
  "documents_failed": 1,
  "collection_name": "raw_documents",
  "filter_applied": { "student_id": "STUDENT_123" },
  "processing_results": [
    {
      "uri": "https://res.cloudinary.com/demo/image/upload/doc1.jpg",
      "success": true,
      "document_type": "aadhaar_card",
      "extracted_data": {
        "student_name": "John Doe",
        "aadhaar_number": "1234-5678-9012",
        "mongodb_document_id": "672c8f5a1234567890abcdef",
        "source_collection": "raw_documents",
        "original_cloudinary_url": "https://res.cloudinary.com/demo/image/upload/doc1.jpg"
      },
      "processing_time": 2.45,
      "confidence_score": 0.92,
      "model_used": "gemini-2.0-flash",
      "mongodb_stored": true,
      "validation_issues": []
    }
  ],
  "total_processing_time": 12.3,
  "message": "Processed 4/5 documents from MongoDB collection"
}
```

## 📊 **MongoDB Collection Structure**

### **Expected Document Format**

Your MongoDB collection documents should follow this structure:

```javascript
// Collection: raw_documents
{
  "_id": ObjectId("672c8f5a1234567890abcdef"),
  "student_id": "STUDENT_123",
  "document_type": "aadhaar_card",
  "cloudinary_url": "https://res.cloudinary.com/your-app/image/upload/v1234567890/aadhaar.jpg",
  "uploaded_at": ISODate("2025-09-27T10:30:00Z"),
  "processed": false,
  "batch_id": "admission_batch_001",
  "metadata": {
    "source": "mobile_app",
    "file_size": 245760,
    "user_agent": "MyApp/1.0"
  }
}
```

### **Flexible Schema Support**

The endpoint supports different field names - just specify them in your request:

```json
{
  "collection_name": "student_uploads",
  "uri_field_name": "document_url", // Instead of "cloudinary_url"
  "document_type_field": "doc_category", // Instead of "document_type"
  "student_id_field": "student_number" // Instead of "student_id"
}
```

## 🔄 **Processing Flow**

```mermaid
flowchart LR
    A[MongoDB Collection] --> B[Query Documents]
    B --> C[Extract Cloudinary URIs]
    C --> D[Download from Cloudinary]
    D --> E[OCR Processing]
    E --> F[Store in Main Collection]
    F --> G[Send Callback]
    G --> H[Update Original Document]
```

1. **Query MongoDB Collection** - Find documents matching your criteria
2. **Extract URIs** - Get Cloudinary URLs from each document
3. **Download Documents** - Fetch files from Cloudinary
4. **Process with OCR** - Extract data using Gemini AI
5. **Store Results** - Save to main student documents collection
6. **Send Callbacks** - Notify your Spring Boot server
7. **Mark as Processed** - (Optional) Update original documents

## 🛠️ **Common Use Cases**

### **1. Process All Unprocessed Documents**

```python
import requests

response = requests.post("http://localhost:8000/api/fetch-and-process", json={
    "collection_name": "raw_documents",
    "filter_criteria": {"processed": False},
    "uri_field_name": "cloudinary_url",
    "batch_size": 20
})
```

### **2. Process Documents for Specific Student**

```python
response = requests.post("http://localhost:8000/api/fetch-and-process", json={
    "collection_name": "student_uploads",
    "filter_criteria": {"student_id": "STUDENT_123"},
    "uri_field_name": "document_url",
    "student_id_field": "student_id",
    "batch_size": 10,
    "callback_url": "http://localhost:8080/api/documents/callback"
})
```

### **3. Process Specific Document Types**

```python
response = requests.post("http://localhost:8000/api/fetch-and-process", json={
    "collection_name": "raw_documents",
    "filter_criteria": {"document_type": "aadhaar_card", "processed": False},
    "uri_field_name": "cloudinary_url",
    "document_type_field": "document_type"
})
```

### **4. Process Documents from Date Range**

```python
response = requests.post("http://localhost:8000/api/fetch-and-process", json={
    "collection_name": "raw_documents",
    "filter_criteria": {
        "uploaded_at": {
            "$gte": "2025-09-01T00:00:00Z",
            "$lt": "2025-09-30T23:59:59Z"
        }
    },
    "uri_field_name": "cloudinary_url"
})
```

## 🔗 **Spring Boot Integration**

### **Java Service Example**

```java
@Service
public class MongoDBDocumentProcessor {

    @Value("${fastapi.base-url}")
    private String fastapiBaseUrl;

    public void processUnprocessedDocuments(String collectionName) {
        // Build request
        Map<String, Object> request = Map.of(
            "collection_name", collectionName,
            "filter_criteria", Map.of("processed", false),
            "uri_field_name", "cloudinary_url",
            "document_type_field", "document_type",
            "student_id_field", "student_id",
            "batch_size", 10,
            "callback_url", "http://localhost:8080/api/documents/mongodb-callback"
        );

        // Send to FastAPI
        ResponseEntity<MongoDBProcessingResponse> response = restTemplate.postForEntity(
            fastapiBaseUrl + "/api/fetch-and-process",
            request,
            MongoDBProcessingResponse.class
        );

        // Handle response
        if (response.getStatusCode() == HttpStatus.OK) {
            MongoDBProcessingResponse result = response.getBody();
            System.out.println("Processed: " + result.getDocumentsProcessed() +
                             "/" + result.getTotalDocumentsFound());
        }
    }
}
```

### **Callback Handler**

```java
@PostMapping("/api/documents/mongodb-callback")
public ResponseEntity<String> handleMongoDBCallback(@RequestBody MongoDBCallbackRequest request) {
    System.out.println("📥 Received MongoDB processing results");
    System.out.println("Collection: " + request.getCollectionName());
    System.out.println("Processed: " + request.getDocumentsProcessed());

    // Process results
    for (DocumentResult result : request.getProcessingResults()) {
        if (result.isSuccess()) {
            // Handle successful processing
            handleProcessedDocument(result);
        }
    }

    return ResponseEntity.ok("MongoDB callback received");
}
```

## 🧪 **Testing**

### **Run the Test Script**

```bash
cd "d:\Projects\MIT Hackathon\ocr-automation-pipeline"
python test_mongodb_fetch.py
```

This will:

1. ✅ Set up test collection with sample Cloudinary URIs
2. ✅ Test processing all documents
3. ✅ Test student-specific processing
4. ✅ Test document type filtering
5. ✅ Test callback functionality

### **Manual Testing with cURL**

```bash
curl -X POST http://localhost:8000/api/fetch-and-process \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "raw_documents",
    "filter_criteria": {"student_id": "STUDENT_123"},
    "uri_field_name": "cloudinary_url",
    "batch_size": 5
  }'
```

## ⚠️ **Important Notes**

### **Performance Considerations**

- Use `batch_size` to control memory usage and processing time
- Large batches may timeout - recommend 10-50 documents per batch
- Cloudinary downloads are parallel but rate-limited

### **Error Handling**

- Failed downloads are reported but don't stop the batch
- Individual processing errors are captured per document
- MongoDB connection errors will fail the entire request

### **Security**

- Ensure MongoDB collections are properly secured
- Validate collection names to prevent injection
- Use proper authentication for production

### **Database Updates**

- Processed documents are stored in the main `document_processor` collection
- Original documents in the source collection are **not** automatically marked as processed
- You may want to update the source collection after successful processing

## 🎉 **You're All Set!**

Your FastAPI service can now:

1. ✅ **Fetch documents from any MongoDB collection**
2. ✅ **Download files from Cloudinary URIs**
3. ✅ **Process with OCR and AI extraction**
4. ✅ **Store results in structured format**
5. ✅ **Send callbacks to Spring Boot server**
6. ✅ **Handle errors gracefully**

**Ready for production MongoDB document processing!** 🚀
