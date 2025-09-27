# Test Documents

This folder contains sample documents for testing the OCR automation pipeline.

## Document Types Supported

- **Aadhaar Card** - National ID card
- **PAN Card** - Permanent Account Number card  
- **Passport** - Travel document
- **Driving License** - Vehicle license
- **Voter ID** - Election card
- **Birth Certificate** - Official birth record
- **10th Marksheet** - Academic transcript
- **12th Marksheet** - Academic transcript
- **College Marksheet** - Academic transcript

## Usage

Place your test documents in this folder and reference them using relative paths in the API:

```json
{
  "studentId": "STUDENT_123",
  "docType": "AadharCard", 
  "documentPath": "assets/test_docs/aadhaar_sample.jpg"
}
```

## File Formats Supported

- JPG/JPEG
- PNG
- PDF
- WebP

## Note

These are for testing purposes only. Do not store real/sensitive documents here.