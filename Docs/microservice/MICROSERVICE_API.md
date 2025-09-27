# Document Processing Microservice API

## Overview

A FastAPI-based microservice that processes student documents using Google Gemini AI and stores them in MongoDB. The service accepts Cloudinary URLs, extracts structured data, normalizes fields, and manages student document collections.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  FastAPI Server  │───▶│   Gemini AI     │    │    MongoDB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
                                │                                              ▲
                                ▼                                              │
                       ┌─────────────────┐                           ┌─────────────────┐
                       │ Cloudinary CDN  │                           │ Student Records │
                       └─────────────────┘                           └─────────────────┘
```

## Features

- ✅ **Document Processing**: AI-powered extraction using Gemini 2.0 Flash
- ✅ **Field Normalization**: Consistent schema across document types
- ✅ **MongoDB Storage**: Student-centric document organization
- ✅ **Cloudinary Integration**: Direct URL-based image processing
- ✅ **Type Validation**: Pydantic models with comprehensive validation
- ✅ **Error Handling**: Robust error management and logging
- ✅ **Health Monitoring**: Database and service health checks

## API Endpoints

### Core Microservice Endpoints

#### 1. Process Document

**POST** `/process-doc`

Process a document from Cloudinary URL and store in MongoDB.

**Request Body:**

```json
{
  "studentId": "12345",
  "docType": "AadharCard",
  "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/aadhaar.jpg"
}
```

**Response:**

```json
{
  "success": true,
  "studentId": "12345",
  "savedDocument": {
    "docType": "AadharCard",
    "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/aadhaar.jpg",
    "fields": {
      "Name": "Sanjan Acharya",
      "AadhaarNumber": "1234 5678 9012",
      "DOB": "2002-06-15",
      "Address": "Bangalore, Karnataka",
      "Gender": "Male"
    },
    "processedAt": "2025-09-27T18:45:00Z",
    "confidence": 0.95,
    "modelUsed": "gemini-2.0-flash-exp",
    "validationIssues": []
  },
  "message": "Document processed successfully"
}
```

#### 2. Get All Student Documents

**GET** `/students/{student_id}/documents`

Retrieve all documents for a specific student.

**Response:**

```json
{
  "success": true,
  "studentId": "12345",
  "documents": [...],
  "totalDocuments": 3,
  "createdAt": "2025-09-27T18:30:00Z",
  "updatedAt": "2025-09-27T18:45:00Z"
}
```

#### 3. Get Student Document by Type

**GET** `/students/{student_id}/documents/{doc_type}`

Retrieve the latest document of a specific type for a student.

**Response:**

```json
{
  "docType": "AadharCard",
  "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/abc.jpg",
  "fields": {
    "Name": "Sanjan Acharya",
    "DOB": "2002-06-15",
    "Address": "Bangalore"
  },
  "processedAt": "2025-09-27T18:45:00Z",
  "confidence": 0.95,
  "modelUsed": "gemini-2.0-flash-exp",
  "validationIssues": []
}
```

### Utility Endpoints

#### Health Check

**GET** `/health`

Check service and database health.

**Response:**

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database_connected": true,
  "gemini_configured": true
}
```

## Supported Document Types

| External Type          | Internal Schema         | Description                      |
| ---------------------- | ----------------------- | -------------------------------- |
| `AadharCard`           | `aadhaar_card`          | Indian Aadhaar Identity Card     |
| `MarkSheet10`          | `marksheet_10th`        | 10th Grade Marksheet             |
| `MarkSheet12`          | `marksheet_12th`        | 12th Grade Marksheet             |
| `TransferCertificate`  | `transfer_certificate`  | School Transfer Certificate      |
| `MigrationCertificate` | `migration_certificate` | University Migration Certificate |
| `EntranceScorecard`    | `entrance_scorecard`    | Competitive Exam Scorecard       |
| `AdmitCard`            | `admit_card`            | Examination Admit Card           |
| `CasteCertificate`     | `caste_certificate`     | Caste Certificate                |
| `DomicileCertificate`  | `domicile_certificate`  | Domicile/Residence Certificate   |

## Field Normalization

The service normalizes extracted fields to ensure consistency:

### Aadhaar Card Example

```json
// Raw extraction
{
  "full_name": "sanjan acharya",
  "aadhaar_number": "123456789012",
  "date_of_birth": "15/06/2002",
  "gender": "m"
}

// Normalized output
{
  "Name": "Sanjan Acharya",
  "AadhaarNumber": "1234 5678 9012",
  "DOB": "2002-06-15",
  "Gender": "Male"
}
```

### Marksheet Example

```json
// Raw extraction
{
  "student_name": "sanjan acharya",
  "subjects_marks": "Math: 95, Science: 90",
  "percentage": "91.0%"
}

// Normalized output
{
  "Name": "Sanjan Acharya",
  "Subjects": {
    "Math": 95,
    "Science": 90
  },
  "Percentage": 91.0
}
```

## MongoDB Schema

### Student Document Structure

```json
{
  "studentId": "12345",
  "documents": [
    {
      "docType": "AadharCard",
      "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/abc.jpg",
      "fields": {
        /* normalized fields */
      },
      "processedAt": "2025-09-27T18:45:00Z",
      "confidence": 0.95,
      "modelUsed": "gemini-2.0-flash-exp",
      "validationIssues": []
    }
  ],
  "createdAt": "2025-09-27T18:30:00Z",
  "updatedAt": "2025-09-27T18:45:00Z"
}
```

## Environment Configuration

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Database
MONGODB_URL=mongodb://localhost:27017/document_processor

# Optional
GEMINI_MODEL=gemini-2.0-flash-exp
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

## Error Handling

### HTTP Status Codes

| Code | Description                    |
| ---- | ------------------------------ |
| 200  | Success                        |
| 400  | Bad Request (validation error) |
| 404  | Student/Document not found     |
| 422  | Processing failed              |
| 500  | Internal server error          |
| 503  | Service unavailable            |

### Error Response Format

```json
{
  "success": false,
  "error": "Document processing failed",
  "details": "Invalid image format"
}
```

## Usage Examples

### Python Client

```python
import requests

# Process document
response = requests.post('http://localhost:8000/process-doc', json={
    'studentId': '12345',
    'docType': 'AadharCard',
    'cloudinaryUrl': 'https://res.cloudinary.com/demo/image/upload/abc.jpg'
})

if response.status_code == 200:
    result = response.json()
    print(f"Processed: {result['savedDocument']['fields']}")

# Get student documents
response = requests.get('http://localhost:8000/students/12345/documents')
documents = response.json()['documents']
```

### cURL Examples

```bash
# Process document
curl -X POST "http://localhost:8000/process-doc" \
  -H "Content-Type: application/json" \
  -d '{
    "studentId": "12345",
    "docType": "AadharCard",
    "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/abc.jpg"
  }'

# Get student documents
curl -X GET "http://localhost:8000/students/12345/documents"

# Health check
curl -X GET "http://localhost:8000/health"
```

## Deployment

### Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - MONGODB_URL=mongodb://mongo:27017/document_processor
    depends_on:
      - mongo

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_api_key"
export MONGODB_URL="mongodb://localhost:27017/document_processor"

# Start MongoDB
docker run -d -p 27017:27017 --name mongo mongo:7

# Start application
python app.py
```

## Performance Considerations

- **Gemini API**: Rate limits apply (check Google AI Studio)
- **MongoDB**: Index on `studentId` for fast lookups
- **Cloudinary**: Images cached temporarily during processing
- **Memory**: PIL image processing requires adequate RAM
- **Timeout**: 60-second default timeout for document processing

## Security Notes

- Validate Cloudinary URLs to prevent SSRF attacks
- Use MongoDB authentication in production
- Implement rate limiting for public endpoints
- Store sensitive data (API keys) securely
- Enable HTTPS in production deployments

## Monitoring

Monitor these metrics:

- Processing time per document
- Success/failure rates by document type
- Database connection health
- Gemini API quota usage
- Memory usage during image processing
