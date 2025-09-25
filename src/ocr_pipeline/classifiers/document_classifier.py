"""
Document Classification Module for OCR Automation Pipeline
MIT Hackathon Project

This module contains the document classifier that identifies document types
from uploaded files using computer vision and machine learning.
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path
import torch
import torchvision.transforms as transforms
from PIL import Image
import logging
from dataclasses import dataclass

# Set up logging
logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Enumeration of supported document types"""
    MARKSHEET_10TH = "marksheet_10th"
    MARKSHEET_12TH = "marksheet_12th"
    PASSING_CERTIFICATE = "passing_certificate"
    TRANSFER_CERTIFICATE = "transfer_certificate"
    MIGRATION_CERTIFICATE = "migration_certificate"
    ENTRANCE_SCORECARD = "entrance_scorecard"
    ENTRANCE_ADMIT_CARD = "entrance_admit_card"
    CASTE_CERTIFICATE = "caste_certificate"
    DOMICILE_CERTIFICATE = "domicile_certificate"
    AADHAR_CARD = "aadhar_card"
    PASSPORT_PHOTO = "passport_photo"
    OTHER = "other"

@dataclass
class ClassificationResult:
    """Result of document classification"""
    document_type: DocumentType
    confidence: float
    features: Dict[str, float]
    metadata: Dict[str, any]

class DocumentClassifier:
    """
    Document classifier that identifies document types using image analysis
    and pattern recognition techniques.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the document classifier.
        
        Args:
            model_path: Path to pre-trained model (optional)
        """
        self.model_path = model_path
        self.is_trained = False
        self.feature_extractors = self._initialize_feature_extractors()
        self.classification_rules = self._initialize_classification_rules()
        
    def _initialize_feature_extractors(self) -> Dict:
        """Initialize feature extraction methods"""
        return {
            "text_density": self._calculate_text_density,
            "form_structure": self._detect_form_structure,
            "logo_detection": self._detect_logos,
            "table_detection": self._detect_tables,
            "signature_detection": self._detect_signatures,
            "photo_detection": self._detect_photos
        }
    
    def _initialize_classification_rules(self) -> Dict:
        """Initialize rule-based classification patterns"""
        return {
            DocumentType.MARKSHEET_10TH: {
                "keywords": ["class x", "10th", "tenth", "secondary", "matriculation", "board",
                           "sslc", "first puc", "i puc", "1st puc", "karnataka secondary"],
                "structure_features": ["table", "marks", "subjects"],
                "min_confidence": 0.7
            },
            DocumentType.MARKSHEET_12TH: {
                "keywords": ["class xii", "12th", "twelfth", "senior secondary", "intermediate", 
                           "puc", "pre-university", "pre university", "karnataka", "department of pre-university",
                           "second year puc", "ii puc", "2nd puc", "higher secondary", "plus two"],
                "structure_features": ["table", "marks", "subjects"],
                "min_confidence": 0.3
            },
            DocumentType.PASSING_CERTIFICATE: {
                "keywords": ["passing", "passed", "certificate", "completion", "qualify", "qualified",
                           "pre-university examination", "puc examination", "course and passed"],
                "structure_features": ["header", "signature", "seal"],
                "min_confidence": 0.4
            },
            DocumentType.TRANSFER_CERTIFICATE: {
                "keywords": ["transfer", "tc", "school leaving"],
                "structure_features": ["header", "signature", "institution"],
                "min_confidence": 0.6
            },
            DocumentType.MIGRATION_CERTIFICATE: {
                "keywords": ["migration", "university", "college"],
                "structure_features": ["header", "signature", "university_logo"],
                "min_confidence": 0.6
            },
            DocumentType.ENTRANCE_SCORECARD: {
                "keywords": ["rank", "score", "percentile", "entrance", "jee", "neet"],
                "structure_features": ["table", "scores"],
                "min_confidence": 0.8
            },
            DocumentType.ENTRANCE_ADMIT_CARD: {
                "keywords": ["admit card", "hall ticket", "entrance", "exam"],
                "structure_features": ["photo", "barcode", "table"],
                "min_confidence": 0.8
            },
            DocumentType.CASTE_CERTIFICATE: {
                "keywords": ["caste", "category", "sc", "st", "obc", "reservation"],
                "structure_features": ["government_header", "signature", "seal"],
                "min_confidence": 0.7
            },
            DocumentType.DOMICILE_CERTIFICATE: {
                "keywords": ["domicile", "residence", "resident", "state"],
                "structure_features": ["government_header", "signature", "seal"],
                "min_confidence": 0.7
            },
            DocumentType.AADHAR_CARD: {
                "keywords": ["aadhaar", "aadhar", "uid", "unique identification"],
                "structure_features": ["photo", "qr_code", "specific_layout"],
                "min_confidence": 0.9
            },
            DocumentType.PASSPORT_PHOTO: {
                "keywords": [],
                "structure_features": ["single_photo", "portrait_orientation"],
                "min_confidence": 0.8
            }
        }
    
    def classify_document(self, image_path: str, ocr_text: Optional[str] = None) -> ClassificationResult:
        """
        Classify a document from image path.
        
        Args:
            image_path: Path to document image
            ocr_text: Pre-extracted OCR text (optional, recommended for better accuracy)
            
        Returns:
            ClassificationResult containing document type and confidence
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Extract features
            features = self._extract_features(image)
            
            # Perform classification with OCR text if available
            document_type, confidence = self._classify_from_features(features, image_path, ocr_text)
            
            # Create metadata
            metadata = {
                "image_path": image_path,
                "image_size": image.shape,
                "processing_timestamp": "N/A",  # Simplified
                "used_ocr_text": ocr_text is not None
            }
            
            return ClassificationResult(
                document_type=document_type,
                confidence=confidence,
                features=features,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error classifying document {image_path}: {str(e)}")
            return ClassificationResult(
                document_type=DocumentType.OTHER,
                confidence=0.0,
                features={},
                metadata={"error": str(e)}
            )
    
    def _extract_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        Extract features from document image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Extract all features using feature extractors
        for feature_name, extractor_func in self.feature_extractors.items():
            try:
                features[feature_name] = extractor_func(image)
            except Exception as e:
                logger.warning(f"Error extracting {feature_name}: {str(e)}")
                features[feature_name] = 0.0
        
        return features
    
    def _classify_from_features(self, features: Dict[str, float], image_path: str, ocr_text: Optional[str] = None) -> Tuple[DocumentType, float]:
        """
        Classify document based on extracted features.
        
        Args:
            features: Extracted features dictionary
            image_path: Path to original image for OCR if needed
            ocr_text: Pre-extracted OCR text (preferred over re-extraction)
            
        Returns:
            Tuple of (document_type, confidence)
        """
        scores = {}
        
        # Rule-based classification
        for doc_type, rules in self.classification_rules.items():
            score = 0.0
            
            # Check structural features
            for struct_feature in rules["structure_features"]:
                if struct_feature in features:
                    score += features[struct_feature] * 0.4
            
            # Check text-based keywords using provided OCR text or fallback
            if ocr_text:
                text_score = self._check_text_patterns_from_text(ocr_text, rules["keywords"])
            else:
                text_score = self._check_text_patterns(image_path, rules["keywords"])
            score += text_score * 0.6
            
            scores[doc_type] = score
        
        # Find best match
        if not scores:
            return DocumentType.OTHER, 0.0
        
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Check minimum confidence threshold
        min_confidence = self.classification_rules[best_type]["min_confidence"]
        if best_score < min_confidence:
            return DocumentType.OTHER, best_score
        
        return best_type, best_score
    
    def _check_text_patterns_from_text(self, text: str, keywords: List[str]) -> float:
        """
        Check for text patterns in already extracted OCR text.
        
        Args:
            text: Extracted OCR text
            keywords: List of keywords to search for
            
        Returns:
            Score based on keyword matches
        """
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = 0
        
        # Define high-value keywords that should get extra weight
        high_value_keywords = [
            "puc", "pre-university", "karnataka", "department of pre-university",
            "12th", "class xii", "twelfth", "entrance", "aadhar", "aadhaar"
        ]
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check for exact match
            if keyword_lower in text_lower:
                # Give extra weight to high-value keywords
                weight = 2.0 if keyword_lower in high_value_keywords else 1.0
                matches += weight
            # Partial match for compound keywords
            elif any(word in text_lower for word in keyword_lower.split() if len(word) > 2):
                # Partial matches get half weight
                weight = 1.0 if keyword_lower in high_value_keywords else 0.5
                matches += weight
            # Fuzzy matching for slight variations
            elif self._fuzzy_match(keyword_lower, text_lower):
                matches += 0.3
        
        # Calculate score with bonus for multiple matches
        base_score = matches / len(keywords) if keywords else 0.0
        
        # Bonus for documents with multiple strong indicators
        if matches >= 3:
            base_score *= 1.2  # 20% bonus
        elif matches >= 2:
            base_score *= 1.1  # 10% bonus
            
        return min(base_score, 1.0)
    
    def _fuzzy_match(self, keyword: str, text: str) -> bool:
        """Simple fuzzy matching for slight text variations"""
        keyword_words = keyword.split()
        if len(keyword_words) == 1:
            # Check if most characters match
            keyword_chars = set(keyword.replace(" ", ""))
            text_chars = set(text.replace(" ", ""))
            common_chars = len(keyword_chars.intersection(text_chars))
            return common_chars >= len(keyword_chars) * 0.7
        else:
            # Check if most words are present
            matches = sum(1 for word in keyword_words if word in text)
            return matches >= len(keyword_words) * 0.7
    
    def _check_text_patterns(self, image_path: str, keywords: List[str]) -> float:
        """
        Check for text patterns in the document using simple OCR.
        
        Args:
            image_path: Path to image file
            keywords: List of keywords to search for
            
        Returns:
            Score based on keyword matches
        """
        try:
            # Try to use pytesseract if available, otherwise use basic image analysis
            try:
                import pytesseract
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image).lower()
            except ImportError:
                logger.info("Pytesseract not available, using basic pattern matching")
                # Use basic pattern matching based on image characteristics
                return self._basic_pattern_matching(image_path, keywords)
            
            if not keywords:
                return 0.0
            
            # Enhanced keyword matching with partial matches and fuzzy logic
            matches = 0
            text_words = text.split()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Exact match
                if keyword_lower in text:
                    matches += 1
                # Partial match for compound keywords
                elif any(word in text for word in keyword_lower.split()):
                    matches += 0.5
                # Check individual words for better matching
                elif any(keyword_word in text for keyword_word in keyword_lower.split() if len(keyword_word) > 3):
                    matches += 0.3
            
            return min(matches / len(keywords), 1.0) if keywords else 0.0
            
        except Exception as e:
            logger.warning(f"Error in text pattern matching: {str(e)}")
            return 0.0
    
    def _basic_pattern_matching(self, image_path: str, keywords: List[str]) -> float:
        """
        Basic pattern matching when OCR is not available.
        Uses image characteristics and filename patterns.
        """
        try:
            # Check filename for patterns
            filename = Path(image_path).name.lower()
            matches = sum(1 for keyword in keywords if any(word in filename for word in keyword.lower().split()))
            
            if matches > 0:
                return min(matches / len(keywords) * 0.5, 0.5)  # Lower confidence for filename-based matching
            
            return 0.1  # Minimal score for unknown documents
            
        except Exception:
            return 0.0
    
    # Feature extraction methods
    def _calculate_text_density(self, image: np.ndarray) -> float:
        """Calculate text density in the image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Count non-zero pixels (text pixels)
        text_pixels = np.count_nonzero(binary == 0)  # Black pixels are text
        total_pixels = binary.shape[0] * binary.shape[1]
        
        return text_pixels / total_pixels if total_pixels > 0 else 0.0
    
    def _detect_form_structure(self, image: np.ndarray) -> float:
        """Detect form-like structure (lines, boxes)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        h_score = np.count_nonzero(horizontal_lines) / (image.shape[0] * image.shape[1])
        v_score = np.count_nonzero(vertical_lines) / (image.shape[0] * image.shape[1])
        
        return (h_score + v_score) / 2
    
    def _detect_logos(self, image: np.ndarray) -> float:
        """Detect presence of logos or emblems"""
        # Simple approach: look for circular/rectangular shapes in upper portion
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        upper_portion = gray[:image.shape[0]//3, :]  # Top third of image
        
        # Find contours
        _, binary = cv2.threshold(upper_portion, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        logo_candidates = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 10000:  # Reasonable logo size
                logo_candidates += 1
        
        return min(logo_candidates / 3.0, 1.0)  # Normalize
    
    def _detect_tables(self, image: np.ndarray) -> float:
        """Detect table structures"""
        return self._detect_form_structure(image) * 1.2  # Enhanced form detection for tables
    
    def _detect_signatures(self, image: np.ndarray) -> float:
        """Detect handwritten signatures"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lower_portion = gray[2*image.shape[0]//3:, :]  # Bottom third
        
        # Look for irregular patterns (signatures)
        edges = cv2.Canny(lower_portion, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        signature_score = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Signature size range
                signature_score += 1
        
        return min(signature_score / 5.0, 1.0)
    
    def _detect_photos(self, image: np.ndarray) -> float:
        """Detect passport-style photos"""
        # Look for rectangular regions with face-like characteristics
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simple approach: look for rectangular regions in typical photo locations
        h, w = gray.shape
        
        # Check common photo locations (top-left, top-right, center)
        photo_regions = [
            gray[:h//3, :w//3],      # Top-left
            gray[:h//3, 2*w//3:],    # Top-right
            gray[h//4:3*h//4, w//3:2*w//3]  # Center
        ]
        
        photo_score = 0
        for region in photo_regions:
            if region.size == 0:
                continue
            
            # Check if region has photo-like characteristics
            # (uniform background with some variation for face)
            std_dev = np.std(region)
            if 20 < std_dev < 80:  # Reasonable variation for photos
                photo_score += 1
        
        return min(photo_score / 3.0, 1.0)

def create_classifier(model_path: Optional[str] = None) -> DocumentClassifier:
    """
    Factory function to create a document classifier instance.
    
    Args:
        model_path: Optional path to pre-trained model
        
    Returns:
        DocumentClassifier instance
    """
    return DocumentClassifier(model_path=model_path)