"""
Fallback OCR Module
Basic text extraction when Gemini API is unavailable
"""

import logging
from typing import Dict, Any, List
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class FallbackOCR:
    """
    Fallback OCR processor for when Gemini API is unavailable
    Uses basic text extraction methods
    """
    
    def __init__(self):
        """Initialize fallback OCR"""
        self.available = self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check if fallback OCR dependencies are available"""
        try:
            import pytesseract
            return True
        except ImportError:
            logger.warning("Tesseract not available for fallback OCR")
            return False
    
    def extract_text_basic(self, image: Image.Image, document_type: str) -> Dict[str, Any]:
        """
        Extract basic text from image using available OCR methods
        """
        if not self.available:
            return self._create_placeholder_data(document_type)
        
        try:
            import pytesseract
            
            # Convert image to text
            text = pytesseract.image_to_string(image)
            
            # Basic field extraction based on document type
            extracted_data = self._extract_fields_from_text(text, document_type)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Fallback OCR failed: {e}")
            return self._create_placeholder_data(document_type)
    
    def _extract_fields_from_text(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract fields from raw text using pattern matching
        """
        data = {}
        text_lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if document_type == 'aadhaar_card':
            data.update(self._extract_aadhaar_fields(text_lines))
        elif 'marksheet' in document_type:
            data.update(self._extract_marksheet_fields(text_lines))
        else:
            # Generic extraction for other document types
            data.update(self._extract_generic_fields(text_lines))
        
        # Add extraction metadata
        data['_extraction_method'] = 'fallback_ocr'
        data['_raw_text'] = text[:500] + "..." if len(text) > 500 else text
        
        return data
    
    def _extract_aadhaar_fields(self, lines: List[str]) -> Dict[str, Any]:
        """Extract Aadhaar card specific fields"""
        data = {}
        
        # Look for patterns in text lines
        for line in lines:
            line_lower = line.lower()
            
            # Name extraction (usually the largest text at top)
            if len(line) > 10 and any(char.isalpha() for char in line):
                if 'name' not in data:
                    data['name'] = line.strip()
            
            # Aadhaar number (12 digits with spaces)
            import re
            aadhaar_match = re.search(r'\b\d{4}\s*\d{4}\s*\d{4}\b', line)
            if aadhaar_match:
                data['aadhaar_number'] = aadhaar_match.group().replace(' ', '')
            
            # Date of birth
            dob_match = re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', line)
            if dob_match:
                data['date_of_birth'] = dob_match.group()
        
        return data
    
    def _extract_marksheet_fields(self, lines: List[str]) -> Dict[str, Any]:
        """Extract marksheet specific fields"""
        data = {}
        
        for line in lines:
            line_lower = line.lower()
            
            # Student name (often appears after "name" keyword)
            if 'name' in line_lower and len(line) > 10:
                data['student_name'] = line.replace('name', '').replace(':', '').strip()
            
            # Roll number
            import re
            roll_match = re.search(r'roll\s*(?:no|number)?[:\s]*([A-Z0-9]+)', line_lower)
            if roll_match:
                data['roll_number'] = roll_match.group(1)
            
            # Year
            year_match = re.search(r'\b(20\d{2})\b', line)
            if year_match:
                data['year'] = year_match.group(1)
        
        return data
    
    def _extract_generic_fields(self, lines: List[str]) -> Dict[str, Any]:
        """Generic field extraction for unknown document types"""
        data = {}
        
        # Extract potential names (lines with alphabetic characters)
        names = [line for line in lines if len(line) > 5 and any(char.isalpha() for char in line)]
        if names:
            data['extracted_text_lines'] = names[:3]  # First 3 text lines
        
        # Extract numbers
        import re
        numbers = []
        for line in lines:
            number_matches = re.findall(r'\b\d{4,}\b', line)
            numbers.extend(number_matches)
        
        if numbers:
            data['extracted_numbers'] = numbers[:5]  # First 5 numbers
        
        return data
    
    def _create_placeholder_data(self, document_type: str) -> Dict[str, Any]:
        """Create placeholder data when OCR is not available"""
        return {
            '_extraction_status': 'fallback_unavailable',
            '_message': 'Fallback OCR not available. Please install tesseract-ocr or upgrade Gemini API plan.',
            '_suggested_action': 'Install tesseract: pip install pytesseract',
            'document_type': document_type
        }

def create_fallback_ocr() -> FallbackOCR:
    """Factory function to create fallback OCR"""
    return FallbackOCR()