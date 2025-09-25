"""
OCR Pipeline Extractors Package
MIT Hackathon Project

This package contains OCR engines and text extraction modules.
"""

from .ocr_engine import (
    OCREngine, 
    OCRResult, 
    BaseOCREngine, 
    TesseractEngine, 
    EasyOCREngine, 
    PaddleOCREngine,
    MultiEngineOCR,
    ImagePreprocessor,
    create_ocr_engine,
    create_multi_engine_ocr
)

from .entity_extractor import (
    EntityExtractor,
    EntityResult,
    create_entity_extractor
)

__all__ = [
    'OCREngine',
    'OCRResult', 
    'BaseOCREngine',
    'TesseractEngine',
    'EasyOCREngine', 
    'PaddleOCREngine',
    'MultiEngineOCR',
    'ImagePreprocessor',
    'create_ocr_engine',
    'create_multi_engine_ocr',
    'EntityExtractor',
    'EntityResult',
    'create_entity_extractor'
]