# API Documentation

## Overview

The Document Processor API provides endpoints for extracting structured data from Indian documents using Google's Gemini AI. The API supports various document types including Aadhaar cards, academic marksheets, birth certificates, and more.

## Base URL

```
http://localhost:8000/api
```

## Authentication

The API uses Gemini API key authentication configured via environment variables. No additional authentication is required for API endpoints.

## Supported Document Types

| Document Type | Code | Description |
|---------------|------|-------------|
| Aadhaar Card | `aadhaar` | Indian national ID card |
| Marksheet | `marksheet` | Academic transcripts |
| Birth Certificate | `birth_certificate` | Official birth documents |
| Passport | `passport` | Indian passport |
| PAN Card | `pan_card` | Permanent Account Number card |
| Driving License | `driving_license` | Indian driving license |
| Voter ID | `voter_id` | Election identity card |
| Ration Card | `ration_card` | Public distribution system card |
| Bank Statement | `bank_statement` | Financial institution statements |

## Endpoints

### Health Check

Check API availability and configuration.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "gemini_model": "gemini-2.0-flash-exp",
  "timestamp": "2025-09-26T10:30:00Z",
  "uptime": 3600.5
}
```

### Process Document

Extract structured data from a document image.

```http
POST /api/process
```

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Document image file
  - Supported formats: JPEG, PNG, WebP, HEIC, PDF
  - Maximum size: 10MB
  - Recommended: 1080p or higher resolution

- `document_type` (optional): Expected document type
  - If not provided, auto-detection is attempted
  - Valid values: See supported document types above

- `confidence_threshold` (optional): Minimum confidence score (0.0-1.0)
  - Default: 0.5
  - Higher values = more strict validation

**Request Examples:**

```bash
# Basic processing with auto-detection
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@document.jpg"

# With specific document type
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@aadhaar.jpg" \
  -F "document_type=aadhaar"

# With confidence threshold
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@marksheet.pdf" \
  -F "document_type=marksheet" \
  -F "confidence_threshold=0.8"
```

**Success Response (200):**
```json
{
  "success": true,
  "document_type": "aadhaar",
  "confidence": 0.95,
  "processing_time": 2.34,
  "extracted_data": {
    "name": "John Doe",
    "aadhaar_number": "1234-5678-9012",
    "date_of_birth": "01/01/1990",
    "gender": "Male",
    "address": {
      "line1": "123 Main Street",
      "city": "Mumbai",
      "state": "Maharashtra",
      "pincode": "400001"
    },
    "father_name": "Father's Name",
    "mobile": "+91-9876543210",
    "email": "john.doe@email.com"
  },
  "metadata": {
    "file_size": 1024576,
    "image_dimensions": [1920, 1080],
    "model_used": "gemini-2.0-flash-exp",
    "processing_timestamp": "2025-09-26T10:30:00Z"
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Invalid file format",
  "details": "Only JPEG, PNG, WebP, HEIC, and PDF files are supported",
  "error_code": "INVALID_FILE_FORMAT"
}
```

**Error Response (422):**
```json
{
  "success": false,
  "error": "Low confidence extraction",
  "confidence": 0.3,
  "confidence_threshold": 0.5,
  "details": "Document quality may be poor or document type mismatch",
  "error_code": "LOW_CONFIDENCE",
  "extracted_data": {
    "partial_name": "J*** D**"
  }
}
```

**Error Response (500):**
```json
{
  "success": false,
  "error": "Processing failed",
  "details": "Gemini API quota exceeded",
  "error_code": "API_QUOTA_EXCEEDED",
  "retry_after": 3600
}
```

## Response Schema

### Success Response

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` for successful responses |
| `document_type` | string | Detected/specified document type |
| `confidence` | number | Confidence score (0.0-1.0) |
| `processing_time` | number | Processing duration in seconds |
| `extracted_data` | object | Structured document data |
| `metadata` | object | Processing and file metadata |

### Error Response

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `false` for error responses |
| `error` | string | Human-readable error message |
| `details` | string | Additional error context |
| `error_code` | string | Machine-readable error code |

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `MISSING_FILE` | No file uploaded | 400 |
| `INVALID_FILE_FORMAT` | Unsupported file type | 400 |
| `FILE_TOO_LARGE` | File exceeds size limit | 400 |
| `INVALID_DOCUMENT_TYPE` | Unknown document type specified | 400 |
| `INVALID_CONFIDENCE_THRESHOLD` | Threshold not between 0.0-1.0 | 400 |
| `LOW_CONFIDENCE` | Extraction confidence below threshold | 422 |
| `DOCUMENT_NOT_READABLE` | Document image unclear/corrupted | 422 |
| `API_KEY_INVALID` | Gemini API key authentication failed | 500 |
| `API_QUOTA_EXCEEDED` | Gemini API usage limits reached | 500 |
| `PROCESSING_TIMEOUT` | Document processing timed out | 500 |
| `INTERNAL_ERROR` | Unexpected system error | 500 |

## Document Type Schemas

### Aadhaar Card
```json
{
  "name": "string",
  "aadhaar_number": "string (12 digits with optional hyphens)",
  "date_of_birth": "string (DD/MM/YYYY)",
  "gender": "string (Male/Female/Other)",
  "address": {
    "line1": "string",
    "line2": "string (optional)",
    "city": "string",
    "state": "string",
    "pincode": "string (6 digits)"
  },
  "father_name": "string",
  "mobile": "string (optional)",
  "email": "string (optional)"
}
```

### Academic Marksheet
```json
{
  "student_name": "string",
  "roll_number": "string",
  "registration_number": "string",
  "institution_name": "string",
  "board_university": "string",
  "academic_year": "string",
  "class_grade": "string",
  "subjects": [
    {
      "subject_name": "string",
      "marks_obtained": "number",
      "max_marks": "number",
      "grade": "string"
    }
  ],
  "total_marks": "number",
  "percentage": "number",
  "result": "string (Pass/Fail)",
  "issue_date": "string (DD/MM/YYYY)"
}
```

### Birth Certificate
```json
{
  "child_name": "string",
  "date_of_birth": "string (DD/MM/YYYY)",
  "place_of_birth": "string",
  "gender": "string",
  "father_name": "string",
  "mother_name": "string",
  "registration_number": "string",
  "registration_date": "string (DD/MM/YYYY)",
  "registrar_office": "string"
}
```

## Rate Limits

- Default: 100 requests per hour per IP
- Burst: 10 requests per minute
- Large files (>5MB): 20 requests per hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1695715200
```

## Best Practices

### Image Quality
- Use high resolution (1080p+) images
- Ensure good lighting and contrast
- Avoid blurry or skewed images
- Remove shadows and glare

### File Formats
- JPEG: Good for photos, moderate compression
- PNG: Best for scanned documents, lossless
- PDF: Good for multi-page documents
- WebP: Smaller file sizes, good quality

### Error Handling
```javascript
// Example JavaScript error handling
try {
  const response = await fetch('/api/process', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (!result.success) {
    // Handle specific errors
    switch (result.error_code) {
      case 'LOW_CONFIDENCE':
        console.warn('Document quality may be poor');
        // Show user feedback options
        break;
      case 'API_QUOTA_EXCEEDED':
        console.error('Service temporarily unavailable');
        // Retry after specified time
        break;
      default:
        console.error('Processing failed:', result.error);
    }
  }
} catch (error) {
  console.error('Network error:', error);
}
```

### Performance Optimization
- Compress images before upload when possible
- Use appropriate confidence thresholds
- Implement client-side caching for repeated requests
- Consider batch processing for multiple documents

## SDK Examples

### Python
```python
import requests

def process_document(file_path, document_type=None):
    url = "http://localhost:8000/api/process"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {}
        
        if document_type:
            data['document_type'] = document_type
            
        response = requests.post(url, files=files, data=data)
        return response.json()

# Usage
result = process_document('aadhaar.jpg', 'aadhaar')
if result['success']:
    print(f"Name: {result['extracted_data']['name']}")
    print(f"Aadhaar: {result['extracted_data']['aadhaar_number']}")
```

### cURL
```bash
#!/bin/bash
# Process document with error handling

response=$(curl -s -X POST "http://localhost:8000/api/process" \
  -F "file=@$1" \
  -F "document_type=$2")

success=$(echo "$response" | jq -r '.success')

if [ "$success" = "true" ]; then
  echo "Processing successful!"
  echo "$response" | jq '.extracted_data'
else
  echo "Processing failed:"
  echo "$response" | jq '.error'
fi
```

## Testing

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Process test image
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@tests/fixtures/sample_aadhaar.jpg" \
  -F "document_type=aadhaar"
```

### Sample Test Data
Test images are available in the `tests/fixtures/` directory:
- `sample_aadhaar.jpg`
- `sample_marksheet.pdf`
- `sample_birth_certificate.png`

## Changelog

### v1.0.0
- Initial API release
- Support for 9 Indian document types
- Gemini 2.0 Flash integration
- Auto document type detection
- Confidence scoring
- Comprehensive error handling