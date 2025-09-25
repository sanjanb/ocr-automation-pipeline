#!/usr/bin/env python3
"""
Enhanced OCR pipeline with AI-powered entity extraction option
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

from .extractors import MultiEngineOCR, EntityExtractor, OCREngine
from .classifiers import DocumentClassifier, DocumentType
from .extractors.ai_entity_extractor import AIEntityExtractor, AIExtractionResult

logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    """Result from the OCR pipeline"""
    success: bool
    document_type: DocumentType
    extracted_text: str = ""
    entities: Dict[str, Any] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None
    error: str = ""
    processing_time: float = 0.0
    method_used: str = ""  # "traditional" or "ai"

class EnhancedOCRPipeline:
    """
    Enhanced OCR pipeline with both traditional and AI-powered extraction options
    """
    
    def __init__(self, 
                 use_ai: bool = True,
                 hf_token: Optional[str] = None,
                 ai_fallback_threshold: float = 0.6):
        """
        Initialize enhanced pipeline
        
        Args:
            use_ai: Whether to use AI-powered extraction as primary method
            hf_token: Hugging Face API token for AI models
            ai_fallback_threshold: Confidence threshold below which to try traditional OCR
        """
        self.use_ai = use_ai
        self.ai_fallback_threshold = ai_fallback_threshold
        
        # Initialize traditional components
        self.ocr_engine = MultiEngineOCR()
        self.document_classifier = DocumentClassifier()
        self.entity_extractor = EntityExtractor()
        
        # Initialize AI components
        if use_ai:
            try:
                self.ai_extractor = AIEntityExtractor(hf_token=hf_token)
                logger.info("AI entity extractor initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize AI extractor: {e}")
                self.ai_extractor = None
                self.use_ai = False
        else:
            self.ai_extractor = None
            
    def process_document(self, image_path: str, 
                        method: str = "auto",
                        document_type_hint: Optional[str] = None) -> PipelineResult:
        """
        Process document using specified method
        
        Args:
            image_path: Path to the document image
            method: "auto", "ai", or "traditional"
            document_type_hint: Optional hint about document type
            
        Returns:
            PipelineResult with extracted information
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Processing document: {image_path} using method: {method}")
            
            # Auto method selection
            if method == "auto":
                if self.use_ai and self.ai_extractor:
                    method = "ai"
                else:
                    method = "traditional"
            
            # Try AI-powered extraction first
            if method == "ai" and self.ai_extractor:
                result = self._process_with_ai(image_path, document_type_hint)
                
                # Fallback to traditional if AI confidence is too low
                if result.confidence < self.ai_fallback_threshold:
                    logger.info(f"AI confidence {result.confidence:.3f} below threshold {self.ai_fallback_threshold}, trying traditional method")
                    traditional_result = self._process_traditional(image_path)
                    
                    # Use better result
                    if traditional_result.confidence > result.confidence:
                        result = traditional_result
                        result.metadata["ai_fallback"] = True
                    else:
                        result.metadata["traditional_fallback_attempted"] = True
                        
            else:
                # Use traditional OCR pipeline
                result = self._process_traditional(image_path)
            
            result.processing_time = time.time() - start_time
            logger.info(f"Processing completed in {result.processing_time:.2f}s using {result.method_used}")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            return PipelineResult(
                success=False,
                document_type=DocumentType.OTHER,
                error=str(e),
                processing_time=time.time() - start_time,
                method_used="error"
            )
    
    def _process_with_ai(self, image_path: str, document_type_hint: Optional[str] = None) -> PipelineResult:
        """Process document using AI-powered extraction"""
        logger.info("Using AI-powered extraction")
        
        try:
            # Map document type hint to AI format
            ai_doc_type = self._map_to_ai_document_type(document_type_hint)
            
            # Extract with AI
            ai_result = self.ai_extractor.extract_from_image(image_path, ai_doc_type)
            
            # Convert AI result to pipeline result
            if ai_result.entities:
                # Map AI document type back to our enum
                doc_type = self._map_from_ai_document_type(ai_doc_type)
                
                return PipelineResult(
                    success=True,
                    document_type=doc_type,
                    extracted_text="[AI-extracted structured data]",
                    entities=ai_result.entities,
                    confidence=ai_result.confidence,
                    metadata={
                        "ai_model": ai_result.model_used,
                        "ai_raw_output": ai_result.raw_output,
                        **ai_result.metadata
                    },
                    method_used="ai"
                )
            else:
                return PipelineResult(
                    success=False,
                    document_type=DocumentType.OTHER,
                    confidence=0.0,
                    metadata={"ai_error": "No entities extracted"},
                    method_used="ai"
                )
                
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return PipelineResult(
                success=False,
                document_type=DocumentType.OTHER,
                error=str(e),
                method_used="ai"
            )
    
    def _process_traditional(self, image_path: str) -> PipelineResult:
        """Process document using traditional OCR pipeline"""
        logger.info("Using traditional OCR extraction")
        
        try:
            # Step 1: OCR text extraction
            logger.info("Extracting text with MultiEngineOCR")
            ocr_result = self.ocr_engine.extract_text(image_path)
            
            if not ocr_result.success or not ocr_result.text or len(ocr_result.text.strip()) < 50:
                return PipelineResult(
                    success=False,
                    document_type=DocumentType.OTHER,
                    error="OCR failed to extract sufficient text",
                    method_used="traditional"
                )
            
            extracted_text = ocr_result.text
            ocr_metadata = {
                "ocr_confidence": ocr_result.confidence,
                "text_length": len(extracted_text),
                "processing_time": ocr_result.processing_time,
                "engine_used": ocr_result.metadata.get("engine_used", "unknown")
            }
            
            # Step 2: Document classification
            classification_result = self.document_classifier.classify_from_text(extracted_text)
            document_type = classification_result.document_type
            
            # Step 3: Entity extraction
            entity_result = self.entity_extractor.extract_entities(extracted_text, document_type)
            
            # Combine results
            final_confidence = (
                ocr_metadata.get("ocr_confidence", 0.5) * 0.3 +
                classification_result.confidence * 0.3 +
                entity_result.confidence * 0.4
            )
            
            return PipelineResult(
                success=True,
                document_type=document_type,
                extracted_text=extracted_text,
                entities=entity_result.entities,
                confidence=final_confidence,
                metadata={
                    **ocr_metadata,
                    "classification_confidence": classification_result.confidence,
                    "entity_extraction_confidence": entity_result.confidence,
                    **entity_result.metadata
                },
                method_used="traditional"
            )
            
        except Exception as e:
            logger.error(f"Traditional processing failed: {e}")
            return PipelineResult(
                success=False,
                document_type=DocumentType.OTHER,
                error=str(e),
                method_used="traditional"
            )
    
    def _map_to_ai_document_type(self, document_type_hint: Optional[str]) -> str:
        """Map our document type to AI model document type"""
        mapping = {
            "marksheet_12th": "marksheet_12th",
            "marksheet_10th": "marksheet_10th", 
            "entrance_scorecard": "entrance_scorecard",
            "caste_certificate": "caste_certificate"
        }
        
        return mapping.get(document_type_hint, "marksheet_12th")  # Default to 12th marksheet
    
    def _map_from_ai_document_type(self, ai_doc_type: str) -> DocumentType:
        """Map AI document type back to our enum"""
        mapping = {
            "marksheet_12th": DocumentType.MARKSHEET_12TH,
            "marksheet_10th": DocumentType.MARKSHEET_10TH,
            "entrance_scorecard": DocumentType.ENTRANCE_SCORECARD,
            "caste_certificate": DocumentType.CASTE_CERTIFICATE
        }
        
        return mapping.get(ai_doc_type, DocumentType.OTHER)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    def validate_image_file(self, image_path: str) -> bool:
        """Validate if image file is supported and exists"""
        if not os.path.exists(image_path):
            return False
            
        file_ext = Path(image_path).suffix.lower()
        return file_ext in self.get_supported_formats()

def create_enhanced_pipeline(use_ai: bool = True, 
                           hf_token: Optional[str] = None,
                           ai_fallback_threshold: float = 0.6) -> EnhancedOCRPipeline:
    """
    Factory function to create enhanced OCR pipeline
    
    Args:
        use_ai: Whether to use AI-powered extraction
        hf_token: Hugging Face API token
        ai_fallback_threshold: Confidence threshold for AI fallback
        
    Returns:
        EnhancedOCRPipeline instance
    """
    return EnhancedOCRPipeline(
        use_ai=use_ai,
        hf_token=hf_token, 
        ai_fallback_threshold=ai_fallback_threshold
    )