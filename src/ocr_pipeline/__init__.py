"""
OCR Automation Pipeline
MIT Hackathon Project

An intelligent document processing pipeline that performs:
- Document classification 
- OCR text extraction
- Entity extraction
- JSON structuring
- Cross-validation

Supports multiple document types including:
- 10th/12th Marksheets
- Entrance Exam Scorecards  
- Caste/Domicile Certificates
- Aadhar Cards
- Transfer/Migration Certificates
"""

__version__ = "0.1.0"
__author__ = "MIT Hackathon Team"
__email__ = "team@example.com"

# Core pipeline
from .pipeline import OCRPipeline, create_pipeline

# Main components
from .classifiers import DocumentClassifier, DocumentType, create_classifier
from .extractors import MultiEngineOCR, OCREngine, EntityExtractor, create_multi_engine_ocr, create_entity_extractor
from .validators import DocumentValidator, create_validator, validate_document_json

# Data models
from .models import (
    ProcessingRequest,
    ProcessingResult,
    BatchProcessingRequest, 
    BatchProcessingResult,
    ProcessingStatus,
    DocumentUpload,
    APIResponse
)

__all__ = [
    # Core
    "OCRPipeline",
    "create_pipeline",
    
    # Components
    "DocumentClassifier",
    "DocumentType", 
    "create_classifier",
    "MultiEngineOCR",
    "OCREngine",
    "EntityExtractor", 
    "create_multi_engine_ocr",
    "create_entity_extractor",
    "DocumentValidator",
    "create_validator",
    "validate_document_json",
    
    # Models
    "ProcessingRequest",
    "ProcessingResult", 
    "BatchProcessingRequest",
    "BatchProcessingResult",
    "ProcessingStatus",
    "DocumentUpload",
    "APIResponse"
]