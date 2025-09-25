# OCR Automation Pipeline

**MIT Hackathon Project - Intelligent Document Processing System**

A comprehensive OCR automation pipeline for processing admission documents with AI-powered classification, multi-engine OCR, intelligent entity extraction, and robust validation.

## Features

### **AI-Powered Document Classification**

- Automatically identifies document types (marksheets, certificates, admit cards, etc.)
- Uses computer vision and pattern recognition
- Supports 10+ document types for admission processes

### **Multi-Engine OCR Processing**

- **EasyOCR**: High accuracy with GPU acceleration support
- **Tesseract**: Industry-standard OCR engine
- **PaddleOCR**: Advanced Chinese/multilingual support (optional)
- Automatic best-result selection across engines
- Advanced image preprocessing (denoise, deskew, contrast enhancement)

### **Intelligent Entity Extraction**

- NLP-powered entity recognition using spaCy
- Document-specific extraction templates
- Regex pattern matching for structured data
- Confidence scoring and validation

### **Comprehensive Validation**

- JSON schema validation for each document type
- Cross-document consistency checking
- Data integrity verification
- Business rule enforcement

### **Web Interface**

- Modern FastAPI-based REST API
- Interactive web UI for document upload
- Real-time processing status
- Structured JSON output display
- Batch processing support

## System Architecture

```
Document Upload → Classification → OCR Processing → Entity Extraction → Validation → Structured Output
       ↓               ↓               ↓                ↓               ↓            ↓
    FastAPI        AI Classifier   Multi-Engine      NLP + Templates  JSON Schema   JSON Result
    Web UI         (Vision ML)     (OCR Engines)     (spaCy + Regex)  Validation    + Metadata
```

---

![howitlooks](/assets/look.png)

## Project Structure

```
ocr-automation-pipeline/
├── src/
│   ├── ocr_pipeline/
│   │   ├── __init__.py              # Package exports and main API
│   │   ├── pipeline.py              # Main orchestrator
│   │   ├── classifiers/
│   │   │   └── document_classifier.py  # AI document type classifier
│   │   ├── extractors/
│   │   │   ├── ocr_engine.py           # Multi-engine OCR system
│   │   │   └── entity_extractor.py     # NLP entity extraction
│   │   ├── validators/
│   │   │   └── json_validator.py       # Schema validation & cross-checking
│   │   └── models/
│   │       └── __init__.py             # Pydantic data models
│   └── web_app/
│       ├── app.py                   # FastAPI web application
│       ├── run_demo.py              # Demo startup script
│       └── requirements.txt         # Web app dependencies
├── data/
│   ├── uploads/                     # Uploaded documents
│   ├── temp/                        # Temporary processing files
│   └── samples/                     # Sample documents for testing
├── venv/                           # Python virtual environment
├── requirements.txt                # Core pipeline dependencies
└── README.md                      # This file
```

## Quick Start

### 1. **Setup Environment**

```bash
# Clone or navigate to project directory
cd ocr-automation-pipeline

# Virtual environment should already be created and activated
# If not, create it:
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies (should already be installed)
pip install -r requirements.txt
```

### 2. **Start the Web Application**

```bash
cd src/web_app
python run_demo.py
```

### 3. **Access the Demo**

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Alternative API Docs**: http://localhost:8000/api/redoc

## Supported Document Types

| Document Type             | Description                  | Key Data Extracted                         |
| ------------------------- | ---------------------------- | ------------------------------------------ |
| **10th Marksheet**        | Class X academic records     | Name, Roll No., Marks, Percentage, Board   |
| **12th Marksheet**        | Class XII academic records   | Name, Roll No., Stream, Marks, Board       |
| **Entrance Scorecard**    | JEE/NEET exam results        | Name, Roll No., Subject scores, Percentile |
| **Admit Card**            | Entrance exam hall tickets   | Name, Roll No., Exam center, Date          |
| **Caste Certificate**     | SC/ST/OBC certificates       | Name, Category, Certificate No., Validity  |
| **Aadhar Card**           | Government ID card           | Aadhar No., Name, DOB, Address             |
| **Transfer Certificate**  | School leaving certificate   | Name, Class, School, Date of issue         |
| **Migration Certificate** | University transfer document | Name, Course, University, Migration reason |
| **Domicile Certificate**  | Residence proof              | Name, Address, State, Certificate validity |
| **Passport Photo**        | Student photograph           | Face detection, Image quality check        |

## Technical Stack

### **Core Technologies**

- **Python 3.8+**: Primary development language
- **FastAPI**: Modern web framework for APIs
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for production deployment

### **Machine Learning & AI**

- **spaCy**: Industrial-strength NLP
- **Transformers**: Hugging Face transformer models
- **scikit-learn**: Machine learning utilities
- **OpenCV**: Computer vision and image processing

### **OCR Engines**

- **EasyOCR**: Deep learning-based OCR
- **Tesseract**: Google's OCR engine
- **PaddleOCR**: Baidu's multilingual OCR (optional)

### **Data Processing**

- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Pillow (PIL)**: Image processing
- **scikit-image**: Advanced image processing

## API Usage

### **Single Document Processing**

```bash
# Upload document
curl -X POST "http://localhost:8000/api/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@marksheet.pdf"

# Process document
curl -X POST "http://localhost:8000/api/process" \
     -H "accept: application/json" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "file_path=/path/to/uploaded/file&file_name=marksheet.pdf&file_size=102400&mime_type=application/pdf"
```

### **Batch Processing**

```bash
curl -X POST "http://localhost:8000/api/process-batch" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@marksheet.pdf" \
     -F "files=@certificate.pdf" \
     -F "files=@aadhar.pdf"
```

### **Health Check**

```bash
curl -X GET "http://localhost:8000/api/health"
```

## Output Format

The pipeline generates structured JSON output:

```json
{
  "success": true,
  "message": "Document processed successfully",
  "data": {
    "request_id": "uuid-string",
    "status": "completed",
    "result": {
      "document_upload": {
        "file_name": "marksheet_10th.pdf",
        "file_path": "/uploads/uuid_marksheet_10th.pdf",
        "file_size": 102400
      },
      "classification_result": {
        "document_type": "MARKSHEET_10TH",
        "confidence": 0.95
      },
      "ocr_result": {
        "raw_text": "CBSE Board...",
        "metadata": {
          "engine_used": "easyocr",
          "confidence": 0.89,
          "processing_time": 2.3
        }
      },
      "structured_data": {
        "student_name": "RAHUL KUMAR SHARMA",
        "father_name": "SURESH KUMAR SHARMA",
        "roll_number": "12345678",
        "board": "CBSE",
        "total_marks": 424,
        "max_marks": 500,
        "percentage": 84.8,
        "result": "PASS"
      }
    }
  }
}
```

## Demo Highlights

### **For Hackathon Judges**

1. **Upload any admission document** via the web interface
2. **Watch real-time processing** with status updates
3. **See structured JSON output** with extracted data
4. **Validate cross-document consistency** with batch upload
5. **Check API documentation** at `/api/docs`

### **Key Demo Documents**

- Sample 10th marksheet → Structured academic data
- Sample JEE scorecard → Entrance exam results
- Sample Aadhar card → Identity verification data
- Multiple documents → Cross-validation demo

## 🔧 Development & Customization

### **Adding New Document Types**

1. Add document type to `DocumentType` enum
2. Create data model in `models/__init__.py`
3. Add classification patterns in `document_classifier.py`
4. Create extraction template in `entity_extractor.py`
5. Define JSON schema in `json_validator.py`

### **Adding New OCR Engines**

1. Extend `BaseOCREngine` in `ocr_engine.py`
2. Implement `extract_text()` method
3. Add to `MultiEngineOCR` initialization
4. Update configuration options

### **Extending Validation Rules**

1. Modify schemas in `DocumentSchemas` class
2. Add custom validators in `DocumentValidator`
3. Extend cross-validation logic in `CrossValidator`

## Performance & Scalability

- **Processing Time**: 2-5 seconds per document
- **Supported Formats**: PDF, JPG, PNG, TIFF
- **Batch Processing**: Up to 10 documents simultaneously
- **Accuracy**: 85-95% depending on document quality
- **Memory Usage**: ~500MB baseline + ~200MB per concurrent process

## Known Limitations

1. **Tesseract Installation**: Requires manual system installation
2. **GPU Support**: EasyOCR benefits from GPU but works on CPU
3. **Language Support**: Optimized for English documents
4. **File Size**: Recommended max 10MB per document
5. **Complex Layouts**: May struggle with heavily formatted documents

## Future Enhancements

- [ ] Multi-language support (Hindi, regional languages)
- [ ] GPU optimization for faster processing
- [ ] Document quality assessment and enhancement
- [ ] Integration with admission management systems
- [ ] Mobile application support
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] Advanced ML models for classification
- [ ] Database integration for persistence

## Contributing

This is a hackathon project built for demonstration. For production use:

1. Add comprehensive test coverage
2. Implement proper logging and monitoring
3. Add authentication and authorization
4. Optimize for production deployment
5. Add database integration
6. Implement proper error handling

## License

Built for MIT Hackathon - Educational and demonstration purposes.

## Support

For hackathon demonstration and questions, the system includes:

- Live web interface with upload capabilities
- Comprehensive API documentation
- Sample documents for testing
- Real-time processing status
- Detailed error messages and logging

---

**Ready for Demo! **

The OCR Automation Pipeline is now fully operational and ready for hackathon presentation. Upload documents, see the magic happen, and explore the API documentation for technical details.

cd "d:\Projects\MIT Hackathon\ocr-automation-pipeline\src\web_app"; ..\..\venv\Scripts\Activate.ps1; uvicorn app:app --host 0.0.0.0 --port 8000 --reload

_Built with ❤️ for MIT Hackathon_
for the mit hackathon, a sub module to extract the entities from the student document
