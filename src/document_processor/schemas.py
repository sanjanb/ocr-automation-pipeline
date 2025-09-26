"""
Document Schema Definitions
Defines required fields and validation rules for different document types
"""

from typing import Dict, Any, List

# Document schemas with required fields and validation rules
DOCUMENT_SCHEMAS = {
    'aadhaar_card': {
        'required_fields': ['name', 'aadhaar_number', 'date_of_birth', 'address'],
        'optional_fields': ['father_name', 'gender', 'mobile_number'],
        'validation_rules': {
            'aadhaar_number': 'Must be exactly 12 digits',
            'date_of_birth': 'Format: DD-MM-YYYY or DD/MM/YYYY',
            'mobile_number': 'Must be 10 digits'
        },
        'description': 'Indian Aadhaar Identity Card'
    },
    
    'marksheet_10th': {
        'required_fields': ['student_name', 'roll_number', 'board_name', 'passing_year', 'subjects_marks'],
        'optional_fields': ['father_name', 'mother_name', 'school_name', 'total_marks', 'percentage', 'result'],
        'validation_rules': {
            'passing_year': 'Must be 4-digit year',
            'roll_number': 'Alphanumeric roll number',
            'percentage': 'Numeric value between 0-100'
        },
        'description': '10th Class/Grade Marksheet'
    },
    
    'marksheet_12th': {
        'required_fields': ['student_name', 'roll_number', 'board_name', 'stream', 'passing_year', 'subjects_marks'],
        'optional_fields': ['father_name', 'mother_name', 'school_name', 'total_marks', 'percentage', 'grade'],
        'validation_rules': {
            'passing_year': 'Must be 4-digit year',
            'stream': 'Must be Science/Commerce/Arts',
            'percentage': 'Numeric value between 0-100'
        },
        'description': '12th Class/Grade Marksheet'
    },
    
    'transfer_certificate': {
        'required_fields': ['student_name', 'father_name', 'class_studied', 'school_name', 'date_of_leaving'],
        'optional_fields': ['mother_name', 'date_of_birth', 'date_of_admission', 'caste', 'religion', 'conduct'],
        'validation_rules': {
            'date_of_leaving': 'Format: DD-MM-YYYY',
            'date_of_birth': 'Format: DD-MM-YYYY',
            'date_of_admission': 'Format: DD-MM-YYYY'
        },
        'description': 'School Transfer Certificate'
    },
    
    'migration_certificate': {
        'required_fields': ['student_name', 'father_name', 'university_name', 'course_name', 'passing_year'],
        'optional_fields': ['roll_number', 'registration_number', 'division', 'migration_purpose'],
        'validation_rules': {
            'passing_year': 'Must be 4-digit year',
            'course_name': 'Full course name'
        },
        'description': 'University Migration Certificate'
    },
    
    'entrance_scorecard': {
        'required_fields': ['candidate_name', 'roll_number', 'exam_name', 'total_score'],
        'optional_fields': ['rank', 'percentile', 'category_rank', 'exam_date', 'qualifying_marks'],
        'validation_rules': {
            'total_score': 'Must be numeric',
            'rank': 'Must be numeric',
            'percentile': 'Must be numeric (0-100)'
        },
        'description': 'Competitive Exam Scorecard (JEE/NEET/etc.)'
    },
    
    'admit_card': {
        'required_fields': ['candidate_name', 'roll_number', 'exam_name', 'exam_date'],
        'optional_fields': ['exam_center', 'exam_time', 'father_name', 'photo_required', 'instructions'],
        'validation_rules': {
            'exam_date': 'Format: DD-MM-YYYY',
            'exam_time': 'Time format (e.g., 9:00 AM - 12:00 PM)'
        },
        'description': 'Examination Admit Card'
    },
    
    'caste_certificate': {
        'required_fields': ['applicant_name', 'father_name', 'caste', 'category'],
        'optional_fields': ['certificate_number', 'issue_date', 'issuing_authority', 'valid_until', 'address'],
        'validation_rules': {
            'category': 'Must be SC/ST/OBC/General',
            'issue_date': 'Format: DD-MM-YYYY'
        },
        'description': 'Caste Certificate'
    },
    
    'domicile_certificate': {
        'required_fields': ['applicant_name', 'father_name', 'state', 'district'],
        'optional_fields': ['certificate_number', 'issue_date', 'issuing_authority', 'address', 'duration_of_residence'],
        'validation_rules': {
            'issue_date': 'Format: DD-MM-YYYY'
        },
        'description': 'Domicile/Residence Certificate'
    },
    
    # Default schema for unknown document types
    'default': {
        'required_fields': ['name'],
        'optional_fields': ['date', 'number', 'address'],
        'validation_rules': {},
        'description': 'Unknown Document Type'
    }
}

def get_schema(document_type: str) -> Dict[str, Any]:
    """Get schema for specific document type"""
    return DOCUMENT_SCHEMAS.get(document_type, DOCUMENT_SCHEMAS['default'])

def get_supported_types() -> List[str]:
    """Get list of supported document types"""
    return [doc_type for doc_type in DOCUMENT_SCHEMAS.keys() if doc_type != 'default']

def create_example_output(document_type: str) -> Dict[str, Any]:
    """Create example output for document type"""
    schema = get_schema(document_type)
    example = {}
    
    # Add required fields with example values
    for field in schema['required_fields']:
        example[field] = f"<{field}_value>"
    
    # Add some optional fields as null
    for field in schema['optional_fields'][:3]:
        example[field] = None
        
    return example