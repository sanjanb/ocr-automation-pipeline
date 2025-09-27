"""
Core Processor Module
Gemini-based document processing with direct image-to-JSON extraction
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from dataclasses import dataclass
from datetime import datetime

try:
    import google.generativeai as genai
    from PIL import Image
except ImportError as e:
    raise ImportError(f"Required packages missing. Install with: pip install google-generativeai pillow") from e

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result from document processing"""
    success: bool
    document_type: str
    extracted_data: Dict[str, Any]
    processing_time: float
    validation_issues: List[str]
    confidence_score: float
    error_message: str = ""
    metadata: Dict[str, Any] = None

class DocumentProcessor:
    """
    AI-powered document processor using Gemini models
    Handles direct image-to-JSON extraction without separate OCR
    """
    
    def __init__(self, api_key: str = None, model_name: str = None):
        """Initialize document processor"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model with fallbacks
        model_options = [
            model_name,
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro-vision'
        ] if model_name else [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash', 
            'gemini-1.5-pro',
            'gemini-pro-vision'
        ]
        
        self.model = None
        self.model_name = None
        
        for model_option in model_options:
            if not model_option:
                continue
            try:
                self.model = genai.GenerativeModel(model_option)
                self.model_name = model_option
                logger.info(f"Initialized Gemini model: {model_option}")
                break
            except Exception as e:
                logger.warning(f"Failed to initialize {model_option}: {e}")
        
        if not self.model:
            raise ValueError("Failed to initialize any Gemini model")
    
    async def process_document_async(self, image_path: str, document_type: str = None) -> ProcessingResult:
        """Async version of document processing"""
        return self.process_document(image_path, document_type)
    
    def process_document(self, image_path: str, document_type: str = None) -> ProcessingResult:
        """
        Process document image with Gemini
        
        Args:
            image_path: Path to document image
            document_type: Optional hint about document type
            
        Returns:
            ProcessingResult with extracted data and validation
        """
        start_time = time.time()
        
        try:
            # Determine file type and prepare for processing
            file_path = Path(image_path)
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.pdf':
                # For PDF files, upload directly to Gemini
                document_data = self._prepare_pdf_for_gemini(image_path)
                
                # Auto-detect document type if not provided
                if not document_type:
                    document_type = self._detect_document_type_pdf(document_data)
                
                # Extract data using Gemini for PDF
                extracted_data = self._extract_with_gemini_pdf(document_data, document_type)
                
                metadata = {
                    'file_type': 'pdf',
                    'file_size': file_path.stat().st_size,
                    'fields_extracted': len(extracted_data)
                }
            else:
                # For image files, use existing logic
                image = Image.open(image_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Auto-detect document type if not provided
                if not document_type:
                    document_type = self._detect_document_type(image)
                
                # Extract data using Gemini
                extracted_data = self._extract_with_gemini(image, document_type)
                
                metadata = {
                    'file_type': 'image',
                    'image_size': image.size,
                    'image_mode': image.mode,
                    'fields_extracted': len(extracted_data)
                }
            
            # Validate extracted data
            validation_issues = self._validate_data(extracted_data, document_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(extracted_data, validation_issues)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                document_type=document_type,
                extracted_data=extracted_data,
                processing_time=processing_time,
                validation_issues=validation_issues,
                confidence_score=confidence,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return ProcessingResult(
                success=False,
                document_type=document_type or "unknown",
                extracted_data={},
                processing_time=time.time() - start_time,
                validation_issues=[],
                confidence_score=0.0,
                error_message=str(e)
            )
    
    def _detect_document_type(self, image: Image.Image) -> str:
        """Auto-detect document type using Gemini"""
        detection_prompt = """
        Analyze this document image and identify its type.
        
        Choose from these options:
        - aadhaar_card
        - marksheet_10th
        - marksheet_12th
        - transfer_certificate
        - migration_certificate
        - entrance_scorecard
        - admit_card
        - caste_certificate
        - domicile_certificate
        - passport_photo
        - other
        
        Return only the document type, nothing else.
        """
        
        try:
            response = self.model.generate_content([detection_prompt, image])
            if response and response.text:
                doc_type = response.text.strip().lower()
                supported_types = {
                    'aadhaar_card', 'marksheet_10th', 'marksheet_12th', 
                    'transfer_certificate', 'migration_certificate', 'entrance_scorecard',
                    'admit_card', 'caste_certificate', 'domicile_certificate', 'passport_photo'
                }
                return doc_type if doc_type in supported_types else 'other'
        except Exception as e:
            logger.warning(f"Document type detection failed: {e}")
        
        return 'other'
    
    def _extract_with_gemini(self, image: Image.Image, document_type: str) -> Dict[str, Any]:
        """Extract structured data using Gemini"""
        schema = self._get_document_schema(document_type)
        prompt = self._create_extraction_prompt(document_type, schema)
        
        try:
            response = self.model.generate_content([prompt, image])
            if response and response.text:
                return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            raise Exception(f"Failed to extract data: {e}")
        
        return {}
    
    def _get_document_schema(self, document_type: str) -> Dict[str, Any]:
        """Get schema for document type"""
        from .schemas import DOCUMENT_SCHEMAS
        return DOCUMENT_SCHEMAS.get(document_type, DOCUMENT_SCHEMAS['default'])
    
    def _create_extraction_prompt(self, document_type: str, schema: Dict[str, Any]) -> str:
        """Create extraction prompt for document type"""
        required_fields = schema.get('required_fields', [])
        optional_fields = schema.get('optional_fields', [])
        
        prompt = f"""
Extract structured information from this {document_type.replace('_', ' ')} document image.

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON, no explanations or markdown
2. Use exact field names as specified
3. Use null for missing information, don't make up data
4. Extract text exactly as it appears

REQUIRED FIELDS:
{json.dumps(required_fields, indent=2)}

OPTIONAL FIELDS (extract if available):
{json.dumps(optional_fields, indent=2)}

EXAMPLE OUTPUT FORMAT:
{{
  "field_name": "extracted_value",
  "another_field": null,
  "numeric_field": 123
}}

Extract the data now:"""
        
        return prompt
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini JSON response"""
        try:
            # Find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = response_text[start:end+1]
                return json.loads(json_str)
            else:
                return json.loads(response_text.strip())
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            raise Exception(f"Failed to parse JSON response: {e}")
    
    def _validate_data(self, data: Dict[str, Any], document_type: str) -> List[str]:
        """Validate extracted data"""
        schema = self._get_document_schema(document_type)
        issues = []
        
        required_fields = schema.get('required_fields', [])
        validation_rules = schema.get('validation_rules', {})
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                issues.append(f"Missing required field: {field}")
        
        # Check validation rules
        for field, rule in validation_rules.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                if 'year' in rule and 'digit' in rule:
                    if not (isinstance(value, (int, str)) and len(str(value)) == 4):
                        issues.append(f"{field} should be 4-digit year, got: {value}")
                
                elif 'digits' in rule:
                    expected_length = int(''.join(filter(str.isdigit, rule)))
                    cleaned_value = str(value).replace(' ', '').replace('-', '')
                    if len(cleaned_value) != expected_length:
                        issues.append(f"{field} should be {expected_length} digits, got: {value}")
        
        return issues
    
    def _prepare_pdf_for_gemini(self, pdf_path: str):
        """Prepare PDF file for Gemini processing"""
        try:
            # Upload PDF to Gemini
            file_part = genai.upload_file(pdf_path)
            return file_part
        except Exception as e:
            logger.error(f"Failed to prepare PDF for Gemini: {e}")
            raise
    
    def _detect_document_type_pdf(self, pdf_data) -> str:
        """Auto-detect document type for PDF using Gemini"""
        detection_prompt = """
        Analyze this PDF document and identify its type.
        
        Choose from these options:
        - aadhaar_card
        - marksheet_10th
        - marksheet_12th
        - transfer_certificate
        - migration_certificate
        - entrance_scorecard
        - admit_card
        - caste_certificate
        - domicile_certificate
        - passport_photo
        - other
        
        Return only the document type, nothing else.
        """
        
        try:
            response = self.model.generate_content([detection_prompt, pdf_data])
            if response and response.text:
                doc_type = response.text.strip().lower()
                supported_types = {
                    'aadhaar_card', 'marksheet_10th', 'marksheet_12th', 
                    'transfer_certificate', 'migration_certificate', 'entrance_scorecard',
                    'admit_card', 'caste_certificate', 'domicile_certificate', 'passport_photo'
                }
                return doc_type if doc_type in supported_types else 'other'
        except Exception as e:
            logger.warning(f"PDF document type detection failed: {e}")
        
        return 'other'
    
    def _extract_with_gemini_pdf(self, pdf_data, document_type: str) -> Dict[str, Any]:
        """Extract structured data from PDF using Gemini"""
        schema = self._get_document_schema(document_type)
        prompt = self._create_extraction_prompt(document_type, schema)
        
        try:
            response = self.model.generate_content([prompt, pdf_data])
            if response and response.text:
                # Clean and parse JSON response
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                
                return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response for PDF: {e}")
            logger.debug(f"Raw response: {response.text if response else 'None'}")
        except Exception as e:
            logger.error(f"Gemini PDF extraction failed: {e}")
        
        return {}
    
    def _calculate_confidence(self, data: Dict[str, Any], validation_issues: List[str]) -> float:
        """Calculate confidence score"""
        if not data:
            return 0.0
        
        base_confidence = 0.7
        
        # Bonus for extracted fields
        field_count = len([v for v in data.values() if v is not None and v != ""])
        if field_count >= 5:
            base_confidence += 0.2
        elif field_count >= 3:
            base_confidence += 0.1
        
        # Penalty for validation issues
        penalty = len(validation_issues) * 0.1
        
        return max(0.0, min(1.0, base_confidence - penalty))

def create_processor(api_key: str = None, model_name: str = None) -> DocumentProcessor:
    """Factory function to create processor"""
    return DocumentProcessor(api_key=api_key, model_name=model_name)