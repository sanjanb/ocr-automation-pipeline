"""
Data Models for OCR Automation Pipeline
MIT Hackathon Project

This module contains Pydantic data models for the OCR pipeline.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum

from ..classifiers.document_classifier import DocumentType

class ProcessingStatus(str, Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentUpload(BaseModel):
    """Model for document upload request"""
    file_name: str = Field(..., description="Name of uploaded file")
    file_path: str = Field(..., description="Path to uploaded file")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of file")
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProcessingRequest(BaseModel):
    """Model for processing request"""
    document_upload: DocumentUpload
    processing_options: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class OCRMetadata(BaseModel):
    """Metadata from OCR processing"""
    engine_used: str
    confidence: float = Field(..., ge=0, le=1)
    processing_time: float = Field(..., description="Processing time in seconds")
    bounding_boxes: List[List[int]] = Field(default_factory=list)
    word_confidences: List[float] = Field(default_factory=list)

class ClassificationMetadata(BaseModel):
    """Metadata from document classification"""
    document_type: DocumentType
    confidence: float = Field(..., ge=0, le=1)
    features: Dict[str, float] = Field(default_factory=dict)
    classification_method: str = "hybrid"

class ExtractionMetadata(BaseModel):
    """Metadata from entity extraction"""
    extraction_method: str = "hybrid"
    confidence: float = Field(..., ge=0, le=1)
    processing_time: float
    template_used: Optional[str] = None

class ValidationMetadata(BaseModel):
    """Metadata from validation"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0, le=1)
    schema_used: str

# Document-specific models
class BaseDocumentData(BaseModel):
    """Base model for all documents"""
    document_type: DocumentType
    name: str = Field(..., min_length=3, max_length=100)
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)

class MarksheetData(BaseDocumentData):
    """Data model for marksheet documents"""
    roll_number: str = Field(..., pattern=r"^\d{6,12}$")
    board: str
    year: int = Field(..., ge=1990, le=datetime.now().year)
    school_name: Optional[str] = None
    dob: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    father_name: Optional[str] = None
    subjects: Dict[str, int] = Field(..., description="Subject-wise marks")
    total_marks: Optional[int] = None
    percentage: Optional[float] = Field(None, ge=0, le=100)
    grade: Optional[str] = None
    
    @validator('subjects')
    def validate_subjects(cls, v):
        if not v:
            raise ValueError("Subjects cannot be empty")
        for subject, marks in v.items():
            if not isinstance(marks, int) or marks < 0 or marks > 100:
                raise ValueError(f"Invalid marks for {subject}: {marks}")
        return v

class Marksheet10thData(MarksheetData):
    """Specific model for 10th marksheet"""
    document_type: DocumentType = DocumentType.MARKSHEET_10TH

class Marksheet12thData(MarksheetData):
    """Specific model for 12th marksheet"""
    document_type: DocumentType = DocumentType.MARKSHEET_12TH
    stream: str = Field(..., pattern=r"^(Science|Commerce|Arts|Humanities)$")

class EntranceScorecardData(BaseDocumentData):
    """Data model for entrance exam scorecard"""
    document_type: DocumentType = DocumentType.ENTRANCE_SCORECARD
    roll_number: str = Field(..., pattern=r"^[A-Z0-9]{8,15}$")
    exam_name: str
    rank: int = Field(..., ge=1, le=10000000)
    category_rank: Optional[int] = Field(None, ge=1)
    score: int = Field(..., ge=0)
    percentile: Optional[float] = Field(None, ge=0, le=100)
    category: Optional[str] = None
    exam_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    qualifying_marks: Optional[int] = Field(None, ge=0)
    
    @validator('category_rank')
    def validate_category_rank(cls, v, values):
        if v is not None and 'rank' in values and v > values['rank']:
            raise ValueError("Category rank cannot be higher than overall rank")
        return v

class CasteCertificateData(BaseDocumentData):
    """Data model for caste certificate"""
    document_type: DocumentType = DocumentType.CASTE_CERTIFICATE
    category: str = Field(..., pattern=r"^(SC|ST|OBC|EWS)$")
    caste: str = Field(..., max_length=100)
    issuing_authority: str = Field(..., max_length=200)
    certificate_number: Optional[str] = Field(None, pattern=r"^[A-Z0-9/-]+$")
    issue_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    validity_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    father_name: Optional[str] = None
    address: Optional[Dict[str, str]] = None

class AadharCardData(BaseDocumentData):
    """Data model for Aadhar card"""
    document_type: DocumentType = DocumentType.AADHAR_CARD
    aadhar_number: str = Field(..., pattern=r"^\d{4}\s*\d{4}\s*\d{4}$")
    dob: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    gender: Optional[str] = Field(None, pattern=r"^(Male|Female|Other)$")
    father_name: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    mobile: Optional[str] = Field(None, pattern=r"^[6-9]\d{9}$")
    email: Optional[str] = None

# Processing result models
class ProcessingResult(BaseModel):
    """Complete processing result"""
    request_id: str = Field(..., description="Unique processing request ID")
    status: ProcessingStatus
    document_upload: DocumentUpload
    
    # Processing results
    ocr_result: Optional[Dict[str, Any]] = None
    classification_result: Optional[ClassificationMetadata] = None
    extraction_result: Optional[Dict[str, Any]] = None
    validation_result: Optional[ValidationMetadata] = None
    
    # Final structured data
    structured_data: Optional[Union[
        Marksheet10thData,
        Marksheet12thData, 
        EntranceScorecardData,
        CasteCertificateData,
        AadharCardData,
        BaseDocumentData
    ]] = None
    
    # Processing metadata
    total_processing_time: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            DocumentType: lambda v: v.value
        }

class BatchProcessingRequest(BaseModel):
    """Model for batch processing multiple documents"""
    documents: List[DocumentUpload]
    processing_options: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    cross_validate: bool = True

class BatchProcessingResult(BaseModel):
    """Result from batch processing"""
    batch_id: str
    individual_results: List[ProcessingResult]
    cross_validation_result: Optional[ValidationMetadata] = None
    batch_status: ProcessingStatus
    total_processing_time: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# API Response models
class APIResponse(BaseModel):
    """Base API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UploadResponse(APIResponse):
    """Response for file upload"""
    data: Optional[DocumentUpload] = None

class ProcessingStatusResponse(APIResponse):
    """Response for processing status check"""
    data: Optional[ProcessingResult] = None

class ValidationResponse(APIResponse):
    """Response for validation results"""
    data: Optional[ValidationMetadata] = None

# Health check and system status models
class SystemHealth(BaseModel):
    """System health check model"""
    status: str = Field(..., description="Overall system status")
    components: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "0.1.0"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }