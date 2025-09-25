# Sample Documents for OCR Pipeline Demo

# MIT Hackathon Project

This directory contains sample documents for testing the OCR automation pipeline.

## Sample Documents Included:

### 1. Academic Documents

- `sample_marksheet_10th.pdf` - 10th standard marksheet
- `sample_marksheet_12th.pdf` - 12th standard marksheet
- `sample_entrance_scorecard.pdf` - JEE/NEET entrance exam scorecard
- `sample_entrance_admit_card.pdf` - Entrance exam admit card

### 2. Identity Documents

- `sample_aadhar_card.pdf` - Aadhar card sample
- `sample_caste_certificate.pdf` - Caste certificate
- `sample_domicile_certificate.pdf` - Domicile certificate

### 3. Certificates

- `sample_transfer_certificate.pdf` - Transfer certificate
- `sample_migration_certificate.pdf` - Migration certificate
- `sample_passing_certificate.pdf` - Passing certificate

### 4. Photos

- `sample_passport_photo.jpg` - Passport size photo

## Usage Instructions:

1. Start the web application: `python run_demo.py`
2. Open http://localhost:8000 in your browser
3. Upload any of these sample documents
4. See the structured JSON output

## Document Structure:

Each document is designed to test specific extraction patterns:

- **Names and personal information**
- **Dates and academic years**
- **Marks, grades, and percentages**
- **Institution names and codes**
- **Registration and roll numbers**
- **Address information**
- **Certificate numbers and validity**

## Expected Output:

The pipeline will:

1. **Classify** the document type automatically
2. **Extract** text using multiple OCR engines
3. **Parse** entities using NLP and pattern matching
4. **Validate** data against JSON schemas
5. **Cross-validate** across multiple documents

Perfect for demonstrating the complete admission document processing workflow!
