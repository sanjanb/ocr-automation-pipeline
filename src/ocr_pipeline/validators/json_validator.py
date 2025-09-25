"""
JSON Schema and Validation Module for OCR Automation Pipeline
MIT Hackathon Project

This module defines JSON schemas for different document types and provides
validation and cross-referencing capabilities for extracted data.
"""

import json
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, date
from dataclasses import dataclass, field
import re
import logging
from enum import Enum

from ..classifiers.document_classifier import DocumentType

logger = logging.getLogger(__name__)

@dataclass 
class ValidationResult:
    """Result from JSON validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class DocumentSchemas:
    """JSON schemas for different document types"""
    
    @staticmethod
    def get_base_schema() -> Dict[str, Any]:
        """Base schema shared by all documents"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["document_type", "name"],
            "properties": {
                "document_type": {
                    "type": "string",
                    "enum": [dt.value for dt in DocumentType]
                },
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z\\s\\.]+$",
                    "minLength": 3,
                    "maxLength": 100
                },
                "processing_metadata": {
                    "type": "object",
                    "properties": {
                        "processed_at": {"type": "string", "format": "date-time"},
                        "ocr_engine": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "file_path": {"type": "string"}
                    }
                }
            }
        }
    
    @staticmethod
    def get_marksheet_10th_schema() -> Dict[str, Any]:
        """Schema for 10th marksheet"""
        base = DocumentSchemas.get_base_schema()
        base.update({
            "required": ["document_type", "name", "roll_number", "board", "year", "subjects"],
            "properties": {
                **base["properties"],
                "roll_number": {
                    "type": "string",
                    "pattern": "^\\d{6,12}$"
                },
                "board": {
                    "type": "string",
                    "enum": ["CBSE", "ICSE", "State Board", "Bihar Board", "UP Board", "Other"]
                },
                "year": {
                    "type": "integer",
                    "minimum": 1990,
                    "maximum": datetime.now().year
                },
                "school_name": {
                    "type": "string",
                    "maxLength": 200
                },
                "dob": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "father_name": {
                    "type": "string",
                    "pattern": "^[A-Za-z\\s\\.]+$"
                },
                "subjects": {
                    "type": "object",
                    "patternProperties": {
                        "^[A-Za-z\\s]+$": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100
                        }
                    },
                    "minProperties": 3  # At least 3 subjects
                },
                "total_marks": {
                    "type": "integer",
                    "minimum": 0
                },
                "percentage": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100
                },
                "grade": {
                    "type": "string",
                    "enum": ["A+", "A", "B+", "B", "C+", "C", "D", "F"]
                }
            }
        })
        return base
    
    @staticmethod
    def get_marksheet_12th_schema() -> Dict[str, Any]:
        """Schema for 12th marksheet"""
        base = DocumentSchemas.get_marksheet_10th_schema()
        base["required"].append("stream")
        base["properties"]["stream"] = {
            "type": "string",
            "enum": ["Science", "Commerce", "Arts", "Humanities"]
        }
        return base
    
    @staticmethod
    def get_entrance_scorecard_schema() -> Dict[str, Any]:
        """Schema for entrance exam scorecard"""
        base = DocumentSchemas.get_base_schema()
        base.update({
            "required": ["document_type", "name", "roll_number", "exam_name", "rank", "score"],
            "properties": {
                **base["properties"],
                "roll_number": {
                    "type": "string",
                    "pattern": "^[A-Z0-9]{8,15}$"
                },
                "exam_name": {
                    "type": "string",
                    "enum": ["JEE Main", "JEE Advanced", "NEET", "CAT", "GATE", "Other"]
                },
                "rank": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10000000
                },
                "category_rank": {
                    "type": "integer",
                    "minimum": 1
                },
                "score": {
                    "type": "integer",
                    "minimum": 0
                },
                "percentile": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100
                },
                "category": {
                    "type": "string",
                    "enum": ["General", "SC", "ST", "OBC", "EWS"]
                },
                "exam_date": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "qualifying_marks": {
                    "type": "integer",
                    "minimum": 0
                }
            }
        })
        return base
    
    @staticmethod
    def get_caste_certificate_schema() -> Dict[str, Any]:
        """Schema for caste certificate"""
        base = DocumentSchemas.get_base_schema()
        base.update({
            "required": ["document_type", "name", "category", "caste", "issuing_authority"],
            "properties": {
                **base["properties"],
                "category": {
                    "type": "string",
                    "enum": ["SC", "ST", "OBC", "EWS"]
                },
                "caste": {
                    "type": "string",
                    "maxLength": 100
                },
                "issuing_authority": {
                    "type": "string",
                    "maxLength": 200
                },
                "certificate_number": {
                    "type": "string",
                    "pattern": "^[A-Z0-9/-]+$"
                },
                "issue_date": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "validity_date": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "father_name": {
                    "type": "string",
                    "pattern": "^[A-Za-z\\s\\.]+$"
                },
                "address": {
                    "type": "object",
                    "properties": {
                        "district": {"type": "string"},
                        "state": {"type": "string"},
                        "pin_code": {"type": "string", "pattern": "^\\d{6}$"}
                    }
                }
            }
        })
        return base
    
    @staticmethod
    def get_aadhar_card_schema() -> Dict[str, Any]:
        """Schema for Aadhar card"""
        base = DocumentSchemas.get_base_schema()
        base.update({
            "required": ["document_type", "name", "aadhar_number", "dob"],
            "properties": {
                **base["properties"],
                "aadhar_number": {
                    "type": "string",
                    "pattern": "^\\d{4}\\s*\\d{4}\\s*\\d{4}$"
                },
                "dob": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "gender": {
                    "type": "string",
                    "enum": ["Male", "Female", "Other"]
                },
                "father_name": {
                    "type": "string",
                    "pattern": "^[A-Za-z\\s\\.]+$"
                },
                "address": {
                    "type": "object",
                    "properties": {
                        "care_of": {"type": "string"},
                        "house_number": {"type": "string"},
                        "street": {"type": "string"},
                        "locality": {"type": "string"},
                        "district": {"type": "string"},
                        "state": {"type": "string"},
                        "pin_code": {"type": "string", "pattern": "^\\d{6}$"}
                    }
                },
                "mobile": {
                    "type": "string",
                    "pattern": "^[6-9]\\d{9}$"
                },
                "email": {
                    "type": "string",
                    "format": "email"
                }
            }
        })
        return base

class DocumentValidator:
    """Validator for document JSON data"""
    
    def __init__(self):
        """Initialize the validator with schemas"""
        self.schemas = {
            DocumentType.MARKSHEET_10TH: DocumentSchemas.get_marksheet_10th_schema(),
            DocumentType.MARKSHEET_12TH: DocumentSchemas.get_marksheet_12th_schema(),
            DocumentType.ENTRANCE_SCORECARD: DocumentSchemas.get_entrance_scorecard_schema(),
            DocumentType.CASTE_CERTIFICATE: DocumentSchemas.get_caste_certificate_schema(),
            DocumentType.AADHAR_CARD: DocumentSchemas.get_aadhar_card_schema()
        }
        
        # Initialize validators
        self.validators = {}
        for doc_type, schema in self.schemas.items():
            self.validators[doc_type] = Draft7Validator(schema)
    
    def validate_document(self, 
                         document_data: Dict[str, Any], 
                         document_type: DocumentType) -> ValidationResult:
        """
        Validate document data against schema.
        
        Args:
            document_data: Document data to validate
            document_type: Type of document
            
        Returns:
            ValidationResult with validation outcome
        """
        try:
            if document_type not in self.validators:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"No schema available for document type: {document_type.value}"]
                )
            
            validator = self.validators[document_type]
            errors = []
            warnings = []
            
            # Perform schema validation
            schema_errors = sorted(validator.iter_errors(document_data), key=lambda e: e.path)
            
            for error in schema_errors:
                error_path = " -> ".join(str(p) for p in error.path)
                error_msg = f"Field '{error_path}': {error.message}"
                
                # Classify as error or warning based on severity
                if error.validator in ['required', 'type']:
                    errors.append(error_msg)
                else:
                    warnings.append(error_msg)
            
            # Additional custom validations
            custom_errors, custom_warnings = self._perform_custom_validations(
                document_data, document_type
            )
            
            errors.extend(custom_errors)
            warnings.extend(custom_warnings)
            
            # Calculate confidence score
            confidence_score = self._calculate_validation_confidence(
                document_data, document_type, len(errors), len(warnings)
            )
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                confidence_score=confidence_score,
                metadata={
                    "schema_used": document_type.value,
                    "total_fields": len(document_data),
                    "validation_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"]
            )
    
    def _perform_custom_validations(self, 
                                  document_data: Dict[str, Any], 
                                  document_type: DocumentType) -> Tuple[List[str], List[str]]:
        """Perform custom validation logic beyond schema"""
        errors = []
        warnings = []
        
        # Date validations
        if 'dob' in document_data:
            try:
                dob = datetime.strptime(document_data['dob'], '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                
                if age < 5:
                    errors.append("Date of birth indicates age less than 5 years")
                elif age > 100:
                    warnings.append("Date of birth indicates age greater than 100 years")
                    
                if dob > today:
                    errors.append("Date of birth cannot be in the future")
                    
            except ValueError:
                errors.append("Invalid date format for date of birth")
        
        # Academic year validations
        if 'year' in document_data and document_type in [DocumentType.MARKSHEET_10TH, DocumentType.MARKSHEET_12TH]:
            year = document_data['year']
            current_year = datetime.now().year
            
            if year > current_year:
                errors.append("Academic year cannot be in the future")
            elif year < current_year - 10:
                warnings.append("Academic year is more than 10 years old")
        
        # Subject marks validation for marksheets
        if 'subjects' in document_data and isinstance(document_data['subjects'], dict):
            subject_marks = document_data['subjects']
            
            if not subject_marks:
                errors.append("No subject marks found")
            else:
                # Check for reasonable subject names and marks
                for subject, marks in subject_marks.items():
                    if not isinstance(marks, (int, float)):
                        errors.append(f"Invalid marks for subject '{subject}': {marks}")
                    elif marks < 0 or marks > 100:
                        errors.append(f"Marks for '{subject}' out of valid range: {marks}")
                    
                    # Check subject name
                    if len(subject.strip()) < 3:
                        warnings.append(f"Subject name too short: '{subject}'")
        
        # Rank validation for entrance scorecards
        if document_type == DocumentType.ENTRANCE_SCORECARD:
            if 'rank' in document_data and 'category_rank' in document_data:
                rank = document_data['rank']
                cat_rank = document_data['category_rank']
                
                if cat_rank > rank:
                    errors.append("Category rank cannot be higher than overall rank")
        
        # Aadhar number validation
        if 'aadhar_number' in document_data:
            aadhar = document_data['aadhar_number'].replace(' ', '')
            if len(aadhar) != 12 or not aadhar.isdigit():
                errors.append("Invalid Aadhar number format")
        
        return errors, warnings
    
    def _calculate_validation_confidence(self, 
                                       document_data: Dict[str, Any], 
                                       document_type: DocumentType,
                                       error_count: int,
                                       warning_count: int) -> float:
        """Calculate confidence score for validation"""
        if document_type not in self.schemas:
            return 0.0
        
        schema = self.schemas[document_type]
        required_fields = set(schema.get('required', []))
        present_fields = set(document_data.keys())
        
        # Base score from required field coverage
        required_coverage = len(required_fields.intersection(present_fields)) / len(required_fields)
        
        # Penalty for errors and warnings
        error_penalty = error_count * 0.2
        warning_penalty = warning_count * 0.1
        
        confidence = required_coverage - error_penalty - warning_penalty
        
        # Bonus for having additional valid fields
        optional_fields = set(schema.get('properties', {}).keys()) - required_fields
        optional_coverage = len(optional_fields.intersection(present_fields)) / max(len(optional_fields), 1)
        
        confidence += optional_coverage * 0.2
        
        return max(0.0, min(1.0, confidence))

class CrossValidator:
    """Cross-validation between multiple documents"""
    
    def __init__(self):
        """Initialize cross validator"""
        self.validation_rules = self._initialize_cross_validation_rules()
    
    def _initialize_cross_validation_rules(self) -> Dict[str, Dict]:
        """Initialize cross-validation rules"""
        return {
            "name_consistency": {
                "description": "Name should be consistent across all documents",
                "fields": ["name"],
                "tolerance": 0.8  # Allow for minor OCR differences
            },
            "dob_consistency": {
                "description": "Date of birth should be consistent",
                "fields": ["dob"],
                "tolerance": 1.0  # Must be exact
            },
            "father_name_consistency": {
                "description": "Father's name should be consistent",
                "fields": ["father_name"],
                "tolerance": 0.8
            },
            "academic_progression": {
                "description": "12th marks should be after 10th marks",
                "documents": [DocumentType.MARKSHEET_10TH, DocumentType.MARKSHEET_12TH],
                "validation": "year_progression"
            },
            "eligibility_check": {
                "description": "Entrance exam eligibility based on 12th marks",
                "documents": [DocumentType.MARKSHEET_12TH, DocumentType.ENTRANCE_SCORECARD],
                "validation": "eligibility_criteria"
            }
        }
    
    def cross_validate_documents(self, documents: List[Dict[str, Any]]) -> ValidationResult:
        """
        Perform cross-validation between multiple documents.
        
        Args:
            documents: List of document data dictionaries
            
        Returns:
            ValidationResult with cross-validation outcome
        """
        errors = []
        warnings = []
        
        if len(documents) < 2:
            return ValidationResult(
                is_valid=True,
                warnings=["Cross-validation requires at least 2 documents"]
            )
        
        # Check name consistency
        names = [doc.get('name', '').lower().strip() for doc in documents if 'name' in doc]
        if len(set(names)) > 1:
            # Check if names are similar (allowing for OCR errors)
            similarity_threshold = 0.8
            if not self._are_names_similar(names, similarity_threshold):
                errors.append(f"Name inconsistency detected: {names}")
        
        # Check date of birth consistency
        dobs = [doc.get('dob') for doc in documents if 'dob' in doc]
        if len(set(dobs)) > 1:
            errors.append(f"Date of birth inconsistency: {dobs}")
        
        # Academic progression check
        marksheets = {}
        for doc in documents:
            doc_type = doc.get('document_type')
            if doc_type in ['marksheet_10th', 'marksheet_12th']:
                marksheets[doc_type] = doc
        
        if 'marksheet_10th' in marksheets and 'marksheet_12th' in marksheets:
            year_10th = marksheets['marksheet_10th'].get('year', 0)
            year_12th = marksheets['marksheet_12th'].get('year', 0)
            
            if year_12th <= year_10th:
                errors.append("12th examination year should be after 10th examination year")
            elif year_12th - year_10th > 5:
                warnings.append("Unusual gap between 10th and 12th examinations")
        
        # Calculate cross-validation confidence
        confidence = 1.0 - (len(errors) * 0.3 + len(warnings) * 0.1)
        confidence = max(0.0, min(1.0, confidence))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            confidence_score=confidence,
            metadata={
                "documents_validated": len(documents),
                "cross_validation_rules_applied": len(self.validation_rules)
            }
        )
    
    def _are_names_similar(self, names: List[str], threshold: float) -> bool:
        """Check if names are similar allowing for OCR errors"""
        if not names:
            return True
        
        # Simple similarity check based on character overlap
        base_name = names[0]
        for name in names[1:]:
            similarity = self._calculate_string_similarity(base_name, name)
            if similarity < threshold:
                return False
        return True
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

def create_validator() -> DocumentValidator:
    """Factory function to create a document validator"""
    return DocumentValidator()

def create_cross_validator() -> CrossValidator:
    """Factory function to create a cross validator"""
    return CrossValidator()

def validate_document_json(document_data: Dict[str, Any], 
                         document_type: DocumentType) -> ValidationResult:
    """
    Convenience function to validate a single document.
    
    Args:
        document_data: Document data to validate
        document_type: Type of document
        
    Returns:
        ValidationResult
    """
    validator = create_validator()
    return validator.validate_document(document_data, document_type)