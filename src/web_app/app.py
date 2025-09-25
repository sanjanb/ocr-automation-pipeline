"""
FastAPI Web Application for OCR Automation Pipeline
MIT Hackathon Project

This is the web interface for the OCR automation pipeline demo.
Provides REST API endpoints and a simple web UI for document upload and processing.
"""

import os
import sys
import uuid
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

# Pipeline imports
from ocr_pipeline import (
    OCRPipeline, 
    create_pipeline, 
    ProcessingRequest,
    ProcessingResult,
    BatchProcessingRequest,
    BatchProcessingResult,
    DocumentUpload,
    ProcessingStatus,
    APIResponse,
    DocumentType,
    OCREngine
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OCR Automation Pipeline",
    description="MIT Hackathon - Intelligent Document Processing System",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
pipeline: Optional[OCRPipeline] = None
upload_dir = Path("data/uploads")
temp_dir = Path("data/temp")
processing_results: Dict[str, ProcessingResult] = {}

# Templates and static files
templates = Jinja2Templates(directory="templates")
static_dir = Path("static")

# Create directories if they don't exist
upload_dir.mkdir(parents=True, exist_ok=True)
temp_dir.mkdir(parents=True, exist_ok=True)
static_dir.mkdir(exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize the OCR pipeline on startup"""
    global pipeline
    
    try:
        logger.info("Starting OCR Automation Pipeline...")
        
        # Initialize pipeline with available engines
        available_engines = [OCREngine.TESSERACT, OCREngine.EASYOCR]
        pipeline = create_pipeline(ocr_engines=available_engines)
        
        logger.info("OCR Pipeline initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {str(e)}")
        pipeline = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down OCR Pipeline...")

# Serve static files (CSS, JS, images)
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# API Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with upload interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "OCR Automation Pipeline - MIT Hackathon",
        "supported_types": [dt.value for dt in DocumentType if dt != DocumentType.OTHER]
    })

@app.get("/api/health")
async def health_check():
    """System health check endpoint"""
    if pipeline is None:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": "Pipeline not initialized"}
        )
    
    health_status = pipeline.health_check()
    
    return APIResponse(
        success=health_status["overall"] in ["healthy"],
        message=f"System status: {health_status['overall']}",
        data={
            "status": health_status["overall"],
            "components": health_status,
            "stats": pipeline.get_pipeline_stats(),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/api/stats")
async def get_stats():
    """Get pipeline processing statistics"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    stats = pipeline.get_pipeline_stats()
    
    return APIResponse(
        success=True,
        message="Pipeline statistics retrieved",
        data=stats
    )

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a document file"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{file.filename}"
        file_path = upload_dir / safe_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file info
        file_size = file_path.stat().st_size
        
        # Create DocumentUpload model
        document_upload = DocumentUpload(
            file_name=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        logger.info(f"📎 File uploaded: {file.filename} ({file_size} bytes)")
        
        return APIResponse(
            success=True,
            message="File uploaded successfully",
            data=document_upload.dict()
        )
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/process")
async def process_document(
    background_tasks: BackgroundTasks,
    file_path: str = Form(...),
    file_name: str = Form(...),
    file_size: int = Form(...),
    mime_type: str = Form(...)
):
    """Process an uploaded document"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        # Create processing request
        document_upload = DocumentUpload(
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )
        
        request = ProcessingRequest(
            document_upload=document_upload,
            processing_options={}
        )
        
        # Process document in background
        result = pipeline.process_document(request)
        
        # Store result for retrieval
        processing_results[result.request_id] = result
        
        logger.info(f"📋 Document processed: {file_name} (ID: {result.request_id})")
        
        return APIResponse(
            success=True,
            message="Document processed successfully",
            data={
                "request_id": result.request_id,
                "status": result.status.value,
                "result": result.dict()
            }
        )
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/result/{request_id}")
async def get_processing_result(request_id: str):
    """Get processing result by request ID"""
    if request_id not in processing_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    result = processing_results[request_id]
    
    return APIResponse(
        success=True,
        message="Processing result retrieved",
        data=result.dict()
    )

@app.post("/api/process-batch")
async def process_batch(files: List[UploadFile] = File(...)):
    """Process multiple documents in batch"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if len(files) > 10:  # Limit batch size for demo
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed in batch")
    
    try:
        document_uploads = []
        
        # Upload all files first
        for file in files:
            if not file.filename:
                continue
                
            # Generate unique filename
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}_{file.filename}"
            file_path = upload_dir / safe_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = file_path.stat().st_size
            
            document_uploads.append(DocumentUpload(
                file_name=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                mime_type=file.content_type or "application/octet-stream"
            ))
        
        # Create batch processing request
        batch_request = BatchProcessingRequest(
            documents=document_uploads,
            cross_validate=True
        )
        
        # Process batch
        batch_result = pipeline.process_batch(batch_request)
        
        # Store individual results
        for individual_result in batch_result.individual_results:
            processing_results[individual_result.request_id] = individual_result
        
        logger.info(f"📚 Batch processed: {len(files)} files (ID: {batch_result.batch_id})")
        
        return APIResponse(
            success=True,
            message="Batch processed successfully",
            data={
                "batch_id": batch_result.batch_id,
                "status": batch_result.batch_status.value,
                "result": batch_result.dict()
            }
        )
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/api/supported-types")
async def get_supported_document_types():
    """Get list of supported document types"""
    return APIResponse(
        success=True,
        message="Supported document types retrieved",
        data={
            "types": [
                {
                    "value": dt.value,
                    "name": dt.value.replace("_", " ").title(),
                    "description": get_document_description(dt)
                }
                for dt in DocumentType if dt != DocumentType.OTHER
            ]
        }
    )

def get_document_description(doc_type: DocumentType) -> str:
    """Get human-readable description for document type"""
    descriptions = {
        DocumentType.MARKSHEET_10TH: "10th Standard/Class X Marksheet or Report Card",
        DocumentType.MARKSHEET_12TH: "12th Standard/Class XII Marksheet or Report Card",
        DocumentType.ENTRANCE_SCORECARD: "Entrance Exam Scorecard (JEE, NEET, etc.)",
        DocumentType.ENTRANCE_ADMIT_CARD: "Entrance Exam Admit Card or Hall Ticket",
        DocumentType.CASTE_CERTIFICATE: "Caste Certificate (SC/ST/OBC/EWS)",
        DocumentType.DOMICILE_CERTIFICATE: "Domicile/Residence Certificate",
        DocumentType.AADHAR_CARD: "Aadhar Card (UID)",
        DocumentType.TRANSFER_CERTIFICATE: "Transfer Certificate (TC)",
        DocumentType.MIGRATION_CERTIFICATE: "Migration Certificate",
        DocumentType.PASSING_CERTIFICATE: "Passing/Completion Certificate",
        DocumentType.PASSPORT_PHOTO: "Passport Size Photo"
    }
    return descriptions.get(doc_type, "Document")

@app.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    """Demo page showing processing results"""
    recent_results = list(processing_results.values())[-10:]  # Show last 10 results
    
    return templates.TemplateResponse("demo.html", {
        "request": request,
        "title": "OCR Pipeline Demo Results",
        "results": recent_results,
        "stats": pipeline.get_pipeline_stats() if pipeline else {}
    })

# Create HTML templates
@app.on_event("startup")
async def create_templates():
    """Create HTML templates for the demo"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create index.html template
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .upload-area {
            border: 2px dashed #007bff;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background-color: #f8f9fa;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            background-color: #e9ecef;
            border-color: #0056b3;
        }
        .result-card {
            margin-top: 20px;
            border-left: 4px solid #28a745;
        }
        .processing {
            border-left-color: #ffc107;
        }
        .error {
            border-left-color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-md-8 offset-md-2">
                <div class="text-center mb-5">
                    <h1 class="display-4 text-primary">
                        <i class="fas fa-file-text"></i> OCR Automation Pipeline
                    </h1>
                    <p class="lead">MIT Hackathon - Intelligent Document Processing System</p>
                    <p class="text-muted">Upload student documents and get structured JSON data instantly!</p>
                </div>

                <div class="card shadow">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-upload"></i> Upload Documents
                        </h5>
                        
                        <form id="uploadForm" enctype="multipart/form-data">
                            <div class="upload-area" id="uploadArea">
                                <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                                <h5>Drag & drop files here or click to browse</h5>
                                <p class="text-muted">Supported formats: PDF, JPG, PNG, TIFF</p>
                                <input type="file" id="fileInput" multiple accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif" style="display: none;">
                                <button type="button" class="btn btn-primary" onclick="document.getElementById('fileInput').click();">
                                    <i class="fas fa-folder-open"></i> Choose Files
                                </button>
                            </div>
                            
                            <div id="fileList" class="mt-3"></div>
                            
                            <div class="mt-3 text-center">
                                <button type="submit" class="btn btn-success btn-lg" id="processBtn" disabled>
                                    <i class="fas fa-cogs"></i> Process Documents
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div class="mt-4">
                    <h5><i class="fas fa-info-circle"></i> Supported Document Types</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item"><i class="fas fa-graduation-cap text-primary"></i> 10th & 12th Marksheets</li>
                                <li class="list-group-item"><i class="fas fa-certificate text-success"></i> Entrance Exam Scorecards</li>
                                <li class="list-group-item"><i class="fas fa-id-card text-info"></i> Caste Certificates</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item"><i class="fas fa-address-card text-warning"></i> Aadhar Cards</li>
                                <li class="list-group-item"><i class="fas fa-file-alt text-secondary"></i> Transfer Certificates</li>
                                <li class="list-group-item"><i class="fas fa-camera text-dark"></i> Passport Photos</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div id="results"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const processBtn = document.getElementById('processBtn');
        const fileList = document.getElementById('fileList');
        const results = document.getElementById('results');
        let selectedFiles = [];

        // File input change handler
        fileInput.addEventListener('change', handleFileSelect);

        // Drag and drop handlers
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('drop', handleFileDrop);
        uploadArea.addEventListener('click', () => fileInput.click());

        function handleFileSelect(e) {
            selectedFiles = Array.from(e.target.files);
            displayFileList();
        }

        function handleDragOver(e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#e3f2fd';
        }

        function handleFileDrop(e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#f8f9fa';
            selectedFiles = Array.from(e.dataTransfer.files);
            displayFileList();
        }

        function displayFileList() {
            fileList.innerHTML = '';
            if (selectedFiles.length > 0) {
                const listHtml = selectedFiles.map((file, index) => `
                    <div class="d-flex justify-content-between align-items-center p-2 border rounded mb-2">
                        <div>
                            <i class="fas fa-file"></i> ${file.name} 
                            <small class="text-muted">(${(file.size / 1024).toFixed(1)} KB)</small>
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `).join('');
                fileList.innerHTML = listHtml;
                processBtn.disabled = false;
            } else {
                processBtn.disabled = true;
            }
        }

        function removeFile(index) {
            selectedFiles.splice(index, 1);
            displayFileList();
        }

        // Form submission
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (selectedFiles.length === 0) {
                alert('Please select at least one file.');
                return;
            }

            processBtn.disabled = true;
            processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

            try {
                for (const file of selectedFiles) {
                    await processFile(file);
                }
            } catch (error) {
                console.error('Processing error:', error);
                showError('Processing failed: ' + error.message);
            } finally {
                processBtn.disabled = false;
                processBtn.innerHTML = '<i class="fas fa-cogs"></i> Process Documents';
            }
        });

        async function processFile(file) {
            // Upload file
            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error('Upload failed');
            }

            const uploadData = await uploadResponse.json();
            const documentUpload = uploadData.data;

            // Process file
            const processFormData = new FormData();
            processFormData.append('file_path', documentUpload.file_path);
            processFormData.append('file_name', documentUpload.file_name);
            processFormData.append('file_size', documentUpload.file_size);
            processFormData.append('mime_type', documentUpload.mime_type);

            const processResponse = await fetch('/api/process', {
                method: 'POST',
                body: processFormData
            });

            if (!processResponse.ok) {
                throw new Error('Processing failed');
            }

            const processData = await processResponse.json();
            displayResult(processData.data.result);
        }

        function displayResult(result) {
            const resultHtml = `
                <div class="card result-card ${result.status === 'completed' ? '' : result.status === 'processing' ? 'processing' : 'error'}">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-file"></i> ${result.document_upload.file_name}
                            <span class="badge badge-${result.status === 'completed' ? 'success' : result.status === 'processing' ? 'warning' : 'danger'}">${result.status}</span>
                        </h6>
                        ${result.status === 'completed' && result.structured_data ? `
                            <div class="mt-3">
                                <h6>Extracted Data:</h6>
                                <pre class="bg-light p-3 rounded"><code>${JSON.stringify(result.structured_data, null, 2)}</code></pre>
                            </div>
                        ` : ''}
                        ${result.error_message ? `
                            <div class="alert alert-danger mt-3">
                                <strong>Error:</strong> ${result.error_message}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            results.innerHTML = resultHtml + results.innerHTML;
        }

        function showError(message) {
            const errorHtml = `
                <div class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            results.innerHTML = errorHtml + results.innerHTML;
        }
    </script>
</body>
</html>'''
    
    with open(templates_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

if __name__ == "__main__":
    print("Starting OCR Automation Pipeline Web App...")
    print("Open http://localhost:8000 in your browser")
    print("API Documentation: http://localhost:8000/api/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )