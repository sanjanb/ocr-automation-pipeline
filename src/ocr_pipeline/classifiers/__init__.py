"""
OCR Pipeline Classifier Package
MIT Hackathon Project

This package contains document classification modules for the OCR automation pipeline.
"""

from .document_classifier import DocumentClassifier, DocumentType, ClassificationResult, create_classifier

__all__ = [
    'DocumentClassifier',
    'DocumentType', 
    'ClassificationResult',
    'create_classifier'
]