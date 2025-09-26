"""
Document Schema Definitions
Defines required fields and validation rules for different document types
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class DocumentSchema:
    """Schema definition for a document type"""
    document_type: str
    required_fields: List[str]
    optional_fields: List[str]
    validation_rules: Dict[str, str]
    description: str

class DocumentSchemas:
    """Collection of all document schemas"""
    
    @staticmethod
    def get_all_schemas() -> Dict[str, DocumentSchema]:
        """Get all document schemas"""
        return {
            'aadhaar_card': DocumentSchema(
                document_type='aadhaar_card',
                required_fields=['name', 'aadhaar_number', 'date_of_birth', 'address'],
                optional_fields=['father_name', 'gender', 'mobile_number'],
                validation_rules={
                    'aadhaar_number': 'Must be exactly 12 digits (spaces and hyphens will be removed)',
                    'date_of_birth': 'Format: DD-MM-YYYY or DD/MM/YYYY',
                    'mobile_number': 'Must be 10 digits'
                },
                description='Indian Aadhaar Identity Card'
            ),
            
            'marksheet_10th': DocumentSchema(
                document_type='marksheet_10th',
                required_fields=['student_name', 'roll_number', 'board_name', 'passing_year', 'subjects_marks'],
                optional_fields=['father_name', 'mother_name', 'school_name', 'total_marks', 'percentage', 'result'],
                validation_rules={
                    'passing_year': 'Must be 4-digit year (e.g., 2023)',
                    'roll_number': 'Alphanumeric roll number',
                    'subjects_marks': 'Object with subject names as keys and marks as numeric values',
                    'percentage': 'Numeric value between 0-100',
                    'total_marks': 'Numeric total marks'
                },
                description='10th Class/Grade Marksheet'
            ),
            
            'marksheet_12th': DocumentSchema(
                document_type='marksheet_12th',
                required_fields=['student_name', 'roll_number', 'board_name', 'stream', 'passing_year', 'subjects_marks'],
                optional_fields=['father_name', 'mother_name', 'school_name', 'total_marks', 'percentage', 'grade'],
                validation_rules={
                    'passing_year': 'Must be 4-digit year (e.g., 2023)',
                    'stream': 'Must be Science/Commerce/Arts',
                    'subjects_marks': 'Object with subject names as keys and marks as numeric values',
                    'percentage': 'Numeric value between 0-100'
                },
                description='12th Class/Grade Marksheet'
            ),
            
            'transfer_certificate': DocumentSchema(
                document_type='transfer_certificate',
                required_fields=['student_name', 'father_name', 'class_studied', 'school_name', 'date_of_leaving'],
                optional_fields=['mother_name', 'date_of_birth', 'date_of_admission', 'caste', 'religion', 'conduct'],
                validation_rules={
                    'date_of_leaving': 'Format: DD-MM-YYYY',
                    'date_of_birth': 'Format: DD-MM-YYYY',
                    'date_of_admission': 'Format: DD-MM-YYYY',
                    'class_studied': 'Class/grade level (e.g., 10th, 12th)'
                },
                description='School Transfer Certificate'
            ),
            
            'migration_certificate': DocumentSchema(
                document_type='migration_certificate',
                required_fields=['student_name', 'father_name', 'university_name', 'course_name', 'passing_year'],
                optional_fields=['roll_number', 'registration_number', 'division', 'migration_purpose'],
                validation_rules={
                    'passing_year': 'Must be 4-digit year',
                    'course_name': 'Full course name (e.g., Bachelor of Science)',
                    'division': 'First/Second/Third division or percentage'
                },
                description='University Migration Certificate'
            ),
            
            'entrance_scorecard': DocumentSchema(
                document_type='entrance_scorecard',
                required_fields=['candidate_name', 'roll_number', 'exam_name', 'total_score'],
                optional_fields=['rank', 'percentile', 'category_rank', 'exam_date', 'qualifying_marks'],
                validation_rules={
                    'total_score': 'Must be numeric',
                    'rank': 'Must be numeric (overall rank)',
                    'percentile': 'Must be numeric (0-100)',
                    'category_rank': 'Must be numeric'
                },
                description='Competitive Exam Scorecard (JEE/NEET/etc.)'
            ),
            
            'admit_card': DocumentSchema(
                document_type='admit_card',
                required_fields=['candidate_name', 'roll_number', 'exam_name', 'exam_date'],
                optional_fields=['exam_center', 'exam_time', 'father_name', 'photo_required', 'instructions'],
                validation_rules={
                    'exam_date': 'Format: DD-MM-YYYY or full date',
                    'exam_time': 'Time format (e.g., 9:00 AM - 12:00 PM)'
                },
                description='Examination Admit Card'
            ),
            
            'caste_certificate': DocumentSchema(
                document_type='caste_certificate',
                required_fields=['applicant_name', 'father_name', 'caste', 'category'],
                optional_fields=['certificate_number', 'issue_date', 'issuing_authority', 'valid_until', 'address'],
                validation_rules={
                    'category': 'Must be SC/ST/OBC/General',
                    'issue_date': 'Format: DD-MM-YYYY',
                    'valid_until': 'Format: DD-MM-YYYY'
                },
                description='Caste Certificate'
            ),
            
            'domicile_certificate': DocumentSchema(
                document_type='domicile_certificate',
                required_fields=['applicant_name', 'father_name', 'state', 'district'],
                optional_fields=['certificate_number', 'issue_date', 'issuing_authority', 'address', 'duration_of_residence'],
                validation_rules={
                    'issue_date': 'Format: DD-MM-YYYY',
                    'duration_of_residence': 'Number of years as resident'
                },
                description='Domicile/Residence Certificate'
            )
        }
    
    @staticmethod
    def get_schema(document_type: str) -> DocumentSchema:
        """Get schema for specific document type"""
        schemas = DocumentSchemas.get_all_schemas()
        return schemas.get(document_type, DocumentSchema(
            document_type='unknown',
            required_fields=['name'],
            optional_fields=[],
            validation_rules={},
            description='Unknown Document Type'
        ))
    
    @staticmethod
    def get_supported_types() -> List[str]:
        """Get list of supported document types"""
        return list(DocumentSchemas.get_all_schemas().keys())
    
    @staticmethod
    def create_extraction_example(document_type: str) -> Dict[str, Any]:
        """Create example output for document type"""
        schema = DocumentSchemas.get_schema(document_type)
        example = {}
        
        # Add required fields with example values
        for field in schema.required_fields:
            example[field] = f"<{field}_value>"
        
        # Add optional fields as null
        for field in schema.optional_fields[:3]:  # Only show first 3 optional fields
            example[field] = None
            
        return example