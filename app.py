"""
FastAPI Application for Document Processing
Modern async API with automatic documentation and MongoDB integration
"""

import os
import tempfile
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Union, List
import uvicorn
import requests

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
        # Initialize document processor with configured model
        processor = create_processor(model_name=settings.gemini_model)
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

def sanitize_error_for_frontend(error_message: str, extracted_data: dict = None) -> str:
    """
    Sanitize error messages for frontend display, hiding API quota details
    """
    if not error_message:
        return "Processing completed"
    
    error_lower = error_message.lower()
    
    # Check if this is a quota/API limit error
    if any(keyword in error_lower for keyword in ['quota', '429', 'rate limit', 'api limit', 'billing']):
        # Check if we have any extracted data (fallback worked)
        if extracted_data and any(value for value in extracted_data.values() if value and value != "Unable to extract due to API quota limits"):
            return "Document processed with basic extraction"
        else:
            return "Document processing temporarily unavailable. Please try again in a moment."
    
    # Check for model availability errors
    if any(keyword in error_lower for keyword in ['model', 'not found', 'api version', 'v1beta', 'generatecontent']):
        # Check if we have any extracted data (fallback worked)
        if extracted_data and any(value for value in extracted_data.values() if value):
            return "Document processed successfully using backup system"
        else:
            return "Document processing temporarily unavailable due to service updates. Please try again."
    
    # Check for other common API errors to hide
    if any(keyword in error_lower for keyword in ['api key', 'authentication', 'unauthorized']):
        return "Service temporarily unavailable. Please contact support."
    
    # For other errors, return a generic message
    if 'failed' in error_lower or 'error' in error_lower:
        return "Processing encountered an issue. Please try again or contact support."
    
    # If no concerning keywords, return the original message
    return error_message

# Legacy response models (keeping for backward compatibility)
class ProcessingResponse(BaseModel):
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    processing_time: float
    validation_issues: list[str]
    confidence_score: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentSchema(BaseModel):
    description: str
    required_fields: list[str]
    optional_fields: list[str]
    validation_rules: Dict[str, str]

def create_user_friendly_response(result, mongodb_stored: bool = False, student_id: str = None) -> ProcessingResponse:
    """
    Create a user-friendly response that hides technical API details
    """
    # Sanitize the error message
    sanitized_error = sanitize_error_for_frontend(result.error_message, result.extracted_data)
    
    # Check if we have any useful extracted data despite errors
    has_useful_data = (
        result.extracted_data and 
        len([v for v in result.extracted_data.values() if v and v != "Unable to extract due to API quota limits"]) > 0
    )
    
    # Determine success status - if we have useful data, consider it successful
    response_success = result.success or has_useful_data
    
    # Clean extracted data for frontend
    cleaned_data = {}
    if result.extracted_data:
        for key, value in result.extracted_data.items():
            # Hide technical metadata fields
            if key.startswith('_'):
                continue
            # Replace quota error messages with user-friendly text
            if isinstance(value, str) and "quota limits" in value:
                cleaned_data[key] = "Data extraction in progress..."
            else:
                cleaned_data[key] = value
    
    # Create response with sanitized data
    response = ProcessingResponse(
        success=response_success,
        document_type=result.document_type,
        extracted_data=cleaned_data,
        processing_time=result.processing_time,
        validation_issues=result.validation_issues,
        confidence_score=max(0.5, result.confidence_score) if has_useful_data else result.confidence_score,
        error_message=sanitized_error if not response_success else None,
        metadata=result.metadata or {}
    )
    
    # Add MongoDB storage status to metadata
    response.metadata['mongodb_stored'] = mongodb_stored
    if student_id:
        response.metadata['student_id'] = student_id
    
    return response

# Helper functions for error sanitization
def create_user_friendly_response(result, mongodb_stored: bool = False, student_id: str = None) -> ProcessingResponse:
    """
    Create a user-friendly response that hides technical API details
    """
    # Sanitize the error message
    sanitized_error = sanitize_error_for_frontend(result.error_message, result.extracted_data)
    
    # Check if we have any useful extracted data despite errors
    has_useful_data = (
        result.extracted_data and 
        len([v for v in result.extracted_data.values() if v and v != "Unable to extract due to API quota limits"]) > 0
    )
    
    # Determine success status - if we have useful data, consider it successful
    response_success = result.success or has_useful_data
    
    # Clean extracted data for frontend
    cleaned_data = {}
    if result.extracted_data:
        for key, value in result.extracted_data.items():
            # Hide technical metadata fields
            if key.startswith('_'):
                continue
            # Replace quota error messages with user-friendly text
            if isinstance(value, str) and "quota limits" in value:
                cleaned_data[key] = "Data extraction in progress..."
            else:
                cleaned_data[key] = value
    
    # Create response with sanitized data
    response = ProcessingResponse(
        success=response_success,
        document_type=result.document_type,
        extracted_data=cleaned_data,
        processing_time=result.processing_time,
        validation_issues=result.validation_issues,
        confidence_score=max(0.5, result.confidence_score) if has_useful_data else result.confidence_score,
        error_message=sanitized_error if not response_success else None,
        metadata=result.metadata or {}
    )
    
    # Add MongoDB storage status to metadata
    response.metadata['mongodb_stored'] = mongodb_stored
    if student_id:
        response.metadata['student_id'] = student_id
    
    return response

# New models for URI/document processing
class DocumentProcessingRequest(BaseModel):
    """Request model for processing documents from URIs or direct upload"""
    document_uris: Optional[List[str]] = Field(None, description="List of document URIs to download and process")
    document_type: Optional[str] = Field(None, description="Document type hint (optional)")
    student_id: Optional[str] = Field(None, description="Student ID for MongoDB storage (optional)")
    batch_name: Optional[str] = Field(None, description="Batch identifier for grouping documents")
    callback_url: Optional[str] = Field(None, description="URL to send results to when processing is complete")

# Models for fetching documents from MongoDB collections
class MongoDBFetchRequest(BaseModel):
    """Request model for fetching documents from MongoDB and processing them"""
    collection_name: str = Field(..., description="MongoDB collection name containing document URIs")
    filter_criteria: Optional[Dict[str, Any]] = Field(None, description="MongoDB query filter (e.g., {'student_id': 'STUDENT_123'})")
    uri_field_name: str = Field("cloudinary_url", description="Field name containing the Cloudinary URI")
    document_type_field: Optional[str] = Field("document_type", description="Field name containing document type")
    student_id_field: Optional[str] = Field("student_id", description="Field name containing student ID")
    batch_size: int = Field(10, description="Maximum documents to process in one batch")
    callback_url: Optional[str] = Field(None, description="URL to send results when processing is complete")
    additional_fields: Optional[List[str]] = Field(None, description="Additional fields to include in processing metadata")

class MongoDBDocument(BaseModel):
    """Model representing a document fetched from MongoDB"""
    document_id: str
    cloudinary_url: str
    document_type: Optional[str] = None
    student_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

class DocumentProcessingResult(BaseModel):
    """Result for a single document processing"""
    uri: Optional[str] = None
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    processing_time: float
    validation_issues: List[str]
    confidence_score: float
    error_message: Optional[str] = None
    mongodb_stored: bool = False

class MongoDBFetchResponse(BaseModel):
    """Response for MongoDB fetch and process operation"""
    success: bool
    total_documents_found: int
    documents_processed: int
    documents_failed: int
    collection_name: str
    filter_applied: Optional[Dict[str, Any]]
    processing_results: List[DocumentProcessingResult]
    total_processing_time: float
    message: str

class BatchProcessingResponse(BaseModel):
    """Response for batch document processing"""
    success: bool
    batch_name: Optional[str]
    student_id: Optional[str] = None
    total_documents: int
    processed_documents: int
    failed_documents: int
    results: List[DocumentProcessingResult]
    total_processing_time: float
    message: str

class DocumentProcessingResult(BaseModel):
    """Result for a single document processing"""
    uri: Optional[str] = None
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    processing_time: float
    validation_issues: List[str]
    confidence_score: float
    error_message: Optional[str] = None
    mongodb_stored: bool = False

class BatchProcessingResponse(BaseModel):
    """Response for batch document processing"""
    success: bool
    batch_name: Optional[str]
    total_documents: int
    processed_documents: int
    failed_documents: int
    results: List[DocumentProcessingResult]
    total_processing_time: float
    message: str

# Service registration models
class ServiceRegistration(BaseModel):
    """Model for external service registration"""
    service_name: str
    service_type: str = "spring_boot"
    base_url: str
    callback_endpoint: Optional[str] = None
    health_endpoint: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None

class RegisteredService(BaseModel):
    """Model for registered service info"""
    id: str
    service_name: str
    service_type: str
    base_url: str
    callback_endpoint: Optional[str]
    health_endpoint: Optional[str]
    registered_at: str
    last_health_check: Optional[str] = None
    status: str = "active"

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Document Processor</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; 
                color: #333; 
                padding: 20px;
                margin: 0;
            }
            
            .container { 
                max-width: 1000px; 
                margin: 0 auto; 
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px; 
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                overflow: hidden;
                backdrop-filter: blur(10px);
            }
            
            .header { 
                background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
                color: white; 
                padding: 40px;
                text-align: center;
            }
            
            .header h1 { 
                font-size: 2.8em; 
                font-weight: 700; 
                margin-bottom: 15px;
                letter-spacing: -1px;
            }
            
            .header p { 
                opacity: 0.9; 
                font-size: 1.2em;
                font-weight: 300;
            }
            
            .content { 
                padding: 40px;
            }
            
            .upload-section { 
                background: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 15px; 
                padding: 40px; 
                margin-bottom: 30px;
                transition: all 0.3s ease;
            }
            
            .upload-section:hover { 
                border-color: #4CAF50;
                background: #f1f8f4;
            }
            
            .form-group { margin-bottom: 25px; }
            
            label { 
                display: block; 
                margin-bottom: 10px; 
                font-weight: 600; 
                color: #555;
                font-size: 14px;
            }
            
            small { 
                display: block; 
                margin-top: 8px; 
                color: #666; 
                font-size: 12px;
            }
            
            input[type="file"], select { 
                width: 100%; 
                padding: 15px; 
                border: 2px solid #e1e5e9;
                border-radius: 10px;
                font-size: 16px;
                background: white;
                transition: all 0.3s;
            }
            
            input[type="file"]:focus, select:focus { 
                border-color: #4CAF50;
                outline: none;
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
            }
            
            .btn { 
                background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
                color: white; 
                padding: 18px 40px; 
                border: none; 
                border-radius: 12px; 
                font-size: 16px;
                cursor: pointer; 
                transition: all 0.3s ease; 
                font-weight: 600; 
                width: 100%;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            }
            
            .btn:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
            }
            
            .btn:disabled { 
                opacity: 0.6; 
                cursor: not-allowed; 
                transform: none;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
            }
            
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
            
            .loading { 
                text-align: center; 
                padding: 30px;
                color: #666;
                font-size: 16px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 10px;
                margin: 20px 0;
            }
            
            /* Modern Progress Bar */
            .progress-container {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border: 1px solid #e9ecef;
                padding: 35px;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                margin: 30px 0;
                color: #333;
            }
            
            .progress-header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .progress-title {
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 8px;
                color: #2E7D32;
            }
            
            .progress-subtitle {
                font-size: 14px;
                color: #666;
                font-weight: 400;
            }
            
            .progress-stages {
                display: flex;
                justify-content: space-between;
                margin-bottom: 25px;
                position: relative;
            }
            
            .progress-stages::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 10%;
                right: 10%;
                height: 2px;
                background: #e9ecef;
                z-index: 1;
            }
            
            .progress-stage {
                display: flex;
                flex-direction: column;
                align-items: center;
                z-index: 2;
                background: white;
                padding: 16px 12px;
                border-radius: 12px;
                min-width: 100px;
                transition: all 0.3s ease;
                border: 2px solid #e9ecef;
            }
            
            .progress-stage.active {
                background: #e8f5e9;
                border-color: #4CAF50;
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(76, 175, 80, 0.2);
            }
            
            .progress-stage.completed {
                background: #e8f5e9;
                border-color: #4CAF50;
            }
            
            .stage-icon {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                margin-bottom: 8px;
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                transition: all 0.3s ease;
                color: #666;
            }
            
            .progress-stage.active .stage-icon {
                background: #4CAF50;
                border-color: #4CAF50;
                color: white;
                animation: pulse-gentle 2s ease-in-out infinite;
            }
            
            .progress-stage.completed .stage-icon {
                background: #4CAF50;
                border-color: #4CAF50;
                color: white;
            }
            
            .stage-label {
                font-size: 12px;
                text-align: center;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .progress-stage.active .stage-label,
            .progress-stage.completed .stage-label {
                color: #4CAF50;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
                margin: 20px 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #66BB6A);
                border-radius: 4px;
                transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
            }
            
            .progress-fill::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                bottom: 0;
                right: 0;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                animation: shine 2s ease-in-out infinite;
            }
            
            .progress-text {
                text-align: center;
                font-size: 14px;
                font-weight: 500;
                margin-top: 12px;
                color: #555;
            }
            
            @keyframes pulse-gentle {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            @keyframes shine {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
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
                <p>AI-powered document extraction using Local AI</p>
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
                    <h4> API Documentation</h4>
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
                
                // Show progressive loading
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                resultDiv.style.display = 'block';
                
                // Initialize progress bar
                const progressContainer = `
                    <div class="progress-container">
                        <div class="progress-header">
                            <div class="progress-title">Processing Document</div>
                            <div class="progress-subtitle">AI-powered extraction in progress</div>
                        </div>
                        
                        <div class="progress-stages">
                            <div class="progress-stage" id="stage-upload">
                                <div class="stage-icon">📄</div>
                                <div class="stage-label">Upload</div>
                            </div>
                            <div class="progress-stage" id="stage-analysis">
                                <div class="stage-icon">🔍</div>
                                <div class="stage-label">Analyze</div>
                            </div>
                            <div class="progress-stage" id="stage-extraction">
                                <div class="stage-icon">🧠</div>
                                <div class="stage-label">Extract</div>
                            </div>
                            <div class="progress-stage" id="stage-validation">
                                <div class="stage-icon">✓</div>
                                <div class="stage-label">Validate</div>
                            </div>
                            <div class="progress-stage" id="stage-storage">
                                <div class="stage-icon">💾</div>
                                <div class="stage-label">Store</div>
                            </div>
                        </div>
                        
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                        </div>
                        
                        <div class="progress-text" id="progress-text">Initializing...</div>
                    </div>
                `;
                
                resultDiv.innerHTML = progressContainer;
                
                // Progress simulation function
                const updateProgress = (stage, percentage, text) => {
                    // Update progress bar
                    document.getElementById('progress-fill').style.width = percentage + '%';
                    document.getElementById('progress-text').textContent = text;
                    
                    // Update stage indicators
                    const stages = ['upload', 'analysis', 'extraction', 'validation', 'storage'];
                    const currentIndex = stages.indexOf(stage);
                    
                    stages.forEach((stageName, index) => {
                        const stageElement = document.getElementById('stage-' + stageName);
                        stageElement.classList.remove('active', 'completed');
                        
                        if (index < currentIndex) {
                            stageElement.classList.add('completed');
                        } else if (index === currentIndex) {
                            stageElement.classList.add('active');
                        }
                    });
                };
                
                // Start progress with clean messages
                updateProgress('upload', 15, 'Uploading document...');
                
                setTimeout(() => updateProgress('analysis', 35, 'Analyzing document structure...'), 500);
                setTimeout(() => updateProgress('extraction', 70, 'Extracting data with AI model...'), 1200);
                setTimeout(() => updateProgress('validation', 90, 'Validating extracted data...'), 2200);
                
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
                        // Complete progress with success message
                        updateProgress('storage', 100, 'Processing completed successfully!');
                        
                        // Wait a moment to show completion, then show results
                        setTimeout(() => {
                            resultDiv.className = 'result';
                            
                            // Check if data was stored in MongoDB
                            const mongoStored = result.metadata?.mongodb_stored;
                            const studentId = result.metadata?.student_id;
                            
                            if (mongoStored) {
                                showToast(`✅ Document processed and saved to database for student: ${studentId}`, 'success');
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
                                        <div class="metric-value">${mongoStored ? 'Saved' : '❌ Not Saved'}</div>
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
                        }, 1000); // Wait 1 second to show completion before results
                    } else {
                        // Update progress to show processing issue
                        updateProgress('extraction', 60, 'Processing encountered an issue...');
                        
                        setTimeout(() => {
                            resultDiv.className = 'result error';
                            resultDiv.innerHTML = `
                                <h3>⏳ Processing Issue</h3>
                                <p><strong>Status:</strong> ${result.error_message || 'Processing temporarily unavailable'}</p>
                                <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
                                    <small><strong>💡 Tip:</strong> Please try again in a moment. The system is optimizing performance.</small>
                                </div>
                            `;
                        }, 1000);
                    }
                } catch (error) {
                    // Update progress to show connection error
                    updateProgress('analysis', 20, 'Connection issue detected...');
                    
                    setTimeout(() => {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `
                            <h3>⏳ Connection Issue</h3>
                            <p><strong>Status:</strong> Unable to connect to processing service</p>
                            <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
                                <small><strong>💡 Solution:</strong> Please check your connection and try again.</small>
                            </div>
                        `;
                    }, 1000);
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
        gemini_configured=bool(processor)  # Check if processor is available instead
    )

@app.get("/api/ping")
async def ping():
    """Simple ping endpoint for Spring Boot server connectivity test"""
    return {
        "status": "SUCCESS",
        "message": "Python server is responding",
        "timestamp": datetime.utcnow().isoformat(),
        "server": "document-processor-python"
    }

@app.get("/api/test-cloudinary/{public_id}")
async def test_cloudinary_url(public_id: str):
    """Test different Cloudinary URL formats to find one that works"""
    import requests
    
    base_url = f"https://res.cloudinary.com/dal5z9kro/image/upload/{public_id}"
    
    url_variants = [
        base_url,
        f"https://res.cloudinary.com/dal5z9kro/image/upload/q_auto/{public_id}",
        f"https://res.cloudinary.com/dal5z9kro/image/upload/f_auto/{public_id}",
        f"https://res.cloudinary.com/dal5z9kro/image/upload/q_auto,f_auto/{public_id}",
        f"https://res.cloudinary.com/dal5z9kro/image/upload/w_auto/{public_id}",
        f"https://res.cloudinary.com/dal5z9kro/image/upload/c_auto/{public_id}",
    ]
    
    results = []
    
    for i, url in enumerate(url_variants):
        try:
            response = requests.head(url, timeout=10)
            results.append({
                "variant": i + 1,
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', 'unknown'),
                "content_length": response.headers.get('content-length', 'unknown'),
                "success": response.status_code == 200
            })
            response.close()
        except Exception as e:
            results.append({
                "variant": i + 1,
                "url": url,
                "status_code": "error",
                "error": str(e),
                "success": False
            })
    
    return {
        "public_id": public_id,
        "test_results": results,
        "working_urls": [r for r in results if r["success"]]
    }

@app.get("/service-info")
async def get_service_info():
    """
    Service information endpoint for Spring Boot server discovery
    Returns the configuration and endpoints that Spring Boot needs to communicate
    """
    import socket
    
    # Get local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Get server port (default 8000)
    server_port = os.getenv("SERVER_PORT", "8000")
    
    service_info = {
        "service_name": "OCR Document Processor",
        "service_type": "document_processing",
        "version": "2.0.0",
        "status": "running",
        "host_info": {
            "hostname": hostname,
            "local_ip": local_ip,
            "port": server_port,
            "base_url": f"http://{local_ip}:{server_port}",
            "public_url": f"http://localhost:{server_port}"  # For same-machine testing
        },
        "endpoints": {
            "health_check": f"http://{local_ip}:{server_port}/health",
            "service_info": f"http://{local_ip}:{server_port}/service-info",
            "single_document_processing": f"http://{local_ip}:{server_port}/api/process",
            "batch_document_processing": f"http://{local_ip}:{server_port}/api/process/documents",
            "mongodb_fetch_and_process": f"http://{local_ip}:{server_port}/api/fetch-and-process",
            "cloudinary_document_processing": f"http://{local_ip}:{server_port}/process-doc",
            "student_documents": f"http://{local_ip}:{server_port}/students/{{student_id}}/documents",
            "api_documentation": f"http://{local_ip}:{server_port}/docs"
        },
        "capabilities": {
            "supported_formats": ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"],
            "supported_document_types": [
                "aadhaar_card", "marksheet_10th", "marksheet_12th", "transfer_certificate",
                "migration_certificate", "entrance_scorecard", "admit_card", 
                "caste_certificate", "domicile_certificate", "passport_photo"
            ],
            "features": [
                "single_document_processing",
                "batch_processing",
                "uri_download",
                "mongodb_storage",
                "callback_webhooks",
                "auto_document_detection",
                "field_extraction",
                "validation",
                "confidence_scoring"
            ]
        },
        "integration_examples": {
            "spring_boot_service_call": {
                "description": "How Spring Boot should call this service",
                "method": "POST",
                "url": f"http://{local_ip}:{server_port}/api/process/documents",
                "headers": {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                "example_request_body": {
                    "document_uris": [
                        "https://your-file-server.com/documents/doc1.jpg"
                    ],
                    "student_id": "STUDENT_123",
                    "document_type": "aadhaar_card",
                    "batch_name": "admission_batch_1",
                    "callback_url": "http://your-spring-boot-server:8080/api/ocr/callback"
                }
            }
        }
    }
    
    return service_info

# In-memory storage for registered services (in production, use Redis or database)
registered_services = {}

@app.post("/register-service")
async def register_external_service(registration: ServiceRegistration):
    """
    Register an external service (like Spring Boot) with this FastAPI server
    This allows the FastAPI server to know about and communicate back to other services
    """
    import uuid
    from datetime import datetime
    
    # Generate unique service ID
    service_id = str(uuid.uuid4())[:8]
    
    # Create registered service record
    registered_service = RegisteredService(
        id=service_id,
        service_name=registration.service_name,
        service_type=registration.service_type,
        base_url=registration.base_url,
        callback_endpoint=registration.callback_endpoint,
        health_endpoint=registration.health_endpoint,
        registered_at=datetime.now().isoformat(),
        status="active"
    )
    
    # Store in memory (use database in production)
    registered_services[service_id] = registered_service
    
    logger.info(f"Registered new service: {registration.service_name} ({service_id}) at {registration.base_url}")
    
    # Get current service info for endpoints
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    server_port = os.getenv("SERVER_PORT", "8000")
    base_url = f"http://{local_ip}:{server_port}"
    
    return {
        "success": True,
        "message": f"Service {registration.service_name} registered successfully",
        "service_id": service_id,
        "registered_service": registered_service,
        "fastapi_endpoints": {
            "batch_processing": f"{base_url}/api/process/documents",
            "single_processing": f"{base_url}/api/process",
            "health_check": f"{base_url}/health",
            "service_info": f"{base_url}/service-info"
        }
    }

@app.get("/registered-services")
async def get_registered_services():
    """Get list of all registered external services"""
    return {
        "total_services": len(registered_services),
        "services": list(registered_services.values())
    }

@app.delete("/registered-services/{service_id}")
async def unregister_service(service_id: str):
    """Unregister a service"""
    if service_id in registered_services:
        service = registered_services.pop(service_id)
        logger.info(f"Unregistered service: {service.service_name} ({service_id})")
        return {"success": True, "message": f"Service {service.service_name} unregistered"}
    else:
        raise HTTPException(status_code=404, detail="Service not found")

@app.post("/notify-services")
async def notify_registered_services(message: Dict[str, Any]):
    """
    Send notifications to all registered services
    Useful for broadcasting system status, maintenance updates, etc.
    """
    results = []
    
    for service_id, service in registered_services.items():
        try:
            if service.callback_endpoint:
                notification_url = f"{service.base_url}{service.callback_endpoint}"
                
                import asyncio
                import concurrent.futures
                
                def send_notification():
                    response = requests.post(
                        notification_url,
                        json={
                            "from_service": "OCR Document Processor",
                            "message_type": "notification",
                            "timestamp": time.time(),
                            "data": message
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    return response.status_code
                
                # Send async
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    status_code = await loop.run_in_executor(executor, send_notification)
                
                results.append({
                    "service_id": service_id,
                    "service_name": service.service_name,
                    "success": status_code == 200,
                    "status_code": status_code
                })
                
        except Exception as e:
            results.append({
                "service_id": service_id,
                "service_name": service.service_name,
                "success": False,
                "error": str(e)
            })
    
    return {
        "message": "Notifications sent to registered services",
        "results": results
    }

# NEW MICROSERVICE ENDPOINTS

@app.post("/process-doc", response_model=ProcessDocumentResponse)
async def process_document_from_cloudinary(request: ProcessDocumentRequest):
    """
    Process a document from Cloudinary URL or local file path and store in MongoDB
    
    Main endpoint for the document processing microservice:
    1. Downloads image from Cloudinary URL OR uses local file path
    2. Processes with PI to extract structured data
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
        
        # Process document with AI
        result = await processor.process_document_async(temp_file_path, internal_doc_type)
        
        if not result.success:
            sanitized_error = sanitize_error_for_frontend(result.error_message, result.extracted_data)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Document processing failed: {sanitized_error}"
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

@app.put("/students/{student_id}/vtu-approval")
async def update_student_vtu_approval(student_id: str, request: Dict[str, Any]):
    """
    Update student documents with VTU approval status
    """
    try:
        logger.info(f"Updating VTU approval for student {student_id}")
        
        vtu_approved = request.get("vtuApproved", False)
        vtu_response = request.get("vtuResponse", {})
        approved_at = request.get("approvedAt", datetime.now().isoformat())
        
        # Find the student document
        student = await StudentDocument.find_one(StudentDocument.studentId == student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Update VTU approval status for all documents using MongoDB update
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        # Get MongoDB connection
        connection_string = os.getenv("MONGODB_URL", "mongodb+srv://photosvvce_db_user:7wo5MumT2Pmih2Rk@cluster0.ujzukh7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db_name = os.getenv("DATABASE_NAME", "admission_automation")
        
        client = AsyncIOMotorClient(connection_string)
        db = client[db_name]
        collection = db["students"]
        
        # Update student approval status from false to true
        update_result = await collection.update_one(
            {"studentId": student_id},
            {
                "$set": {
                    "documents.$[].vtuApproved": vtu_approved,
                    "documents.$[].vtuResponse": vtu_response,
                    "documents.$[].vtuApprovedAt": approved_at,
                    "documents.$[].updatedAt": datetime.now(),
                    "approved": vtu_approved,  # Update approved field from false to true
                    "updatedAt": datetime.now()
                }
            }
        )
        
        logger.info(f"MongoDB update result: {update_result.modified_count} documents modified")
        
        # Also update the student object for consistency
        student.updatedAt = datetime.now()
        await student.save()
        
        logger.info(f"Successfully updated VTU approval for student {student_id}: {vtu_approved}")
        
        return {
            "success": True,
            "message": f"Student {student_id} VTU approval status updated successfully",
            "studentId": student_id,
            "vtuApproved": vtu_approved,
            "updatedDocumentsCount": len(student.documents),
            "approvedAt": approved_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating VTU approval for student {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update VTU approval: {str(e)}"
        )

@app.get("/students/{student_id}/status")
async def get_student_status(student_id: str):
    """
    Get student status including VTU approval information
    """
    try:
        logger.info(f"Getting status for student {student_id}")
        
        # Find the student document
        student = await StudentDocument.find_one(StudentDocument.studentId == student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Check VTU approval status
        is_approved = student.approved
        total_documents = len(student.documents)
        
        return {
            "studentId": student_id,
            "totalDocuments": total_documents,
            "isApproved": is_approved,
            "approved": is_approved,
            "documents": [
                {
                    "docType": doc.docType,
                    "vtuApproved": getattr(doc, 'vtuApproved', None),
                    "vtuApprovedAt": getattr(doc, 'vtuApprovedAt', None),
                    "hasVtuResponse": hasattr(doc, 'vtuResponse') and doc.vtuResponse is not None
                }
                for doc in student.documents
            ],
            "createdAt": student.createdAt,
            "updatedAt": student.updatedAt
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student status for {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student status: {str(e)}"
        )

@app.get("/approved-students")
async def get_approved_students():
    """
    Get all students with VTU approval status
    """
    try:
        logger.info("Fetching all approved students")
        
        # Find all students with VTU approved documents
        students = await StudentDocument.find_all().to_list()
        approved_students = []
        
        for student in students:
            # Check if student is approved (approved field is true)
            if student.approved:
                # Extract student information from documents
                student_info = {
                    "studentId": student.studentId,
                    "name": "Unknown",  # Will be extracted from documents
                    "branch": "CSE",    # Default branch
                    "gender": "Unknown", # Will be extracted from documents
                    "status": "Approved",
                    "admissionDate": student.createdAt.isoformat() if student.createdAt else None,
                    "documents": []
                }
                
                # Extract name and gender from documents
                for doc in student.documents:
                    if hasattr(doc, 'vtuApproved') and doc.vtuApproved:
                        # Extract name from fields
                        if 'fields' in doc.__dict__ and doc.fields:
                            if 'Name' in doc.fields:
                                student_info["name"] = doc.fields['Name']
                            elif 'name' in doc.fields:
                                student_info["name"] = doc.fields['name']
                            
                            # Extract gender (if available in fields)
                            if 'Gender' in doc.fields:
                                student_info["gender"] = doc.fields['Gender']
                            elif 'gender' in doc.fields:
                                student_info["gender"] = doc.fields['gender']
                        
                        # Add document info
                        doc_info = {
                            "docType": doc.docType,
                            "vtuApproved": getattr(doc, 'vtuApproved', False),
                            "vtuApprovedAt": getattr(doc, 'vtuApprovedAt', None),
                            "confidence": doc.confidence
                        }
                        student_info["documents"].append(doc_info)
                
                approved_students.append(student_info)
        
        logger.info(f"Found {len(approved_students)} approved students")
        
        return {
            "success": True,
            "message": f"Found {len(approved_students)} approved students",
            "students": approved_students,
            "totalCount": len(approved_students)
        }
        
    except Exception as e:
        logger.error(f"Error fetching approved students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch approved students: {str(e)}"
        )

@app.get("/approved-students/{student_id}")
async def get_approved_student_by_id(student_id: str):
    """
    Get specific approved student by ID
    """
    try:
        logger.info(f"Fetching approved student: {student_id}")
        
        # Find the student document
        student = await StudentDocument.find_one(StudentDocument.studentId == student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        # Check if student is approved (approved field is true)
        if not student.approved:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} is not approved by VTU"
            )
        
        # Extract student information
        student_info = {
            "studentId": student.studentId,
            "name": "Unknown",
            "branch": "CSE",
            "gender": "Unknown",
            "status": "Approved",
            "admissionDate": student.createdAt.isoformat() if student.createdAt else None,
            "documents": []
        }
        
        # Extract name and gender from documents
        for doc in student.documents:
            if hasattr(doc, 'vtuApproved') and doc.vtuApproved:
                # Extract name from fields
                if 'fields' in doc.__dict__ and doc.fields:
                    if 'Name' in doc.fields:
                        student_info["name"] = doc.fields['Name']
                    elif 'name' in doc.fields:
                        student_info["name"] = doc.fields['name']
                    
                    # Extract gender (if available in fields)
                    if 'Gender' in doc.fields:
                        student_info["gender"] = doc.fields['Gender']
                    elif 'gender' in doc.fields:
                        student_info["gender"] = doc.fields['gender']
                
                # Add document info
                doc_info = {
                    "docType": doc.docType,
                    "vtuApproved": getattr(doc, 'vtuApproved', False),
                    "vtuApprovedAt": getattr(doc, 'vtuApprovedAt', None),
                    "confidence": doc.confidence,
                    "fields": doc.fields
                }
                student_info["documents"].append(doc_info)
        
        return {
            "success": True,
            "message": f"Approved student {student_id} found",
            "student": student_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching approved student {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch approved student: {str(e)}"
        )

@app.get("/test-approved-field/{student_id}")
async def test_approved_field(student_id: str):
    """
    Test endpoint to check if approved field is set correctly
    """
    try:
        logger.info(f"Testing approved field for student: {student_id}")
        
        # Find the student document
        student = await StudentDocument.find_one(StudentDocument.studentId == student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student {student_id} not found"
            )
        
        return {
            "studentId": student_id,
            "approved": student.approved,
            "updatedAt": student.updatedAt,
            "message": f"Student {student_id} approved status: {student.approved}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing approved field for student {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test approved field: {str(e)}"
        )

@app.get("/all-students-status")
async def get_all_students_status():
    """
    Get all students and their approval status for testing
    """
    try:
        logger.info("Fetching all students status")
        
        # Find all students
        students = await StudentDocument.find_all().to_list()
        
        students_status = []
        for student in students:
            students_status.append({
                "studentId": student.studentId,
                "approved": student.approved,
                "documentsCount": len(student.documents),
                "createdAt": student.createdAt.isoformat() if student.createdAt else None,
                "updatedAt": student.updatedAt.isoformat() if student.updatedAt else None
            })
        
        return {
            "success": True,
            "message": f"Found {len(students_status)} students",
            "students": students_status,
            "totalCount": len(students_status)
        }
        
    except Exception as e:
        logger.error(f"Error fetching all students status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch students status: {str(e)}"
        )

@app.post("/migrate-approval-fields")
async def migrate_approval_fields():
    """
    Migrate existing students to add approved field if missing
    """
    try:
        logger.info("Starting migration of approval fields")
        
        # Get MongoDB connection
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        connection_string = os.getenv("MONGODB_URL", "mongodb+srv://photosvvce_db_user:7wo5MumT2Pmih2Rk@cluster0.ujzukh7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db_name = os.getenv("DATABASE_NAME", "admission_automation")
        
        client = AsyncIOMotorClient(connection_string)
        db = client[db_name]
        collection = db["students"]
        
        # Find all students that don't have the approved field
        students_without_approved = await collection.find({"approved": {"$exists": False}}).to_list(length=None)
        
        logger.info(f"Found {len(students_without_approved)} students without approved field")
        
        # Update all students to add approved: false
        update_result = await collection.update_many(
            {"approved": {"$exists": False}},
            {"$set": {"approved": False}}
        )
        
        logger.info(f"Migration completed: {update_result.modified_count} students updated")
        
        return {
            "success": True,
            "message": f"Migration completed: {update_result.modified_count} students updated with approved: false",
            "studentsFound": len(students_without_approved),
            "studentsUpdated": update_result.modified_count
        }
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )

@app.get("/debug-student-creation/{student_id}")
async def debug_student_creation(student_id: str):
    """
    Debug endpoint to test student creation with approved field
    """
    try:
        logger.info(f"Testing student creation for: {student_id}")
        
        # Test the find_or_create_student method
        student = await StudentDocument.find_or_create_student(student_id)
        
        return {
            "studentId": student.studentId,
            "approved": student.approved,
            "hasApprovedField": hasattr(student, 'approved'),
            "documentsCount": len(student.documents),
            "createdAt": student.createdAt.isoformat() if student.createdAt else None,
            "updatedAt": student.updatedAt.isoformat() if student.updatedAt else None,
            "message": f"Student {student_id} created/retrieved successfully with approved={student.approved}"
        }
        
    except Exception as e:
        logger.error(f"Error in debug student creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}"
        )

@app.get("/check-student-structure/{student_id}")
async def check_student_structure(student_id: str):
    """
    Check the exact structure of a student document in MongoDB
    """
    try:
        logger.info(f"Checking student structure for: {student_id}")
        
        # Get MongoDB connection
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        connection_string = os.getenv("MONGODB_URL", "mongodb+srv://photosvvce_db_user:7wo5MumT2Pmih2Rk@cluster0.ujzukh7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db_name = os.getenv("DATABASE_NAME", "admission_automation")
        
        client = AsyncIOMotorClient(connection_string)
        db = client[db_name]
        collection = db["students"]
        
        # Find the student document directly from MongoDB
        student_doc = await collection.find_one({"studentId": student_id})
        
        if not student_doc:
            return {
                "studentId": student_id,
                "found": False,
                "message": f"Student {student_id} not found in MongoDB"
            }
        
        # Check if approved field exists
        has_approved = "approved" in student_doc
        approved_value = student_doc.get("approved", "NOT_SET")
        
        return {
            "studentId": student_id,
            "found": True,
            "hasApprovedField": has_approved,
            "approvedValue": approved_value,
            "allFields": list(student_doc.keys()),
            "documentCount": len(student_doc.get("documents", [])),
            "rawDocument": student_doc
        }
        
    except Exception as e:
        logger.error(f"Error checking student structure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check failed: {str(e)}"
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
            response = create_user_friendly_response(result, mongodb_stored, student_id)
                
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
        "message": "Batch processing available via /api/process/documents endpoint",
        "suggested_approach": "Use /api/process/documents for processing multiple documents from URIs",
        "rate_limits": "Optimized for high throughput processing"
    }

@app.post("/api/process/documents", response_model=BatchProcessingResponse)
async def process_documents_from_uris(request: DocumentProcessingRequest):
    """
    Process multiple documents from URIs and extract structured data
    
    This endpoint allows you to:
    - Submit multiple document URIs for batch processing
    - Specify document types for better accuracy 
    - Store results in MongoDB with student ID
    - Get results via callback URL (optional)
    
    **Example request:**
    ```json
    {
        "document_uris": [
            "https://example.com/document1.jpg",
            "https://example.com/document2.pdf"
        ],
        "document_type": "aadhaar_card",
        "student_id": "STUDENT_123",
        "batch_name": "admission_docs_batch_1"
    }
    ```
    
    Returns processing results for all documents
    """
    if not processor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document processor not available"
        )
    
    if not request.document_uris or len(request.document_uris) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one document URI must be provided"
        )
    
    # Validate document type
    if request.document_type and request.document_type not in get_supported_types() + ['other']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported document type: {request.document_type}"
        )
    
    start_time = time.time()
    results = []
    processed_count = 0
    failed_count = 0
    
    logger.info(f"Starting batch processing of {len(request.document_uris)} documents")
    
    # Process each URI
    for uri in request.document_uris:
        try:
            logger.info(f"Processing document from URI: {uri}")
            
            # Download document from URI
            temp_file_path = await download_document_from_uri(uri)
            
            if not temp_file_path:
                result = DocumentProcessingResult(
                    uri=uri,
                    success=False,
                    document_type="unknown",
                    extracted_data={},
                    processing_time=0.0,
                    validation_issues=["Failed to download document from URI"],
                    confidence_score=0.0,
                    error_message=f"Could not download document from {uri}",
                    mongodb_stored=False
                )
                results.append(result)
                failed_count += 1
                continue
            
            try:
                # Process the downloaded document
                processing_result = await processor.process_document_async(temp_file_path, request.document_type)
                
                # Store in MongoDB if student_id is provided
                mongodb_stored = False
                if request.student_id and processing_result.success:
                    try:
                        # Use document type from result if available, fallback to provided or 'other'
                        detected_doc_type = processing_result.document_type if processing_result.document_type != 'unknown' else request.document_type or 'other'
                        
                        # Normalize extracted fields
                        normalized_fields = normalize_fields(processing_result.extracted_data, detected_doc_type)
                        
                        # Create document entry for database
                        doc_entry = DocumentEntry(
                            docType=detected_doc_type,
                            cloudinaryUrl=uri,  # Store the URI as cloudinary URL
                            documentPath=None,
                            fields=normalized_fields,
                            confidence=processing_result.confidence_score,
                            validationIssues=processing_result.validation_issues
                        )
                        
                        # Find or create student record
                        student = await StudentDocument.find_or_create_student(request.student_id)
                        
                        # Ensure approved field is set to false in the student object
                        student.approved = False
                        await student.save()
                        
                        # Add document to student record
                        await student.add_document(doc_entry)
                        
                        # Double-check with direct MongoDB update to ensure field exists
                        from motor.motor_asyncio import AsyncIOMotorClient
                        import os
                        
                        connection_string = os.getenv("MONGODB_URL", "mongodb+srv://photosvvce_db_user:7wo5MumT2Pmih2Rk@cluster0.ujzukh7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
                        db_name = os.getenv("DATABASE_NAME", "admission_automation")
                        
                        client = AsyncIOMotorClient(connection_string)
                        db = client[db_name]
                        collection = db["students"]
                        
                        # Ensure approved field is set to false (direct MongoDB update)
                        update_result = await collection.update_one(
                            {"studentId": request.student_id},
                            {"$set": {"approved": False}},
                            upsert=False
                        )
                        
                        # Verify the field was set
                        updated_student = await collection.find_one({"studentId": request.student_id})
                        approved_status = updated_student.get("approved", "NOT_SET") if updated_student else "STUDENT_NOT_FOUND"
                        
                        mongodb_stored = True
                        
                        logger.info(f"Document from {uri} stored in MongoDB for student {request.student_id}")
                        logger.info(f"Approved field status: {approved_status}, Update result: {update_result.modified_count} documents modified")
                        
                    except Exception as e:
                        logger.error(f"Failed to store document from {uri} in MongoDB: {e}")
                        mongodb_stored = False
                
                # Create result
                result = DocumentProcessingResult(
                    uri=uri,
                    success=processing_result.success,
                    document_type=processing_result.document_type,
                    extracted_data=processing_result.extracted_data,
                    processing_time=processing_result.processing_time,
                    validation_issues=processing_result.validation_issues,
                    confidence_score=processing_result.confidence_score,
                    error_message=processing_result.error_message,
                    mongodb_stored=mongodb_stored
                )
                
                if processing_result.success:
                    processed_count += 1
                else:
                    failed_count += 1
                    
                results.append(result)
                
            finally:
                # Clean up temp file
                try:
                    if temp_file_path and os.path.exists(temp_file_path):
                        Path(temp_file_path).unlink(missing_ok=True)
                        logger.debug(f"Cleaned up temp file: {temp_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
                    
        except Exception as e:
            logger.error(f"Error processing document from {uri}: {e}")
            result = DocumentProcessingResult(
                uri=uri,
                success=False,
                document_type="unknown",
                extracted_data={},
                processing_time=0.0,
                validation_issues=[f"Processing error: {str(e)}"],
                confidence_score=0.0,
                error_message=str(e),
                mongodb_stored=False
            )
            results.append(result)
            failed_count += 1
    
    total_processing_time = time.time() - start_time
    
    # Create response
    response = BatchProcessingResponse(
        success=processed_count > 0,
        batch_name=request.batch_name,
        student_id=request.student_id,
        total_documents=len(request.document_uris),
        processed_documents=processed_count,
        failed_documents=failed_count,
        results=results,
        total_processing_time=total_processing_time,
        message=f"Processed {processed_count}/{len(request.document_uris)} documents successfully"
    )
    
    # Send callback if URL provided
    if request.callback_url and processed_count > 0:
        try:
            await send_callback(request.callback_url, response)
            logger.info(f"Callback sent to {request.callback_url}")
        except Exception as e:
            logger.error(f"Failed to send callback to {request.callback_url}: {e}")
    
    logger.info(f"Batch processing completed: {processed_count} successful, {failed_count} failed")
    return response

@app.post("/api/fetch-and-process", response_model=MongoDBFetchResponse)
async def fetch_documents_from_mongodb_and_process(request: MongoDBFetchRequest):
    """
    Fetch documents from MongoDB collection and process their Cloudinary URIs
    
    This endpoint:
    1. Connects to the specified MongoDB collection
    2. Queries documents based on filter criteria
    3. Extracts Cloudinary URIs from each document
    4. Downloads and processes each document through OCR
    5. Stores processed results in the main documents collection
    6. Returns processing summary
    
    **Example request:**
    ```json
    {
        "collection_name": "raw_documents",
        "filter_criteria": {"student_id": "STUDENT_123", "processed": false},
        "uri_field_name": "cloudinary_url",
        "document_type_field": "doc_type",
        "student_id_field": "student_id",
        "batch_size": 5
    }
    ```
    
    **Use Cases:**
    - Process documents uploaded to a staging collection
    - Batch process unprocessed documents
    - Re-process documents with updated models
    - Process documents for specific students or document types
    """
    if not processor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document processor not available"
        )
    
    start_time = time.time()
    processing_results = []
    processed_count = 0
    failed_count = 0
    
    try:
        # Get database connection
        db_manager = await get_database()
        db = db_manager.db
        
        # Access the specified collection
        collection = db[request.collection_name]
        
        # Build MongoDB query
        query = request.filter_criteria or {}
        
        # Limit results to batch size
        cursor = collection.find(query).limit(request.batch_size)
        documents = await cursor.to_list(length=request.batch_size)
        
        logger.info(f"Found {len(documents)} documents in collection '{request.collection_name}' with filter: {query}")
        
        if not documents:
            return MongoDBFetchResponse(
                success=True,
                total_documents_found=0,
                documents_processed=0,
                documents_failed=0,
                collection_name=request.collection_name,
                filter_applied=query,
                processing_results=[],
                total_processing_time=time.time() - start_time,
                message="No documents found matching the criteria"
            )
        
        # Process each document
        for doc in documents:
            try:
                # Extract URI from document
                cloudinary_url = doc.get(request.uri_field_name)
                if not cloudinary_url:
                    logger.warning(f"Document {doc.get('_id')} missing URI field '{request.uri_field_name}'")
                    failed_count += 1
                    continue
                
                # Extract other fields
                document_type = doc.get(request.document_type_field) if request.document_type_field else None
                student_id = doc.get(request.student_id_field) if request.student_id_field else None
                document_id = str(doc.get('_id'))
                
                # Extract additional fields if requested
                additional_data = {}
                if request.additional_fields:
                    for field in request.additional_fields:
                        if field in doc:
                            additional_data[field] = doc[field]
                
                logger.info(f"Processing document {document_id} from {cloudinary_url}")
                
                # Download document from Cloudinary
                temp_file_path = await download_document_from_uri(cloudinary_url)
                
                if not temp_file_path:
                    result = DocumentProcessingResult(
                        uri=cloudinary_url,
                        success=False,
                        document_type="unknown",
                        extracted_data={"mongodb_document_id": document_id},
                        processing_time=0.0,
                        validation_issues=["Failed to download document from Cloudinary"],
                        confidence_score=0.0,
                        error_message=f"Could not download document from {cloudinary_url}",
                        mongodb_stored=False
                    )
                    processing_results.append(result)
                    failed_count += 1
                    continue
                
                try:
                    # Process the downloaded document with OCR
                    processing_result = await processor.process_document_async(temp_file_path, document_type)
                    
                    # Enhance extracted data with MongoDB document info
                    enhanced_extracted_data = processing_result.extracted_data.copy()
                    enhanced_extracted_data.update({
                        "mongodb_document_id": document_id,
                        "source_collection": request.collection_name,
                        "original_cloudinary_url": cloudinary_url
                    })
                    
                    # Add additional fields from original document
                    if additional_data:
                        enhanced_extracted_data["mongodb_additional_data"] = additional_data
                    
                    # Store in MongoDB if student_id is available
                    mongodb_stored = False
                    if student_id and processing_result.success:
                        try:
                            # Use document type from result if available, fallback to MongoDB or 'other'
                            detected_doc_type = (
                                processing_result.document_type if processing_result.document_type != 'unknown' 
                                else document_type or 'other'
                            )
                            
                            # Normalize extracted fields
                            normalized_fields = normalize_fields(enhanced_extracted_data, detected_doc_type)
                            
                            # Create document entry for database
                            doc_entry = DocumentEntry(
                                docType=detected_doc_type,
                                cloudinaryUrl=cloudinary_url,
                                documentPath=None,
                                fields=normalized_fields,
                                confidence=processing_result.confidence_score,
                                validationIssues=processing_result.validation_issues
                            )
                            
                            # Find or create student record
                            student = await StudentDocument.find_or_create_student(student_id)
                            
                            # Add document to student record
                            await student.add_document(doc_entry)
                            mongodb_stored = True
                            
                            logger.info(f"Document {document_id} stored in MongoDB for student {student_id}")
                            
                        except Exception as e:
                            logger.error(f"Failed to store document {document_id} in MongoDB: {e}")
                            mongodb_stored = False
                    
                    # Create processing result
                    result = DocumentProcessingResult(
                        uri=cloudinary_url,
                        success=processing_result.success,
                        document_type=processing_result.document_type,
                        extracted_data=enhanced_extracted_data,
                        processing_time=processing_result.processing_time,
                        validation_issues=processing_result.validation_issues,
                        confidence_score=processing_result.confidence_score,
                        error_message=processing_result.error_message,
                        mongodb_stored=mongodb_stored
                    )
                    
                    if processing_result.success:
                        processed_count += 1
                    else:
                        failed_count += 1
                        
                    processing_results.append(result)
                    
                finally:
                    # Clean up temp file
                    try:
                        if temp_file_path and os.path.exists(temp_file_path):
                            Path(temp_file_path).unlink(missing_ok=True)
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")
                        
            except Exception as e:
                logger.error(f"Error processing document {doc.get('_id')}: {e}")
                result = DocumentProcessingResult(
                    uri=doc.get(request.uri_field_name, "unknown"),
                    success=False,
                    document_type="unknown",
                    extracted_data={"mongodb_document_id": str(doc.get('_id'))},
                    processing_time=0.0,
                    validation_issues=[f"Processing error: {str(e)}"],
                    confidence_score=0.0,
                    error_message=str(e),
                    mongodb_stored=False
                )
                processing_results.append(result)
                failed_count += 1
    
    except Exception as e:
        logger.error(f"Error accessing MongoDB collection '{request.collection_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to access MongoDB collection: {str(e)}"
        )
    
    total_processing_time = time.time() - start_time
    
    # Create response
    response = MongoDBFetchResponse(
        success=processed_count > 0,
        total_documents_found=len(documents) if 'documents' in locals() else 0,
        documents_processed=processed_count,
        documents_failed=failed_count,
        collection_name=request.collection_name,
        filter_applied=query,
        processing_results=processing_results,
        total_processing_time=total_processing_time,
        message=f"Processed {processed_count}/{len(documents) if 'documents' in locals() else 0} documents from MongoDB collection"
    )
    
    # Send callback if URL provided
    if request.callback_url and processed_count > 0:
        try:
            # Convert response to dict for callback
            callback_data = response.dict()
            callback_data["callback_type"] = "mongodb_fetch_processing"
            
            await send_mongodb_callback(request.callback_url, callback_data)
            logger.info(f"MongoDB fetch callback sent to {request.callback_url}")
        except Exception as e:
            logger.error(f"Failed to send callback to {request.callback_url}: {e}")
    
    logger.info(f"MongoDB fetch processing completed: {processed_count} successful, {failed_count} failed from collection '{request.collection_name}'")
    return response

async def send_mongodb_callback(callback_url: str, response_data: Dict[str, Any]):
    """Send MongoDB processing results to callback URL"""
    try:
        import asyncio
        import concurrent.futures
        
        def send_callback_sync():
            response = requests.post(
                callback_url, 
                json=response_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code
        
        # Run the sync callback in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            status_code = await loop.run_in_executor(executor, send_callback_sync)
            
        if status_code == 200:
            logger.info(f"MongoDB callback successfully sent to {callback_url}")
        else:
            logger.warning(f"MongoDB callback to {callback_url} returned status {status_code}")
                    
    except Exception as e:
        logger.error(f"Failed to send MongoDB callback to {callback_url}: {e}")
        raise

async def download_document_from_uri(uri: str) -> Optional[str]:
    """Download document from URI and save to temp file"""
    try:
        import asyncio
        import concurrent.futures
        import hashlib
        import time
        
        def download_sync():
            # Try regular download first
            response = requests.get(uri, timeout=30, stream=True)
            
            # If unauthorized and it's a Cloudinary URL, try different URL formats
            if response.status_code == 401 and 'res.cloudinary.com' in uri:
                logger.info("Unauthorized access to Cloudinary, trying different URL formats...")
                response.close()  # Close the first response
                
                # Try different URL formats that might work
                url_variants = [
                    uri,  # Original URL
                    uri.replace('/upload/', '/upload/q_auto/'),  # Add quality parameter
                    uri.replace('/upload/', '/upload/f_auto/'),  # Add format parameter
                    uri.replace('/upload/', '/upload/q_auto,f_auto/'),  # Add both parameters
                ]
                
                for i, variant_url in enumerate(url_variants):
                    logger.info(f"Trying URL variant {i+1}: {variant_url}")
                    try:
                        response = requests.get(variant_url, timeout=30, stream=True)
                        if response.status_code == 200:
                            logger.info(f"Success with URL variant {i+1}!")
                            break
                        else:
                            response.close()
                            logger.warning(f"URL variant {i+1} failed: HTTP {response.status_code}")
                    except Exception as e:
                        logger.warning(f"URL variant {i+1} exception: {e}")
                        continue
                else:
                    logger.error("All URL variants failed")
                    return None
            
            if response.status_code == 200:
                # Get file extension from URI or content type
                content_type = response.headers.get('content-type', '')
                
                if content_type.startswith('image/'):
                    extension = '.jpg'
                elif content_type == 'application/pdf':
                    extension = '.pdf'
                else:
                    # Try to get from URI
                    path = Path(uri)
                    extension = path.suffix or '.jpg'
                
                # Create temp file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
                temp_path = temp_file.name
                
                # Download content
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file.close()
                response.close()
                
                logger.info(f"Downloaded document from {uri} to {temp_path}")
                return temp_path
            else:
                logger.error(f"Failed to download {uri}: HTTP {response.status_code}")
                response.close()
                return None
        
        # Run the sync download in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, download_sync)
                    
    except Exception as e:
        logger.error(f"Error downloading document from {uri}: {e}")
        return None

async def send_callback(callback_url: str, response_data: BatchProcessingResponse):
    """Send processing results to callback URL"""
    try:
        import asyncio
        import concurrent.futures
        
        def send_callback_sync():
            response = requests.post(
                callback_url, 
                json=response_data.dict(),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code
        
        # Run the sync callback in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            status_code = await loop.run_in_executor(executor, send_callback_sync)
            
        if status_code == 200:
            logger.info(f"Callback successfully sent to {callback_url}")
        else:
            logger.warning(f"Callback to {callback_url} returned status {status_code}")
                    
    except Exception as e:
        logger.error(f"Failed to send callback to {callback_url}: {e}")
        raise

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    print(" Starting FastAPI Document Processor...")
    print("Web interface: http://127.0.0.1:8000")
    print(" API docs: http://127.0.0.1:8000/docs")
    print(" ReDoc: http://127.0.0.1:8000/redoc")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")