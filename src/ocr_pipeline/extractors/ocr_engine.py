"""
OCR Engine Module for OCR Automation Pipeline
MIT Hackathon Project

This module provides multiple OCR engines (Tesseract, EasyOCR, PaddleOCR)
with preprocessing capabilities for optimal text extraction.
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from pathlib import Path
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from PIL import Image
import json

# Import OCR libraries
import pytesseract
import easyocr
# Note: PaddleOCR import will be handled conditionally

logger = logging.getLogger(__name__)

class OCREngine(Enum):
    """Available OCR engines"""
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"

@dataclass
class OCRResult:
    """Result from OCR processing"""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]
    word_confidences: List[float]
    engine_used: OCREngine
    processing_time: float
    metadata: Dict[str, any]

class ImagePreprocessor:
    """Image preprocessing for better OCR results"""
    
    @staticmethod
    def preprocess_image(image: np.ndarray, 
                        enhance_contrast: bool = True,
                        denoise: bool = True,
                        deskew: bool = True,
                        resize_factor: Optional[float] = None) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image as numpy array
            enhance_contrast: Whether to enhance contrast
            denoise: Whether to apply denoising
            deskew: Whether to correct skew
            resize_factor: Optional resize factor
            
        Returns:
            Preprocessed image
        """
        processed = image.copy()
        
        # Convert to grayscale if needed
        if len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        
        # Resize if specified
        if resize_factor and resize_factor != 1.0:
            height, width = processed.shape
            new_height = int(height * resize_factor)
            new_width = int(width * resize_factor)
            processed = cv2.resize(processed, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Denoise
        if denoise:
            processed = cv2.fastNlMeansDenoising(processed)
        
        # Enhance contrast
        if enhance_contrast:
            processed = cv2.equalizeHist(processed)
        
        # Deskew
        if deskew:
            processed = ImagePreprocessor._deskew_image(processed)
        
        # Apply adaptive threshold for better text detection
        processed = cv2.adaptiveThreshold(
            processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return processed
    
    @staticmethod
    def _deskew_image(image: np.ndarray) -> np.ndarray:
        """Correct skewed text in image"""
        try:
            # Find contours to detect text lines
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours that might be text
            text_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 10000:  # Reasonable text size
                    text_contours.append(contour)
            
            if not text_contours:
                return image
            
            # Find the dominant angle
            angles = []
            for contour in text_contours:
                rect = cv2.minAreaRect(contour)
                angle = rect[2]
                if angle < -45:
                    angle += 90
                angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                
                # Rotate image to correct skew
                if abs(median_angle) > 0.5:  # Only correct if significant skew
                    height, width = image.shape
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    corrected = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    return corrected
            
            return image
            
        except Exception as e:
            logger.warning(f"Error in deskewing: {str(e)}")
            return image

class BaseOCREngine(ABC):
    """Abstract base class for OCR engines"""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.preprocessor = ImagePreprocessor()
    
    @abstractmethod
    def extract_text(self, image: Union[np.ndarray, str], preprocess: bool = True) -> OCRResult:
        """Extract text from image"""
        pass
    
    def preprocess_image(self, image: Union[np.ndarray, str]) -> np.ndarray:
        """Preprocess image before OCR"""
        if isinstance(image, str):
            img_array = cv2.imread(image)
            if img_array is None:
                raise ValueError(f"Could not load image from {image}")
        else:
            img_array = image
        
        return self.preprocessor.preprocess_image(img_array)

class TesseractEngine(BaseOCREngine):
    """Tesseract OCR Engine implementation"""
    
    def __init__(self, language: str = "eng", 
                 config: str = "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "):
        super().__init__(language)
        self.config = config
        
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.error(f"Tesseract not available: {str(e)}")
            raise
    
    def extract_text(self, image: Union[np.ndarray, str], preprocess: bool = True) -> OCRResult:
        """Extract text using Tesseract"""
        import time
        start_time = time.time()
        
        try:
            # Load and preprocess image
            if isinstance(image, str):
                img_array = cv2.imread(image)
                if img_array is None:
                    raise ValueError(f"Could not load image from {image}")
            else:
                img_array = image
            
            if preprocess:
                processed_img = self.preprocess_image(img_array)
            else:
                processed_img = img_array
            
            # Convert to PIL Image for Tesseract
            pil_image = Image.fromarray(processed_img)
            
            # Extract text
            text = pytesseract.image_to_string(pil_image, lang=self.language, config=self.config)
            
            # Get detailed data
            data = pytesseract.image_to_data(pil_image, lang=self.language, 
                                           config=self.config, output_type=pytesseract.Output.DICT)
            
            # Calculate overall confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            overall_confidence = np.mean(confidences) / 100.0 if confidences else 0.0
            
            # Extract bounding boxes
            bounding_boxes = []
            word_confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Only include confident detections
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    bounding_boxes.append((x, y, x+w, y+h))
                    word_confidences.append(int(data['conf'][i]) / 100.0)
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=text.strip(),
                confidence=overall_confidence,
                bounding_boxes=bounding_boxes,
                word_confidences=word_confidences,
                engine_used=OCREngine.TESSERACT,
                processing_time=processing_time,
                metadata={
                    "language": self.language,
                    "config": self.config,
                    "total_words": len([t for t in data['text'] if t.strip()])
                }
            )
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            processing_time = time.time() - start_time
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_boxes=[],
                word_confidences=[],
                engine_used=OCREngine.TESSERACT,
                processing_time=processing_time,
                metadata={"error": str(e)}
            )

class EasyOCREngine(BaseOCREngine):
    """EasyOCR Engine implementation"""
    
    def __init__(self, languages: List[str] = ['en'], gpu: bool = False):
        super().__init__(languages[0])
        self.languages = languages
        self.gpu = gpu
        
        # Initialize EasyOCR reader
        try:
            self.reader = easyocr.Reader(languages, gpu=gpu)
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}")
            raise
    
    def extract_text(self, image: Union[np.ndarray, str], preprocess: bool = True) -> OCRResult:
        """Extract text using EasyOCR"""
        import time
        start_time = time.time()
        
        try:
            # Load and preprocess image
            if isinstance(image, str):
                img_array = cv2.imread(image)
                if img_array is None:
                    raise ValueError(f"Could not load image from {image}")
            else:
                img_array = image
            
            if preprocess:
                processed_img = self.preprocess_image(img_array)
            else:
                processed_img = img_array
            
            # Run EasyOCR
            results = self.reader.readtext(processed_img)
            
            # Parse results
            text_parts = []
            bounding_boxes = []
            word_confidences = []
            
            for (bbox, text, confidence) in results:
                text_parts.append(text)
                
                # Convert bbox to standard format
                bbox_array = np.array(bbox)
                x_min, y_min = bbox_array.min(axis=0)
                x_max, y_max = bbox_array.max(axis=0)
                bounding_boxes.append((int(x_min), int(y_min), int(x_max), int(y_max)))
                
                word_confidences.append(confidence)
            
            # Combine text
            full_text = ' '.join(text_parts)
            overall_confidence = np.mean(word_confidences) if word_confidences else 0.0
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=full_text,
                confidence=overall_confidence,
                bounding_boxes=bounding_boxes,
                word_confidences=word_confidences,
                engine_used=OCREngine.EASYOCR,
                processing_time=processing_time,
                metadata={
                    "languages": self.languages,
                    "gpu_used": self.gpu,
                    "total_detections": len(results)
                }
            )
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {str(e)}")
            processing_time = time.time() - start_time
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_boxes=[],
                word_confidences=[],
                engine_used=OCREngine.EASYOCR,
                processing_time=processing_time,
                metadata={"error": str(e)}
            )

class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR Engine implementation"""
    
    def __init__(self, language: str = "en", use_gpu: bool = False):
        super().__init__(language)
        self.use_gpu = use_gpu
        
        # Initialize PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.ocr_engine = PaddleOCR(use_angle_cls=True, lang=language, use_gpu=use_gpu)
        except ImportError:
            logger.error("PaddleOCR not available. Please install PaddleOCR.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            raise
    
    def extract_text(self, image: Union[np.ndarray, str], preprocess: bool = True) -> OCRResult:
        """Extract text using PaddleOCR"""
        import time
        start_time = time.time()
        
        try:
            # Load and preprocess image
            if isinstance(image, str):
                img_array = cv2.imread(image)
                if img_array is None:
                    raise ValueError(f"Could not load image from {image}")
            else:
                img_array = image
            
            if preprocess:
                processed_img = self.preprocess_image(img_array)
            else:
                processed_img = img_array
            
            # Run PaddleOCR
            results = self.ocr_engine.ocr(processed_img, cls=True)
            
            # Parse results
            text_parts = []
            bounding_boxes = []
            word_confidences = []
            
            if results[0]:  # Check if any text was detected
                for line in results[0]:
                    bbox, (text, confidence) = line
                    text_parts.append(text)
                    
                    # Convert bbox to standard format
                    bbox_array = np.array(bbox)
                    x_min, y_min = bbox_array.min(axis=0)
                    x_max, y_max = bbox_array.max(axis=0)
                    bounding_boxes.append((int(x_min), int(y_min), int(x_max), int(y_max)))
                    
                    word_confidences.append(confidence)
            
            # Combine text
            full_text = ' '.join(text_parts)
            overall_confidence = np.mean(word_confidences) if word_confidences else 0.0
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=full_text,
                confidence=overall_confidence,
                bounding_boxes=bounding_boxes,
                word_confidences=word_confidences,
                engine_used=OCREngine.PADDLEOCR,
                processing_time=processing_time,
                metadata={
                    "language": self.language,
                    "gpu_used": self.use_gpu,
                    "total_lines": len(results[0]) if results[0] else 0
                }
            )
            
        except Exception as e:
            logger.error(f"PaddleOCR failed: {str(e)}")
            processing_time = time.time() - start_time
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_boxes=[],
                word_confidences=[],
                engine_used=OCREngine.PADDLEOCR,
                processing_time=processing_time,
                metadata={"error": str(e)}
            )

class MultiEngineOCR:
    """
    OCR system that can use multiple engines and combine results
    """
    
    def __init__(self, engines: Optional[List[OCREngine]] = None):
        """
        Initialize multi-engine OCR system.
        
        Args:
            engines: List of engines to use (default: all available)
        """
        if engines is None:
            engines = [OCREngine.TESSERACT, OCREngine.EASYOCR]  # Default engines
        
        self.engines = {}
        self.engine_order = engines
        
        # Initialize requested engines
        for engine in engines:
            try:
                if engine == OCREngine.TESSERACT:
                    self.engines[engine] = TesseractEngine()
                elif engine == OCREngine.EASYOCR:
                    self.engines[engine] = EasyOCREngine()
                elif engine == OCREngine.PADDLEOCR:
                    self.engines[engine] = PaddleOCREngine()
            except Exception as e:
                logger.warning(f"Could not initialize {engine.value}: {str(e)}")
        
        if not self.engines:
            raise RuntimeError("No OCR engines could be initialized")
    
    def extract_text(self, 
                    image: Union[np.ndarray, str], 
                    engine: Optional[OCREngine] = None,
                    use_best_result: bool = True) -> OCRResult:
        """
        Extract text using specified engine or best available.
        
        Args:
            image: Input image or image path
            engine: Specific engine to use (None for automatic selection)
            use_best_result: Whether to return the best result from multiple engines
            
        Returns:
            OCRResult with extracted text
        """
        if engine and engine in self.engines:
            return self.engines[engine].extract_text(image)
        
        if use_best_result and len(self.engines) > 1:
            return self._get_best_result(image)
        
        # Use first available engine
        first_engine = next(iter(self.engines.values()))
        return first_engine.extract_text(image)
    
    def _get_best_result(self, image: Union[np.ndarray, str]) -> OCRResult:
        """
        Run multiple engines and return the best result based on confidence.
        
        Args:
            image: Input image
            
        Returns:
            Best OCR result
        """
        results = []
        
        for engine_type, engine in self.engines.items():
            try:
                result = engine.extract_text(image)
                results.append(result)
            except Exception as e:
                logger.warning(f"Engine {engine_type.value} failed: {str(e)}")
        
        if not results:
            raise RuntimeError("All OCR engines failed")
        
        # Return result with highest confidence
        best_result = max(results, key=lambda r: r.confidence)
        
        # Add metadata about other results
        best_result.metadata['alternative_results'] = [
            {
                'engine': r.engine_used.value,
                'confidence': r.confidence,
                'text_length': len(r.text)
            }
            for r in results if r != best_result
        ]
        
        return best_result
    
    def get_available_engines(self) -> List[OCREngine]:
        """Get list of available engines"""
        return list(self.engines.keys())

def create_ocr_engine(engine_type: OCREngine = OCREngine.TESSERACT, **kwargs) -> BaseOCREngine:
    """
    Factory function to create an OCR engine instance.
    
    Args:
        engine_type: Type of OCR engine to create
        **kwargs: Additional arguments for engine initialization
        
    Returns:
        Initialized OCR engine
    """
    if engine_type == OCREngine.TESSERACT:
        return TesseractEngine(**kwargs)
    elif engine_type == OCREngine.EASYOCR:
        return EasyOCREngine(**kwargs)
    elif engine_type == OCREngine.PADDLEOCR:
        return PaddleOCREngine(**kwargs)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")

def create_multi_engine_ocr(engines: Optional[List[OCREngine]] = None) -> MultiEngineOCR:
    """
    Factory function to create a multi-engine OCR system.
    
    Args:
        engines: List of engines to use
        
    Returns:
        MultiEngineOCR instance
    """
    return MultiEngineOCR(engines)