"""
FastAPI Application for Document Processing
Modern async API with automatic documentation and MongoDB integration
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.document_processor.core import create_processor, ProcessingResult
from src.document_processor.schemas import get_supported_types, get_schema
from src.document_processor.database import get_database, StudentDocument, DocumentEntry
from src.document_processor.models import (
    ProcessDocumentRequest, ProcessDocumentResponse, ProcessedDocumentResponse, ErrorResponse,
    HealthResponse, StudentDocumentsResponse, get_internal_doc_type
)
from src.document_processor.normalizer import normalize_fields
from src.document_processor.cloudinary_service import download_image_from_url, CloudinaryService
from src.document_processor.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
processor = None
cloudinary_service = CloudinaryService()
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global processor
    
    # Startup
    logger.info("Starting Document Processor API...")
    try:
        # Initialize document processor
        processor = create_processor()
        logger.info("Document processor initialized successfully")
        
        # Initialize database connection
        db_manager = await get_database()
        await db_manager.connect_db(settings.mongodb_url)
        logger.info("Database connection established")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Document Processor API...")
    try:
        db_manager = await get_database()
        await db_manager.disconnect_db()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="Smart Document Processor Microservice",
    description="AI-powered document processing with MongoDB storage for student document management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legacy response models (keeping for backward compatibility)
class ProcessingResponse(BaseModel):
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    processing_time: float
    validation_issues: list[str]
    confidence_score: float
    model_used: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentSchema(BaseModel):
    description: str
    required_fields: list[str]
    optional_fields: list[str]
    validation_rules: Dict[str, str]

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title> Smart Document Processor</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; color: #333; padding: 20px;
            }
            .container { 
                max-width: 1000px; margin: 0 auto; background: white; 
                border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; 
                padding: 30px; text-align: center;
            }
            .header h1 { font-size: 2.5em; font-weight: 700; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 1.1em; }
            
            .content { padding: 30px; }
            .upload-section { 
                background: #f8f9fa; border-radius: 15px; padding: 30px; margin-bottom: 30px;
                border: 2px dashed #dee2e6; transition: all 0.3s;
            }
            .upload-section:hover { border-color: #4CAF50; }
            
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
            small { display: block; margin-top: 5px; color: #666; font-size: 12px; }
            input[type="file"], select { 
                width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px;
                font-size: 16px; background: white;
            }
            input[type="file"]:focus, select:focus { border-color: #4CAF50; outline: none; }
            
            .btn { 
                background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; 
                padding: 15px 30px; border: none; border-radius: 50px; font-size: 18px;
                cursor: pointer; transition: transform 0.3s; font-weight: 600; width: 100%;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
            
            .result { 
                margin-top: 30px; padding: 30px; border-radius: 15px; 
                border-left: 5px solid #4CAF50; background: #e8f5e8;
            }
            .result.error { background: #ffebee; border-left-color: #f44336; }
            
            .metrics { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
            .metric { 
                background: white; padding: 15px; border-radius: 10px; text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); flex: 1; min-width: 150px;
            }
            .metric-value { font-size: 1.5em; font-weight: 700; color: #4CAF50; }
            .metric-label { font-size: 0.9em; color: #666; margin-top: 5px; }
            
            .json-display { 
                background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; 
                padding: 20px; font-family: 'Courier New', monospace; white-space: pre-wrap;
                max-height: 500px; overflow-y: auto; font-size: 14px;
            }
            
            .validation-issues { margin-top: 20px; }
            .issue { 
                background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px;
                padding: 10px; margin-bottom: 10px; color: #856404;
            }
            
            .loading { text-align: center; color: #666; }
            .api-links { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; }
            .api-links h4 { margin-bottom: 15px; color: #333; }
            .api-links a { color: #4CAF50; text-decoration: none; margin-right: 20px; }
            .api-links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1> Smart Document Processor</h1>
                <p>AI-powered document extraction using Local API | Upload Images & PDFs | FastAPI + Modern Interface</p>
            </div>
            
            <div class="content">
                <div class="upload-section">
                    <form id="uploadForm">
                        <div class="form-group">
                            <label for="student_id">👤 Student ID (Optional - for MongoDB storage)</label>
                            <input 
                                type="text" 
                                id="student_id" 
                                placeholder="Enter student ID to save in database (e.g., STUDENT_123)"
                            />
                        </div>
                        
                        <div class="form-group">
                            <label for="document"> Select Document (Image or PDF)</label>
                            <input type="file" id="document" accept="image/*,application/pdf" required>
                            <small>Supported: JPG, PNG, GIF, WebP, PDF</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="doc_type"> Document Type (optional - auto-detect if not selected)</label>
                            <select id="doc_type">
                                <option value=""> Auto-detect</option>
                                <option value="aadhaar_card"> Aadhaar Card</option>
                                <option value="marksheet_10th"> 10th Marksheet</option>
                                <option value="marksheet_12th"> 12th Marksheet</option>
                                <option value="transfer_certificate"> Transfer Certificate</option>
                                <option value="migration_certificate"> Migration Certificate</option>
                                <option value="entrance_scorecard"> Entrance Scorecard</option>
                                <option value="admit_card"> Admit Card</option>
                                <option value="caste_certificate"> Caste Certificate</option>
                                <option value="domicile_certificate"> Domicile Certificate</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn" id="submitBtn"> Process Document</button>
                    </form>
                </div>
                
                <div id="result" style="display: none;"></div>
                
                <div class="api-links">
                    <h4>🔗 API Documentation</h4>
                    <a href="/docs" target="_blank">Interactive API Docs (Swagger)</a>
                    <a href="/redoc" target="_blank">ReDoc Documentation</a>
                    <a href="/health" target="_blank">Health Check</a>
                    <a href="/schemas" target="_blank">Document Schemas</a>
                </div>
            </div>
        </div>
        
        <script>
            // Toast notification function
            function showToast(message, type = 'success') {
                const toast = document.createElement('div');
                toast.style.cssText = `
                    position: fixed; top: 20px; right: 20px; z-index: 10000;
                    padding: 15px 25px; border-radius: 10px; font-weight: 600;
                    color: white; font-size: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    transform: translateX(400px); transition: all 0.3s ease;
                    background: ${type === 'success' ? 'linear-gradient(135deg, #4CAF50, #2E7D32)' : 'linear-gradient(135deg, #f44336, #d32f2f)'};
                `;
                toast.textContent = message;
                document.body.appendChild(toast);
                
                setTimeout(() => toast.style.transform = 'translateX(0)', 100);
                setTimeout(() => {
                    toast.style.transform = 'translateX(400px)';
                    setTimeout(() => document.body.removeChild(toast), 300);
                }, 4000);
            }
            
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const fileInput = document.getElementById('document');
                const docTypeInput = document.getElementById('doc_type');
                const studentIdInput = document.getElementById('student_id');
                const submitBtn = document.getElementById('submitBtn');
                const resultDiv = document.getElementById('result');
                
                if (!fileInput.files[0]) {
                    alert('Please select a file');
                    return;
                }
                
                // Validate file type (images and PDFs)
                const file = fileInput.files[0];
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Please select an image file (JPG, PNG, GIF, WebP) or PDF document');
                    return;
                }
                
                // Show loading
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="loading">🔍 Processing your document (image/PDF)...</div>';
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                if (docTypeInput.value) {
                    formData.append('document_type', docTypeInput.value);
                }
                if (studentIdInput.value.trim()) {
                    formData.append('student_id', studentIdInput.value.trim());
                }
                
                try {
                    const response = await axios.post('/api/process', formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    
                    const result = response.data;
                    
                    if (result.success) {
                        resultDiv.className = 'result';
                        
                        // Check if data was stored in MongoDB
                        const mongoStored = result.metadata?.mongodb_stored;
                        const studentId = result.metadata?.student_id;
                        
                        if (mongoStored) {
                            showToast(`✅ Document processed and  to database for student: ${studentId}`, 'success');
                        } else if (studentId) {
                            showToast(`⚠️ Document processed but failed to save to database`, 'error');
                        } else {
                            showToast(`✅ Document processed successfully (not saved - no student ID provided)`, 'success');
                        }
                        
                        resultDiv.innerHTML = `
                            <div class="metrics">
                                <div class="metric">
                                    <div class="metric-value">${result.document_type.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</div>
                                    <div class="metric-label">Document Type</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${(result.confidence_score * 100).toFixed(0)}%</div>
                                    <div class="metric-label">Confidence</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${result.processing_time.toFixed(2)}s</div>
                                    <div class="metric-label">Processing Time</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">${mongoStored ? '✅ Saved' : '❌ Not Saved'}</div>
                                    <div class="metric-label">Database Storage</div>
                                </div>
                            </div>
                            
                            ${result.validation_issues && result.validation_issues.length > 0 ? `
                            <div class="validation-issues">
                                <h4>⚠️ Validation Issues:</h4>
                                ${result.validation_issues.map(issue => `<div class="issue">${issue}</div>`).join('')}
                            </div>
                            ` : ''}
                            
                            <h4>Extracted Data:</h4>
                            <div class="json-display">${JSON.stringify(result.extracted_data, null, 2)}</div>
                            
                            ${studentId && mongoStored ? `
                            <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 10px; border-left: 4px solid #4CAF50;">
                                <strong>Success!</strong> Document has been stored in MongoDB for student <strong>${studentId}</strong>.
                                <br><small>You can retrieve this data later using the student ID.</small>
                            </div>
                            ` : ''}
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `
                            <h3>❌ Processing Failed</h3>
                            <p><strong>Error:</strong> ${result.error_message}</p>
                        `;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>❌ Request Failed</h3>
                        <p><strong>Error:</strong> ${error.response?.data?.detail || error.message}</p>
                    `;
                }
                
                // Reset button
                submitBtn.disabled = false;
                submitBtn.textContent = ' Process Document';
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    db_manager = await get_database()
    db_healthy = await db_manager.health_check()
    
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        version="2.0.0",
        database_connected=db_healthy,
        gemini_configured=bool(os.getenv("GEMINI_API_KEY"))
    )

# NEW MICROSERVICE ENDPOINTS

@app.post("/process-doc", response_model=ProcessDocumentResponse)
async def process_document_from_cloudinary(request: ProcessDocumentRequest):
    """
    Process a document from Cloudinary URL or local file path and store in MongoDB
    
    Main endpoint for the document processing microservice:
    1. Downloads image from Cloudinary URL OR uses local file path
    2. Processes with local API to extract structured data
    3. Normalizes fields based on document type
    4. Stores/updates in MongoDB under student record
    
    Returns the processed document data
    """
    if not processor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document processor not available"
        )
    
    temp_file_path = None
    use_local_file = False
    
    try:
        logger.info(f"Processing document for student {request.studentId}: {request.docType}")
        
        # Determine file path - either download from Cloudinary or use local file
        if request.cloudinaryUrl:
            # Download image from Cloudinary
            temp_file_path = await download_image_from_url(request.cloudinaryUrl)
            logger.info(f"Downloaded image from Cloudinary: {temp_file_path}")
        elif request.documentPath:
            # Use local file path for testing
            import os
            temp_file_path = os.path.abspath(request.documentPath)
            use_local_file = True
            
            # Verify file exists
            if not os.path.exists(temp_file_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Local document file not found: {request.documentPath}"
                )
            logger.info(f"Using local test file: {temp_file_path}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either cloudinaryUrl or documentPath must be provided"
            )
        
        # Convert external document type to internal schema type
        internal_doc_type = get_internal_doc_type(request.docType)
        
        # Process document with Gemini
        result = await processor.process_document_async(temp_file_path, internal_doc_type)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Document processing failed: {result.error_message}"
            )
        
        # Normalize extracted fields
        normalized_fields = normalize_fields(result.extracted_data, internal_doc_type)
        
        # Create document entry for database
        doc_entry = DocumentEntry(
            docType=request.docType,  # Store external format
            cloudinaryUrl=request.cloudinaryUrl,
            documentPath=request.documentPath if use_local_file else None,
            fields=normalized_fields,
            confidence=result.confidence_score,
            modelUsed=result.model_used,
            validationIssues=result.validation_issues
        )
        
        # Find or create student record
        student = await StudentDocument.find_or_create_student(request.studentId)
        
        # Add document to student record
        updated_student = await student.add_document(doc_entry)
        
        # Find the saved document (latest one of this type)
        saved_doc = await updated_student.get_latest_document(request.docType)
        
        if not saved_doc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document was processed but not found in database"
            )
        
        # Create response
        response = ProcessDocumentResponse(
            success=True,
            studentId=request.studentId,
            savedDocument=ProcessedDocumentResponse(
                docType=saved_doc.docType,
                cloudinaryUrl=saved_doc.cloudinaryUrl,
                documentPath=saved_doc.documentPath if hasattr(saved_doc, 'documentPath') else None,
                fields=saved_doc.fields,
                processedAt=saved_doc.processedAt,
                confidence=saved_doc.confidence,
                modelUsed=saved_doc.modelUsed,
                validationIssues=saved_doc.validationIssues
            ),
            message=f"Document {request.docType} processed and saved successfully"
        )
        
        logger.info(f"Successfully processed {request.docType} for student {request.studentId}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temporary file only if it was downloaded (not local)
        if temp_file_path and not use_local_file:
            CloudinaryService.cleanup_temp_file(temp_file_path)

@app.get("/students/{student_id}/documents", response_model=StudentDocumentsResponse)
async def get_student_documents(student_id: str):
    """
    Get all documents for a specific student
    
    Returns all processed documents stored for the given student ID
    """
    try:
        student = await StudentDocument.find_one(StudentDocument.studentId == student_id)
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Convert documents to response format
        processed_docs = []
        for doc in student.documents:
            processed_docs.append(ProcessedDocumentResponse(
                docType=doc.docType,
                cloudinaryUrl=doc.cloudinaryUrl,
                fields=doc.fields,
                processedAt=doc.processedAt,
                confidence=doc.confidence,
                modelUsed=doc.modelUsed,
                validationIssues=doc.validationIssues
            ))
        
        return StudentDocumentsResponse(
            success=True,
            studentId=student_id,
            documents=processed_docs,
            totalDocuments=len(processed_docs),
            createdAt=student.createdAt,
            updatedAt=student.updatedAt
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving student documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve student documents: {str(e)}"
        )

@app.get("/students/{student_id}/documents/{doc_type}", response_model=ProcessedDocumentResponse)
async def get_student_document_by_type(student_id: str, doc_type: str):
    """
    Get the latest document of a specific type for a student
    """
    try:
        student = await StudentDocument.find_one(StudentDocument.studentId == student_id)
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Get the latest document of specified type
        doc = await student.get_latest_document(doc_type)
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document type {doc_type} not found for student {student_id}"
            )
        
        return ProcessedDocumentResponse(
            docType=doc.docType,
            cloudinaryUrl=doc.cloudinaryUrl,
            fields=doc.fields,
            processedAt=doc.processedAt,
            confidence=doc.confidence,
            modelUsed=doc.modelUsed,
            validationIssues=doc.validationIssues
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving student document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )

@app.get("/schemas", response_model=Dict[str, DocumentSchema])
async def get_schemas():
    """Get all document schemas"""
    from src.document_processor.schemas import DOCUMENT_SCHEMAS
    
    schemas = {}
    for doc_type, schema in DOCUMENT_SCHEMAS.items():
        if doc_type != 'default':
            schemas[doc_type] = DocumentSchema(**schema)
    
    return schemas

@app.post("/api/process", response_model=ProcessingResponse)
async def process_document(
    file: UploadFile = File(..., description="Document image file"),
    document_type: Optional[str] = Form(None, description="Document type hint (optional)"),
    student_id: Optional[str] = Form(None, description="Student ID for MongoDB storage (optional)")
):
    """
    Process a document image and extract structured data
    
    - **file**: Document image (JPG, PNG, etc.)
    - **document_type**: Optional hint about document type for better accuracy
    - **student_id**: Optional student ID - if provided, data will be stored in MongoDB
    
    Returns structured JSON data with validation results
    """
    if not processor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document processor not available"
        )
    
    # Validate file type (allow images and PDFs)
    allowed_types = ['image/', 'application/pdf']
    if not any(file.content_type.startswith(t) for t in allowed_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (jpg, png, etc.) or PDF"
        )
    
    # Validate document type
    if document_type and document_type not in get_supported_types() + ['other']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported document type: {document_type}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Process document
            result = await processor.process_document_async(temp_path, document_type)
            
            # Store in MongoDB if student_id is provided
            mongodb_stored = False
            if student_id and result.success:
                try:
                    # Use document type from result if available, fallback to provided or 'other'
                    detected_doc_type = result.document_type if result.document_type != 'unknown' else document_type or 'other'
                    
                    # Normalize extracted fields
                    normalized_fields = normalize_fields(result.extracted_data, detected_doc_type)
                    
                    # Create document entry for database
                    doc_entry = DocumentEntry(
                        docType=detected_doc_type,  # Use detected type
                        cloudinaryUrl=None,  # No cloudinary URL for uploaded files
                        documentPath=None,   # Temporary file, don't store path
                        fields=normalized_fields,
                        confidence=result.confidence_score,
                        modelUsed=result.model_used,
                        validationIssues=result.validation_issues
                    )
                    
                    # Find or create student record
                    student = await StudentDocument.find_or_create_student(student_id)
                    
                    # Add document to student record
                    await student.add_document(doc_entry)
                    mongodb_stored = True
                    
                    logger.info(f"Document stored in MongoDB for student {student_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to store in MongoDB: {e}")
                    # Continue without failing the request
                    mongodb_stored = False
            
            # Create response with MongoDB storage info
            response = ProcessingResponse(
                success=result.success,
                document_type=result.document_type,
                extracted_data=result.extracted_data,
                processing_time=result.processing_time,
                validation_issues=result.validation_issues,
                confidence_score=result.confidence_score,
                model_used=result.model_used,
                error_message=result.error_message,
                metadata=result.metadata
            )
            
            # Add MongoDB storage status to metadata
            if hasattr(response, 'metadata') and response.metadata:
                response.metadata['mongodb_stored'] = mongodb_stored
            else:
                response.metadata = {'mongodb_stored': mongodb_stored}
            
            if student_id:
                response.metadata['student_id'] = student_id
                
            return response
            
        finally:
            # Clean up temp file with better error handling
            try:
                import time
                time.sleep(0.1)  # Small delay to ensure file is released
                if os.path.exists(temp_path):
                    Path(temp_path).unlink(missing_ok=True)
                    logger.debug(f"Cleaned up temp file: {temp_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")
                # Try alternative cleanup method
                try:
                    import gc
                    gc.collect()  # Force garbage collection
                    time.sleep(0.2)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as alt_cleanup_error:
                    logger.error(f"Alternative cleanup also failed for {temp_path}: {alt_cleanup_error}")
                    # File will be cleaned up by OS eventually
            
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )

@app.get("/api/process/batch")
async def batch_processing_info():
    """Information about batch processing capabilities"""
    return {
        "message": "Batch processing not implemented yet",
        "suggested_approach": "Call /api/process multiple times for batch processing",
        "rate_limits": "Depends on Gemini API quotas"
    }

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not found in environment variables")
        print("Set it with: set GEMINI_API_KEY=your_api_key_here")
    
    print(" Starting FastAPI Document Processor...")
    print("Web interface: http://127.0.0.1:8000")
    print(" API docs: http://127.0.0.1:8000/docs")
    print(" ReDoc: http://127.0.0.1:8000/redoc")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")