"""
Simple Document Processor using Gemini 1.5 Flash
Direct image → JSON extraction without separate OCR step
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
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

class GeminiDocumentProcessor:
    """
    Simple document processor using Gemini 1.5 Flash multimodal capabilities
    No separate OCR needed - Gemini reads images directly
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Gemini processor"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model - try the latest available models
        model_options = [
            'models/gemini-2.0-flash',
            'models/gemini-1.5-flash-latest',
            'models/gemini-1.5-flash', 
            'models/gemini-1.5-pro-latest',
            'models/gemini-1.5-pro'
        ]
        
        self.model = None
        for model_name in model_options:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                logger.info(f"Initialized Gemini model: {model_name}")
                break
            except Exception as e:
                logger.warning(f"Failed to initialize {model_name}: {e}")
        
        if not self.model:
            raise ValueError("Failed to initialize any Gemini model")
    
    def process_document(self, image_path: str, document_type: str = None) -> ProcessingResult:
        """
        Process document image directly with Gemini
        
        Args:
            image_path: Path to document image
            document_type: Optional hint about document type
            
        Returns:
            ProcessingResult with extracted data
        """
        start_time = time.time()
        
        try:
            # Load and prepare image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Auto-detect document type if not provided
            if not document_type:
                document_type = self._detect_document_type(image)
            
            # Get extraction schema for this document type
            schema = self._get_document_schema(document_type)
            
            # Create extraction prompt
            prompt = self._create_extraction_prompt(document_type, schema)
            
            # Send to Gemini for processing
            response = self.model.generate_content([prompt, image])
            
            if not response or not response.text:
                raise Exception("No response from Gemini")
            
            # Parse JSON response
            extracted_data = self._parse_response(response.text)
            
            # Validate extracted data
            validation_issues = self._validate_data(extracted_data, schema)
            
            # Calculate confidence
            confidence = self._calculate_confidence(extracted_data, validation_issues)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                document_type=document_type,
                extracted_data=extracted_data,
                processing_time=processing_time,
                validation_issues=validation_issues,
                confidence_score=confidence
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
                # Validate it's one of our supported types
                supported_types = {
                    'aadhaar_card', 'marksheet_10th', 'marksheet_12th', 
                    'transfer_certificate', 'migration_certificate', 'entrance_scorecard',
                    'admit_card', 'caste_certificate', 'domicile_certificate', 'passport_photo'
                }
                return doc_type if doc_type in supported_types else 'other'
        except Exception as e:
            logger.warning(f"Document type detection failed: {e}")
        
        return 'other'
    
    def _get_document_schema(self, document_type: str) -> Dict[str, Any]:
        """Get required fields schema for document type"""
        schemas = {
            'aadhaar_card': {
                'required_fields': ['name', 'aadhaar_number', 'date_of_birth', 'address'],
                'optional_fields': ['father_name', 'gender'],
                'validation_rules': {
                    'aadhaar_number': 'must be 12 digits',
                    'date_of_birth': 'DD-MM-YYYY or DD/MM/YYYY format'
                }
            },
            'marksheet_10th': {
                'required_fields': ['student_name', 'roll_number', 'board_name', 'passing_year', 'subjects_marks'],
                'optional_fields': ['father_name', 'mother_name', 'school_name', 'total_marks', 'percentage'],
                'validation_rules': {
                    'passing_year': 'must be 4-digit year',
                    'subjects_marks': 'object with subject names as keys and marks as values'
                }
            },
            'marksheet_12th': {
                'required_fields': ['student_name', 'roll_number', 'board_name', 'stream', 'passing_year', 'subjects_marks'],
                'optional_fields': ['father_name', 'school_name', 'total_marks', 'percentage', 'grade'],
                'validation_rules': {
                    'passing_year': 'must be 4-digit year',
                    'stream': 'Science/Commerce/Arts'
                }
            },
            'transfer_certificate': {
                'required_fields': ['student_name', 'father_name', 'class_studied', 'school_name', 'date_of_leaving'],
                'optional_fields': ['mother_name', 'date_of_birth', 'caste', 'religion'],
                'validation_rules': {
                    'date_of_leaving': 'DD-MM-YYYY format'
                }
            },
            'entrance_scorecard': {
                'required_fields': ['candidate_name', 'roll_number', 'exam_name', 'score', 'rank'],
                'optional_fields': ['percentile', 'category_rank', 'exam_date'],
                'validation_rules': {
                    'score': 'must be numeric',
                    'rank': 'must be numeric'
                }
            }
        }
        
        return schemas.get(document_type, {
            'required_fields': ['name'],
            'optional_fields': [],
            'validation_rules': {}
        })
    
    def _create_extraction_prompt(self, document_type: str, schema: Dict[str, Any]) -> str:
        """Create extraction prompt for specific document type"""
        required_fields = schema.get('required_fields', [])
        optional_fields = schema.get('optional_fields', [])
        validation_rules = schema.get('validation_rules', {})
        
        prompt = f"""
Extract structured information from this {document_type.replace('_', ' ')} document image.

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON, no explanations or markdown
2. Use exact field names as specified
3. Use null for missing information, don't make up data
4. Follow validation rules exactly

REQUIRED FIELDS (must extract):
{json.dumps(required_fields, indent=2)}

OPTIONAL FIELDS (extract if available):
{json.dumps(optional_fields, indent=2)}

VALIDATION RULES:
{json.dumps(validation_rules, indent=2)}

EXAMPLE OUTPUT FORMAT:
{{
  "field_name": "extracted_value",
  "another_field": null,
  "numeric_field": 123
}}

Extract the data now:"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini JSON response"""
        try:
            # Find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = response_text[start:end+1]
                return json.loads(json_str)
            else:
                # Try to parse entire response as JSON
                return json.loads(response_text.strip())
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Response text: {response_text}")
            raise Exception(f"Failed to parse JSON response: {e}")
    
    def _validate_data(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate extracted data against schema"""
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
                
                if field.endswith('_year') and 'digit year' in rule:
                    if not (isinstance(value, (int, str)) and len(str(value)) == 4):
                        issues.append(f"{field} should be 4-digit year, got: {value}")
                
                elif field == 'aadhaar_number' and '12 digits' in rule:
                    if not (isinstance(value, str) and len(value.replace(' ', '').replace('-', '')) == 12):
                        issues.append(f"Aadhaar number should be 12 digits, got: {value}")
                
                elif 'numeric' in rule:
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        issues.append(f"{field} should be numeric, got: {value}")
        
        return issues
    
    def _calculate_confidence(self, data: Dict[str, Any], validation_issues: List[str]) -> float:
        """Calculate confidence score based on data quality"""
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

def create_processor(api_key: str = None) -> GeminiDocumentProcessor:
    """Factory function to create processor"""
    return GeminiDocumentProcessor(api_key=api_key)