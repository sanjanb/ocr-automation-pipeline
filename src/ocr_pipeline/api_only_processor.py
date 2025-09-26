"""
API-Only Document Processor
A lightweight document processing system that uses only APIs for OCR and extraction.
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# API integrations
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Gemini not available. Install google-generativeai")

try:
    import requests
    from PIL import Image
    import base64
    from io import BytesIO
    API_DEPS_AVAILABLE = True
except ImportError:
    API_DEPS_AVAILABLE = False
    logging.warning("API dependencies not available")

logger = logging.getLogger(__name__)

@dataclass
class DocumentResult:
    """Result from document processing"""
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    confidence: float
    processing_time: float
    method_used: str
    error_message: str = ""
    metadata: Dict[str, Any] = None

class APIOnlyDocumentProcessor:
    """
    Lightweight document processor using only APIs:
    1. OCR.space API for text extraction (free tier available)
    2. Gemini API for structured extraction
    """
    
    def __init__(self, gemini_api_key: str = None, ocr_space_api_key: str = None):
        """Initialize API-only document processor"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
        if not self.gemini_api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable.")
        
        # Initialize OCR.space API (free alternative to heavy OCR libraries)
        self.ocr_space_api_key = ocr_space_api_key or os.getenv("OCR_SPACE_API_KEY")
        
        # Configure Gemini
        if GEMINI_AVAILABLE:
            genai.configure(api_key=self.gemini_api_key)
            
            # Try different models
            model_options = [
                'models/gemini-2.5-flash',
                'models/gemini-1.5-flash', 
                'models/gemini-pro-latest'
            ]
            
            self.gemini_model = None
            for model_name in model_options:
                try:
                    self.gemini_model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    self.logger.info(f"Gemini model initialized: {model_name}")
                    break
                except Exception as e:
                    self.logger.warning(f"Failed to initialize {model_name}: {e}")
                    continue
                    
            if not self.gemini_model:
                raise ValueError("Failed to initialize any Gemini model")
        else:
            raise ValueError("Gemini API not available")
        
        self.logger.info("API-only document processor initialized")
    
    def process_document(self, image_path: str, document_type_hint: str = None) -> DocumentResult:
        """
        Process document using API-only approach
        
        Args:
            image_path: Path to document image
            document_type_hint: Hint about document type
            
        Returns:
            DocumentResult with extracted information
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing document: {image_path}")
            
            # Step 1: Extract text using API
            ocr_text = self._extract_text_via_api(image_path)
            if not ocr_text:
                return DocumentResult(
                    success=False,
                    document_type="unknown",
                    extracted_data={},
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    method_used="api_only",
                    error_message="Failed to extract text from document"
                )
            
            # Step 2: Classify document type if not provided
            if not document_type_hint:
                document_type_hint = self._classify_document_type(ocr_text)
            
            # Step 3: Extract structured data using Gemini
            extraction_result = self._extract_with_gemini(ocr_text, document_type_hint)
            
            processing_time = time.time() - start_time
            
            return DocumentResult(
                success=bool(extraction_result),
                document_type=document_type_hint,
                extracted_data=extraction_result or {},
                confidence=self._calculate_confidence(extraction_result, ocr_text),
                processing_time=processing_time,
                method_used="api_only",
                metadata={
                    "ocr_text_length": len(ocr_text),
                    "gemini_model": self.model_name,
                    "document_type": document_type_hint
                }
            )
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            return DocumentResult(
                success=False,
                document_type="unknown",
                extracted_data={},
                confidence=0.0,
                processing_time=time.time() - start_time,
                method_used="api_only",
                error_message=str(e)
            )
    
    def _extract_text_via_api(self, image_path: str) -> Optional[str]:
        """Extract text using OCR.space API (free) or fallback to base64 + Gemini"""
        
        # Method 1: Try OCR.space API if key available
        if self.ocr_space_api_key:
            try:
                return self._ocr_space_extract(image_path)
            except Exception as e:
                self.logger.warning(f"OCR.space failed: {e}, trying Gemini vision")
        
        # Method 2: Use Gemini vision capabilities
        try:
            return self._gemini_vision_extract(image_path)
        except Exception as e:
            self.logger.error(f"Gemini vision failed: {e}")
            return None
    
    def _ocr_space_extract(self, image_path: str) -> str:
        """Extract text using OCR.space API"""
        url = "https://api.ocr.space/parse/image"
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'apikey': self.ocr_space_api_key,
                'language': 'eng',
                'isTable': 'true',  # Better for structured documents
                'OCREngine': '2',   # Use engine 2 for better accuracy
            }
            
            response = requests.post(url, files=files, data=data)
            result = response.json()
            
            if result.get('ParsedResults'):
                return result['ParsedResults'][0]['ParsedText']
            else:
                raise Exception(f"OCR.space error: {result.get('ErrorMessage', 'Unknown error')}")
    
    def _gemini_vision_extract(self, image_path: str) -> str:
        """Extract text using Gemini vision capabilities"""
        # Load and prepare image
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create OCR prompt
        prompt = """
        Please extract ALL text from this document image. 
        Preserve the original formatting and structure as much as possible.
        Include all numbers, names, dates, and other details exactly as they appear.
        Return only the extracted text, no explanations.
        """
        
        # Send to Gemini
        response = self.gemini_model.generate_content([prompt, image])
        
        if response and response.text:
            return response.text.strip()
        else:
            raise Exception("No text extracted by Gemini vision")
    
    def _classify_document_type(self, text: str) -> str:
        """Classify document type using Gemini"""
        prompt = f"""
        Based on this OCR text from a document, identify the document type.
        
        Choose from these options:
        - marksheet_10th
        - marksheet_12th  
        - entrance_scorecard
        - admit_card
        - caste_certificate
        - aadhar_card
        - transfer_certificate
        - migration_certificate
        - domicile_certificate
        - other
        
        Text: {text[:500]}...
        
        Return only the document type, no explanation.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            if response and response.text:
                doc_type = response.text.strip().lower()
                return doc_type if doc_type in [
                    'marksheet_10th', 'marksheet_12th', 'entrance_scorecard', 
                    'admit_card', 'caste_certificate', 'aadhar_card',
                    'transfer_certificate', 'migration_certificate', 'domicile_certificate'
                ] else 'marksheet_12th'  # default
        except Exception as e:
            self.logger.warning(f"Document classification failed: {e}")
        
        return 'marksheet_12th'  # default fallback
    
    def _extract_with_gemini(self, text: str, document_type: str) -> Optional[Dict[str, Any]]:
        """Extract structured data using Gemini"""
        prompt = self._create_extraction_prompt(text, document_type)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            if response and response.text:
                return self._parse_json_response(response.text)
        except Exception as e:
            self.logger.error(f"Gemini extraction failed: {e}")
        
        return None
    
    def _create_extraction_prompt(self, text: str, document_type: str) -> str:
        """Create document-specific extraction prompt"""
        
        base_prompt = """
Extract structured information from this document text and return as valid JSON.
IMPORTANT: Return ONLY the JSON object, no explanations.
Use null for missing fields, don't make up data.
"""
        
        # Document-specific schemas
        schemas = {
            "marksheet_10th": {
                "student_name": "string",
                "father_name": "string", 
                "mother_name": "string",
                "roll_number": "string",
                "board": "string",
                "school_name": "string",
                "passing_year": "string",
                "subjects": "object with subject:marks pairs",
                "total_marks": "number",
                "percentage": "number",
                "result": "string"
            },
            "marksheet_12th": {
                "student_name": "string",
                "father_name": "string",
                "roll_number": "string", 
                "board": "string",
                "stream": "string",
                "passing_year": "string",
                "subjects": "object",
                "total_marks": "number",
                "percentage": "number"
            },
            "entrance_scorecard": {
                "candidate_name": "string",
                "roll_number": "string",
                "exam_name": "string",
                "total_score": "number",
                "percentile": "number",
                "rank": "number"
            },
            "aadhar_card": {
                "name": "string",
                "aadhar_number": "string",
                "date_of_birth": "string",
                "address": "string"
            }
        }
        
        schema = schemas.get(document_type, schemas["marksheet_12th"])
        
        return f"""
{base_prompt}

Expected JSON structure for {document_type}:
{json.dumps(schema, indent=2)}

Document text:
{text}

JSON:"""
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse Gemini JSON response"""
        try:
            # Find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = response_text[start:end+1]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"JSON parsing failed: {e}")
        
        return None
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], text: str) -> float:
        """Calculate extraction confidence"""
        if not extracted_data:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Bonus for number of fields
        field_count = len([v for v in extracted_data.values() if v])
        if field_count >= 5:
            confidence += 0.3
        elif field_count >= 3:
            confidence += 0.2
        
        # Bonus for key fields
        key_fields = ['student_name', 'name', 'candidate_name', 'roll_number']
        if any(field in extracted_data and extracted_data[field] for field in key_fields):
            confidence += 0.2
        
        return min(confidence, 1.0)

# Factory function
def create_api_only_processor(gemini_api_key: str = None, ocr_space_api_key: str = None) -> APIOnlyDocumentProcessor:
    """Create API-only document processor"""
    return APIOnlyDocumentProcessor(gemini_api_key=gemini_api_key, ocr_space_api_key=ocr_space_api_key)