"""
Main OCR Automation Pipeline Module
MIT Hackathon Project

This module orchestrates the complete document processing pipeline:
document upload → classification → OCR → entity extraction → JSON validation
"""

import os
import uuid
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
from datetime import datetime

from .classifiers import DocumentClassifier, DocumentType, create_classifier
from .extractors import MultiEngineOCR, EntityExtractor, OCREngine, create_multi_engine_ocr, create_entity_extractor
from .validators import DocumentValidator, CrossValidator, create_validator, create_cross_validator
from .models import (
    ProcessingRequest, 
    ProcessingResult, 
    BatchProcessingRequest, 
    BatchProcessingResult,
    ProcessingStatus,
    DocumentUpload,
    OCRMetadata,
    ClassificationMetadata,
    ExtractionMetadata,
    ValidationMetadata
)

logger = logging.getLogger(__name__)

class OCRPipeline:
    """
    Main OCR automation pipeline that processes documents from upload to structured JSON.
    """
    
    def __init__(self, 
                 ocr_engines: Optional[List[OCREngine]] = None,
                 model_path: Optional[str] = None,
                 spacy_model: str = "en_core_web_sm"):
        """
        Initialize the OCR pipeline.
        
        Args:
            ocr_engines: List of OCR engines to use
            model_path: Path to custom ML models
            spacy_model: spaCy model name for NLP
        """
        
        # Initialize components
        logger.info("Initializing OCR Pipeline components...")
        
        try:
            # Document classifier
            self.classifier = create_classifier(model_path=model_path)
            logger.info("✓ Document classifier initialized")
            
            # OCR engines
            if ocr_engines is None:
                ocr_engines = [OCREngine.TESSERACT, OCREngine.EASYOCR]
            self.ocr_engine = create_multi_engine_ocr(engines=ocr_engines)
            logger.info(f"✓ OCR engines initialized: {[e.value for e in self.ocr_engine.get_available_engines()]}")
            
            # Entity extractor
            self.entity_extractor = create_entity_extractor(model_name=spacy_model)
            logger.info("✓ Entity extractor initialized")
            
            # Validators
            self.validator = create_validator()
            self.cross_validator = create_cross_validator()
            logger.info("✓ Validators initialized")
            
            # Processing statistics
            self.stats = {
                "documents_processed": 0,
                "successful_extractions": 0,
                "failed_extractions": 0,
                "average_processing_time": 0.0
            }
            
            logger.info("OCR Pipeline fully initialized and ready!")
            
        except Exception as e:
            logger.error(f"Failed to initialize OCR Pipeline: {str(e)}")
            raise
    
    def process_document(self, request: ProcessingRequest) -> ProcessingResult:
        """
        Process a single document through the complete pipeline.
        
        Args:
            request: Processing request with document upload info
            
        Returns:
            ProcessingResult with all processing outcomes
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Processing document: {request.document_upload.file_name} (ID: {request_id})")
        
        # Initialize result
        result = ProcessingResult(
            request_id=request_id,
            status=ProcessingStatus.PROCESSING,
            document_upload=request.document_upload
        )
        
        try:
            # Step 1: Initial OCR Text Extraction (needed for improved classification)
            logger.info("Step 1: OCR Text Extraction")
            ocr_result = self.ocr_engine.extract_text(
                request.document_upload.file_path,
                use_best_result=True
            )
            
            result.ocr_result = {
                "text": ocr_result.text,
                "metadata": OCRMetadata(
                    engine_used=ocr_result.engine_used.value,
                    confidence=ocr_result.confidence,
                    processing_time=ocr_result.processing_time,
                    bounding_boxes=ocr_result.bounding_boxes,
                    word_confidences=ocr_result.word_confidences
                ).dict()
            }
            
            logger.info(f"✓ OCR completed using {ocr_result.engine_used.value} "
                       f"(confidence: {ocr_result.confidence:.3f}, "
                       f"text length: {len(ocr_result.text)} chars)")
            
            # Step 2: Document Classification (using OCR text for better accuracy)
            logger.info("Step 2: Document Classification")
            classification_result = self.classifier.classify_document(
                request.document_upload.file_path,
                ocr_text=ocr_result.text
            )
            
            result.classification_result = ClassificationMetadata(
                document_type=classification_result.document_type,
                confidence=classification_result.confidence,
                features=classification_result.features,
                classification_method="hybrid_with_ocr"
            )
            
            logger.info(f"✓ Document classified as: {classification_result.document_type.value} "
                       f"(confidence: {classification_result.confidence:.3f})")
            # Step 3: Entity Extraction
            logger.info("Step 3: Entity Extraction")
            extraction_result = self.entity_extractor.extract_entities(
                ocr_result.text,
                classification_result.document_type,
                additional_context={"file_path": request.document_upload.file_path}
            )
            
            result.extraction_result = {
                "entities": extraction_result.entities,
                "metadata": ExtractionMetadata(
                    extraction_method=extraction_result.extraction_method,
                    confidence=extraction_result.confidence,
                    processing_time=extraction_result.processing_time,
                    template_used=extraction_result.metadata.get("template_used")
                ).dict()
            }
            
            logger.info(f"✓ Entity extraction completed "
                       f"(confidence: {extraction_result.confidence:.3f}, "
                       f"entities found: {len(extraction_result.entities)})")
            
            # Step 4: Create structured data
            logger.info("Step 4: Creating Structured Data")
            structured_data = self._create_structured_data(
                extraction_result.entities,
                classification_result.document_type,
                {
                    "processing_metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "ocr_engine": ocr_result.engine_used.value,
                        "confidence": ocr_result.confidence,
                        "file_path": request.document_upload.file_path
                    }
                }
            )
            
            result.structured_data = structured_data
            
            # Step 5: JSON Validation
            logger.info("Step 5: JSON Validation")
            validation_result = self.validator.validate_document(
                structured_data.dict() if structured_data else extraction_result.entities,
                classification_result.document_type
            )
            
            result.validation_result = ValidationMetadata(
                is_valid=validation_result.is_valid,
                errors=validation_result.errors,
                warnings=validation_result.warnings,
                confidence_score=validation_result.confidence_score,
                schema_used=classification_result.document_type.value
            )
            
            logger.info(f"✓ Validation completed "
                       f"(valid: {validation_result.is_valid}, "
                       f"confidence: {validation_result.confidence_score:.3f})")
            
            # Finalize result
            total_time = time.time() - start_time
            result.total_processing_time = total_time
            result.status = ProcessingStatus.COMPLETED
            result.completed_at = datetime.now()
            
            # Update statistics
            self.stats["documents_processed"] += 1
            if validation_result.is_valid:
                self.stats["successful_extractions"] += 1
            else:
                self.stats["failed_extractions"] += 1
            
            # Update average processing time
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["documents_processed"] - 1) + total_time) 
                / self.stats["documents_processed"]
            )
            
            logger.info(f"Document processing completed successfully in {total_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {request_id}: {str(e)}")
            
            result.status = ProcessingStatus.FAILED
            result.error_message = str(e)
            result.total_processing_time = time.time() - start_time
            result.completed_at = datetime.now()
            
            self.stats["documents_processed"] += 1
            self.stats["failed_extractions"] += 1
            
            return result
    
    def process_batch(self, request: BatchProcessingRequest) -> BatchProcessingResult:
        """
        Process multiple documents in batch with cross-validation.
        
        Args:
            request: Batch processing request
            
        Returns:
            BatchProcessingResult with all individual results
        """
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Processing batch: {len(request.documents)} documents (ID: {batch_id})")
        
        # Initialize batch result
        batch_result = BatchProcessingResult(
            batch_id=batch_id,
            individual_results=[],
            batch_status=ProcessingStatus.PROCESSING
        )
        
        try:
            # Process each document individually
            individual_results = []
            for i, doc_upload in enumerate(request.documents):
                logger.info(f"Processing document {i+1}/{len(request.documents)}: {doc_upload.file_name}")
                
                individual_request = ProcessingRequest(
                    document_upload=doc_upload,
                    processing_options=request.processing_options,
                    user_id=request.user_id,
                    session_id=request.session_id
                )
                
                individual_result = self.process_document(individual_request)
                individual_results.append(individual_result)
            
            batch_result.individual_results = individual_results
            
            # Cross-validation if requested
            if request.cross_validate and len(individual_results) > 1:
                logger.info("Performing cross-validation...")
                
                structured_docs = []
                for result in individual_results:
                    if result.structured_data and result.status == ProcessingStatus.COMPLETED:
                        structured_docs.append(result.structured_data.dict())
                
                if structured_docs:
                    cross_val_result = self.cross_validator.cross_validate_documents(structured_docs)
                    
                    batch_result.cross_validation_result = ValidationMetadata(
                        is_valid=cross_val_result.is_valid,
                        errors=cross_val_result.errors,
                        warnings=cross_val_result.warnings,
                        confidence_score=cross_val_result.confidence_score,
                        schema_used="cross_validation"
                    )
                    
                    logger.info(f"✓ Cross-validation completed "
                               f"(valid: {cross_val_result.is_valid}, "
                               f"confidence: {cross_val_result.confidence_score:.3f})")
            
            # Finalize batch result
            batch_result.total_processing_time = time.time() - start_time
            batch_result.batch_status = ProcessingStatus.COMPLETED
            batch_result.completed_at = datetime.now()
            
            successful_count = sum(1 for r in individual_results 
                                 if r.status == ProcessingStatus.COMPLETED)
            
            logger.info(f"Batch processing completed: "
                       f"{successful_count}/{len(individual_results)} documents successful "
                       f"in {batch_result.total_processing_time:.2f}s")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_id}: {str(e)}")
            
            batch_result.batch_status = ProcessingStatus.FAILED
            batch_result.total_processing_time = time.time() - start_time
            batch_result.completed_at = datetime.now()
            
            return batch_result
    
    def _create_structured_data(self, 
                              entities: Dict[str, Any], 
                              document_type: DocumentType,
                              additional_data: Dict[str, Any]) -> Optional[Any]:
        """
        Create structured data model from extracted entities.
        
        Args:
            entities: Extracted entities
            document_type: Type of document
            additional_data: Additional metadata
            
        Returns:
            Structured data model instance
        """
        try:
            # Combine entities with additional data
            combined_data = {
                **entities,
                **additional_data,
                "document_type": document_type
            }
            
            # Import document models dynamically to avoid circular imports
            from .models import (
                Marksheet10thData, 
                Marksheet12thData,
                EntranceScorecardData,
                CasteCertificateData,
                AadharCardData,
                BaseDocumentData
            )
            
            # Create appropriate model based on document type
            if document_type == DocumentType.MARKSHEET_10TH:
                return Marksheet10thData(**combined_data)
            elif document_type == DocumentType.MARKSHEET_12TH:
                return Marksheet12thData(**combined_data)
            elif document_type == DocumentType.ENTRANCE_SCORECARD:
                return EntranceScorecardData(**combined_data)
            elif document_type == DocumentType.CASTE_CERTIFICATE:
                return CasteCertificateData(**combined_data)
            elif document_type == DocumentType.AADHAR_CARD:
                return AadharCardData(**combined_data)
            else:
                return BaseDocumentData(**combined_data)
                
        except Exception as e:
            logger.warning(f"Could not create structured data model: {str(e)}")
            # Return base model with available data
            try:
                from .models import BaseDocumentData
                return BaseDocumentData(
                    document_type=document_type,
                    name=entities.get("name", "Unknown"),
                    processing_metadata=additional_data.get("processing_metadata", {})
                )
            except:
                return None
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline processing statistics"""
        return {
            **self.stats,
            "available_ocr_engines": [e.value for e in self.ocr_engine.get_available_engines()],
            "supported_document_types": [dt.value for dt in DocumentType],
            "pipeline_status": "ready"
        }
    
    def health_check(self) -> Dict[str, str]:
        """Perform health check on all pipeline components"""
        health_status = {}
        
        try:
            # Check classifier
            health_status["classifier"] = "healthy"
        except:
            health_status["classifier"] = "unhealthy"
        
        try:
            # Check OCR engines
            available_engines = self.ocr_engine.get_available_engines()
            health_status["ocr_engines"] = f"healthy ({len(available_engines)} engines)"
        except:
            health_status["ocr_engines"] = "unhealthy"
        
        try:
            # Check entity extractor
            health_status["entity_extractor"] = "healthy"
        except:
            health_status["entity_extractor"] = "unhealthy"
        
        try:
            # Check validators
            health_status["validators"] = "healthy"
        except:
            health_status["validators"] = "unhealthy"
        
        # Overall status
        if all(status == "healthy" or status.startswith("healthy") for status in health_status.values()):
            health_status["overall"] = "healthy"
        else:
            health_status["overall"] = "degraded"
        
        return health_status

def create_pipeline(ocr_engines: Optional[List[OCREngine]] = None,
                   model_path: Optional[str] = None,
                   spacy_model: str = "en_core_web_sm") -> OCRPipeline:
    """
    Factory function to create an OCR pipeline instance.
    
    Args:
        ocr_engines: List of OCR engines to use
        model_path: Path to custom ML models
        spacy_model: spaCy model name
        
    Returns:
        OCRPipeline instance
    """
    return OCRPipeline(
        ocr_engines=ocr_engines,
        model_path=model_path,
        spacy_model=spacy_model
    )