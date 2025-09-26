"""
Gemini Pro Entity Extractor
Uses Google's Gemini Pro to parse OCR text into structured JSON
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from PIL import Image
import google.generativeai as genai
import requests


@dataclass
class GeminiExtractionResult:
    """Result from Gemini extraction"""
    entities: Dict[str, Any]
    confidence: float
    raw_output: Dict[str, Any]
    model_used: str
    metadata: Dict[str, Any]


class GeminiEntityExtractor:
    """Extract entities using Gemini Pro API"""
    
    def __init__(self, api_key: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Configure Gemini API
        api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
        if not api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=api_key)
        
        # Try multiple model options
        model_options = [
            'models/gemini-2.5-flash',
            'models/gemini-1.5-flash',
            'models/gemini-pro-latest',
            'gemini-pro'
        ]
        
        self.model = None
        for model_name in model_options:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                self.logger.info(f"Successfully initialized Gemini model: {model_name}")
                break
            except Exception as e:
                self.logger.warning(f"Failed to initialize model {model_name}: {e}")
                continue
                
        if not self.model:
            raise ValueError("Failed to initialize any Gemini model. Check API key and model access.")
        
        self.logger.info("Gemini Pro entity extractor initialized")
        
    def extract_from_ocr_text(self, ocr_text: str, document_type: str = "marksheet_12th") -> GeminiExtractionResult:
        """
        Extract structured data from OCR text using Gemini Pro
        
        Args:
            ocr_text: Raw OCR extracted text
            document_type: Type of document for specialized extraction
            
        Returns:
            GeminiExtractionResult with extracted entities
        """
        try:
            self.logger.info(f"Starting Gemini extraction for document type: {document_type}")
            
            # Create extraction prompt based on document type
            prompt = self._create_extraction_prompt(ocr_text, document_type)
            
            # Send to Gemini Pro
            self.logger.info("Sending request to Gemini Pro API")
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                self.logger.warning("Empty response from Gemini Pro")
                return self._empty_result()
            
            # Parse JSON response
            extracted_data = self._parse_gemini_response(response.text, document_type)
            
            if extracted_data:
                confidence = self._calculate_confidence(extracted_data, ocr_text)
                
                return GeminiExtractionResult(
                    entities=extracted_data,
                    confidence=confidence,
                    raw_output={"gemini_response": response.text, "prompt_used": prompt[:200] + "..."},
                    model_used="gemini-pro",
                    metadata={
                        "document_type": document_type,
                        "ocr_text_length": len(ocr_text),
                        "entities_found": len(extracted_data)
                    }
                )
            else:
                self.logger.warning("Failed to parse Gemini response")
                return self._empty_result()
                
        except Exception as e:
            self.logger.error(f"Gemini extraction failed: {e}")
            return GeminiExtractionResult(
                entities={},
                confidence=0.0,
                raw_output={"error": str(e)},
                model_used="gemini-pro",
                metadata={"error": "extraction_failed"}
            )
    
    def _create_extraction_prompt(self, ocr_text: str, document_type: str) -> str:
        """Create extraction prompt for different document types"""
        
        base_instructions = """
You are an expert at parsing document text and extracting structured information.
I will provide you with OCR-extracted text from a document, and you need to extract specific fields and return them as a clean JSON object.

IMPORTANT RULES:
1. Return ONLY valid JSON - no explanations or additional text
2. Use null for missing fields, don't make up data
3. Clean up OCR errors when obvious (e.g., "N4me" → "Name")
4. Extract exact values as they appear in the text
5. For marks/scores, preserve original format
"""
        
        # Document-specific prompts
        prompts = {
            "marksheet_10th": f"""
{base_instructions}

Document Type: 10th Class Marksheet

Extract these fields from the OCR text:
{{
  "student_name": "Full name of student",
  "father_name": "Father's name", 
  "mother_name": "Mother's name",
  "roll_number": "Roll number or registration number",
  "board": "Education board (CBSE, ICSE, State Board, etc.)",
  "school_name": "School name",
  "passing_year": "Year of examination",
  "date_of_birth": "Date of birth if available",
  "subjects": {{
    "subject_name": "marks_obtained"
  }},
  "total_marks": "Total marks obtained",
  "max_marks": "Maximum marks",
  "percentage": "Percentage or CGPA",
  "result": "PASS/FAIL status"
}}

OCR Text:
{ocr_text}

JSON:""",
            
            "marksheet_12th": f"""
{base_instructions}

Document Type: 12th Class Marksheet

Extract these fields from the OCR text:
{{
  "student_name": "Full name of student",
  "father_name": "Father's name",
  "mother_name": "Mother's name", 
  "roll_number": "Roll number or registration number",
  "board": "Education board (CBSE, ICSE, State Board, etc.)",
  "school_name": "School name",
  "stream": "Stream (Science/Commerce/Arts)",
  "passing_year": "Year of examination",
  "date_of_birth": "Date of birth if available",
  "subjects": {{
    "subject_name": "marks_obtained"
  }},
  "total_marks": "Total marks obtained", 
  "max_marks": "Maximum marks",
  "percentage": "Percentage or CGPA",
  "result": "PASS/FAIL status"
}}

OCR Text:
{ocr_text}

JSON:""",
            
            "entrance_scorecard": f"""
{base_instructions}

Document Type: Entrance Exam Scorecard (JEE/NEET)

Extract these fields from the OCR text:
{{
  "candidate_name": "Full name of candidate",
  "roll_number": "Roll number or application number",
  "exam_name": "Exam name (JEE Main, JEE Advanced, NEET, etc.)",
  "exam_date": "Date of examination",
  "date_of_birth": "Date of birth",
  "category": "Category (General/OBC/SC/ST)",
  "subjects": {{
    "subject_name": "score_obtained"
  }},
  "total_score": "Total score",
  "percentile": "Percentile if available", 
  "rank": "Rank if available",
  "qualifying_status": "Qualified/Not Qualified"
}}

OCR Text:
{ocr_text}

JSON:""",
            
            "aadhar_card": f"""
{base_instructions}

Document Type: Aadhar Card

Extract these fields from the OCR text:
{{
  "name": "Full name",
  "aadhar_number": "12-digit Aadhar number",
  "date_of_birth": "Date of birth",
  "gender": "Male/Female",
  "address": "Full address",
  "phone": "Phone number if visible",
  "email": "Email if visible"
}}

OCR Text:
{ocr_text}

JSON:"""
        }
        
        return prompts.get(document_type, prompts["marksheet_12th"])
    
    def _parse_gemini_response(self, response_text: str, document_type: str) -> Optional[Dict[str, Any]]:
        """Parse Gemini response and extract JSON"""
        try:
            # Clean up response text
            response_text = response_text.strip()
            
            # Find JSON in response (sometimes Gemini adds extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end+1]
                parsed_data = json.loads(json_str)
                
                # Clean up and validate data
                cleaned_data = self._clean_extracted_data(parsed_data)
                return cleaned_data
            else:
                self.logger.warning("No JSON found in Gemini response")
                return None
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from Gemini response: {e}")
            # Try to fix common JSON issues
            try:
                fixed_json = self._fix_json_issues(response_text)
                if fixed_json:
                    return json.loads(fixed_json)
            except:
                pass
            return None
        except Exception as e:
            self.logger.error(f"Error parsing Gemini response: {e}")
            return None
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize extracted data"""
        if not isinstance(data, dict):
            return {}
        
        cleaned = {}
        for key, value in data.items():
            if value is not None and value != "" and value != "null":
                # Clean up common OCR errors
                if isinstance(value, str):
                    value = value.strip()
                    # Remove common OCR artifacts
                    value = value.replace('|', 'I').replace('0', 'O').replace('5', 'S')
                    
                cleaned[key] = value
                
        return cleaned
    
    def _fix_json_issues(self, json_text: str) -> Optional[str]:
        """Try to fix common JSON formatting issues"""
        try:
            # Remove markdown code blocks
            json_text = json_text.replace('```json', '').replace('```', '')
            
            # Find JSON boundaries
            start = json_text.find('{')
            end = json_text.rfind('}')
            
            if start != -1 and end != -1:
                return json_text[start:end+1]
                
        except Exception:
            pass
        
        return None
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], ocr_text: str) -> float:
        """Calculate confidence score based on extraction quality"""
        if not extracted_data:
            return 0.0
        
        confidence = 0.0
        total_fields = len(extracted_data)
        
        # Base confidence for successful parsing
        confidence += 0.5
        
        # Bonus for number of fields extracted
        if total_fields >= 5:
            confidence += 0.2
        elif total_fields >= 3:
            confidence += 0.1
        
        # Bonus for key fields present
        key_fields = ['student_name', 'name', 'candidate_name', 'roll_number', 'aadhar_number']
        for field in key_fields:
            if field in extracted_data and extracted_data[field]:
                confidence += 0.1
                break
        
        # Bonus for numeric data (marks, scores)
        numeric_fields = ['total_marks', 'percentage', 'total_score', 'percentile']
        for field in numeric_fields:
            if field in extracted_data and extracted_data[field]:
                try:
                    float(str(extracted_data[field]).replace('%', ''))
                    confidence += 0.1
                    break
                except:
                    pass
        
        return min(confidence, 1.0)
    
    def _empty_result(self) -> GeminiExtractionResult:
        """Return empty result"""
        return GeminiExtractionResult(
            entities={},
            confidence=0.0,
            raw_output={},
            model_used="gemini-pro",
            metadata={"error": "no_extraction"}
        )


def create_gemini_entity_extractor(api_key: str = None) -> GeminiEntityExtractor:
    """Factory function to create Gemini entity extractor"""
    return GeminiEntityExtractor(api_key=api_key)