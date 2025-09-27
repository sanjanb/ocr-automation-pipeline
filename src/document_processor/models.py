"""
API Models for Document Processing Endpoint
Request and response models for the microservice
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ProcessDocumentRequest(BaseModel):
    """Request model for /process-doc endpoint"""
    studentId: str = Field(..., min_length=1, max_length=50, description="Unique student identifier")
    docType: str = Field(..., description="Document type (AadharCard, MarkSheet10, MarkSheet12, etc.)")
    cloudinaryUrl: Optional[str] = Field(None, description="Cloudinary URL of the document image")
    documentPath: Optional[str] = Field(None, description="Local file path for testing (alternative to cloudinaryUrl)")
    
    @validator('docType')
    def validate_doc_type(cls, v):
        # Define supported document types mapping
        supported_types = {
            'AadharCard': 'aadhaar_card',
            'MarkSheet10': 'marksheet_10th',
            'MarkSheet12': 'marksheet_12th',
            'TransferCertificate': 'transfer_certificate',
            'MigrationCertificate': 'migration_certificate',
            'EntranceScorecard': 'entrance_scorecard',
            'AdmitCard': 'admit_card',
            'CasteCertificate': 'caste_certificate',
            'DomicileCertificate': 'domicile_certificate',
        }
        
        if v not in supported_types:
            raise ValueError(f'Unsupported document type. Supported types: {list(supported_types.keys())}')
        return v
    
    @validator('cloudinaryUrl')
    def validate_cloudinary_url(cls, v, values):
        if v is not None and not v.startswith('https://res.cloudinary.com'):
            raise ValueError('Invalid Cloudinary URL format')
        return v
    
    @validator('documentPath')
    def validate_document_path(cls, v, values):
        """Validate local document path if provided"""
        if v is not None:
            # Check if it's a relative path starting with assets/test_docs
            if not v.startswith('assets/test_docs/'):
                raise ValueError('Document path must start with assets/test_docs/')
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.webp']
            if not any(v.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError(f'Invalid file extension. Supported: {valid_extensions}')
        return v
    
    @validator('documentPath', always=True)
    def validate_either_url_or_path(cls, v, values):
        """Ensure either cloudinaryUrl or documentPath is provided, but not both"""
        cloudinary_url = values.get('cloudinaryUrl')
        if cloudinary_url is None and v is None:
            raise ValueError('Either cloudinaryUrl or documentPath must be provided')
        if cloudinary_url is not None and v is not None:
            raise ValueError('Provide either cloudinaryUrl or documentPath, not both')
        return v
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "studentId": "12345",
                "docType": "AadharCard",
                "documentPath": "assets/test_docs/aadhaar_sample.jpg"
            }
        }

class ProcessedDocumentResponse(BaseModel):
    """Response model for processed document"""
    docType: str = Field(..., description="Type of document processed")
    cloudinaryUrl: Optional[str] = Field(None, description="Source Cloudinary URL")
    documentPath: Optional[str] = Field(None, description="Source local file path")
    fields: Dict[str, Any] = Field(..., description="Normalized extracted fields")
    processedAt: datetime = Field(..., description="Processing timestamp")
    confidence: float = Field(..., description="Processing confidence score (0.0-1.0)")
    modelUsed: str = Field(..., description="AI model used for processing")
    validationIssues: List[str] = Field(default_factory=list, description="Any validation issues found")

class ProcessDocumentResponse(BaseModel):
    """Response model for /process-doc endpoint"""
    success: bool = Field(..., description="Whether the processing was successful")
    studentId: str = Field(..., description="Student identifier")
    savedDocument: ProcessedDocumentResponse = Field(..., description="Details of the saved document")
    message: str = Field(default="Document processed successfully", description="Response message")
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "success": True,
                "studentId": "12345",
                "savedDocument": {
                    "docType": "AadharCard",
                    "documentPath": "assets/test_docs/aadhaar_sample.jpg",
                    "fields": {
                        "Name": "Sanjan Acharya",
                        "DOB": "2002-06-15",
                        "Address": "Bangalore, Karnataka"
                    },
                    "processedAt": "2025-09-27T18:45:00Z",
                    "confidence": 0.95,
                    "modelUsed": "gemini-2.0-flash-exp",
                    "validationIssues": []
                },
                "message": "Document processed successfully"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database_connected: bool = Field(..., description="Database connection status")
    gemini_configured: bool = Field(..., description="Gemini API configuration status")

class StudentDocumentsResponse(BaseModel):
    """Response for getting all student documents"""
    success: bool = Field(..., description="Request success status")
    studentId: str = Field(..., description="Student identifier")
    documents: List[ProcessedDocumentResponse] = Field(..., description="List of all student documents")
    totalDocuments: int = Field(..., description="Total number of documents")
    createdAt: datetime = Field(..., description="Student record creation date")
    updatedAt: datetime = Field(..., description="Last update timestamp")

# Document Type Mapping
DOCUMENT_TYPE_MAPPING = {
    'AadharCard': 'aadhaar_card',
    'MarkSheet10': 'marksheet_10th',
    'MarkSheet12': 'marksheet_12th',
    'TransferCertificate': 'transfer_certificate',
    'MigrationCertificate': 'migration_certificate',
    'EntranceScorecard': 'entrance_scorecard',
    'AdmitCard': 'admit_card',
    'CasteCertificate': 'caste_certificate',
    'DomicileCertificate': 'domicile_certificate',
}

def get_internal_doc_type(external_doc_type: str) -> str:
    """Convert external document type to internal schema type"""
    return DOCUMENT_TYPE_MAPPING.get(external_doc_type, 'other')