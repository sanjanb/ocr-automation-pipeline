"""
One-Click Validation System
Enhanced validation using Gemini for intelligent field checking
"""

from typing import Dict, Any, List
import json
import logging
from gemini_processor import GeminiDocumentProcessor
from document_schemas import DocumentSchemas

logger = logging.getLogger(__name__)

class SmartValidator:
    """
    One-click validation system that uses Gemini for intelligent validation
    beyond basic rule checking
    """
    
    def __init__(self, processor: GeminiDocumentProcessor):
        self.processor = processor
    
    def validate_with_ai(self, extracted_data: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """
        Perform AI-powered validation of extracted data
        
        Returns:
            Dict with validation results, suggestions, and confidence
        """
        schema = DocumentSchemas.get_schema(document_type)
        
        # Create validation prompt
        validation_prompt = f"""
        Analyze this extracted data from a {document_type.replace('_', ' ')} and provide validation feedback.
        
        EXTRACTED DATA:
        {json.dumps(extracted_data, indent=2)}
        
        REQUIRED FIELDS: {schema.required_fields}
        VALIDATION RULES: {schema.validation_rules}
        
        Please analyze and respond with JSON containing:
        {{
          "overall_quality": "excellent|good|fair|poor",
          "missing_critical_fields": ["field1", "field2"],
          "data_quality_issues": [
            {{"field": "field_name", "issue": "description", "severity": "high|medium|low"}}
          ],
          "suggestions": [
            "specific suggestion 1",
            "specific suggestion 2"
          ],
          "confidence_assessment": "high|medium|low",
          "ready_for_processing": true/false
        }}
        
        Focus on:
        1. Missing mandatory information
        2. Data format inconsistencies
        3. Logical errors (e.g., future dates, impossible values)
        4. Completeness for the document type
        
        Return only the JSON, no explanations.
        """
        
        try:
            response = self.processor.model.generate_content(validation_prompt)
            if response and response.text:
                return self._parse_validation_response(response.text)
        except Exception as e:
            logger.error(f"AI validation failed: {e}")
        
        # Fallback to basic validation
        return self._basic_validation_fallback(extracted_data, schema)
    
    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini validation response"""
        try:
            # Find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = response_text[start:end+1]
                return json.loads(json_str)
                
            return json.loads(response_text.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"Validation JSON parsing failed: {e}")
            return {
                "overall_quality": "unknown",
                "missing_critical_fields": [],
                "data_quality_issues": [],
                "suggestions": ["AI validation failed - please review manually"],
                "confidence_assessment": "low",
                "ready_for_processing": False
            }
    
    def _basic_validation_fallback(self, data: Dict[str, Any], schema) -> Dict[str, Any]:
        """Fallback validation when AI fails"""
        missing_fields = []
        issues = []
        
        for field in schema.required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        # Basic data quality checks
        for field, value in data.items():
            if value and isinstance(value, str):
                if field.endswith('_year') and len(value) != 4:
                    issues.append({
                        "field": field,
                        "issue": "Year should be 4 digits",
                        "severity": "medium"
                    })
                elif field.endswith('_number') and not value.replace(' ', '').replace('-', '').isdigit():
                    issues.append({
                        "field": field,
                        "issue": "Should contain only numbers",
                        "severity": "high"
                    })
        
        return {
            "overall_quality": "fair" if len(missing_fields) < 2 else "poor",
            "missing_critical_fields": missing_fields,
            "data_quality_issues": issues,
            "suggestions": [f"Please verify {field}" for field in missing_fields[:3]],
            "confidence_assessment": "medium" if len(missing_fields) == 0 else "low",
            "ready_for_processing": len(missing_fields) == 0 and len(issues) == 0
        }

def create_validator(processor: GeminiDocumentProcessor) -> SmartValidator:
    """Factory function to create validator"""
    return SmartValidator(processor)