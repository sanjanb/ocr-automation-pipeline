"""
Field Normalization for Document Types
Standardizes extracted fields across different document types
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Field mapping rules for each document type
FIELD_MAPPINGS = {
    'aadhaar_card': {
        # Common variations -> Normalized field name
        'full_name': 'Name',
        'name': 'Name',
        'holder_name': 'Name',
        'aadhaar_holder_name': 'Name',
        
        'aadhaar_number': 'AadhaarNumber',
        'aadhar_number': 'AadhaarNumber',
        'uid': 'AadhaarNumber',
        'number': 'AadhaarNumber',
        
        'date_of_birth': 'DOB',
        'dob': 'DOB',
        'birth_date': 'DOB',
        'date_birth': 'DOB',
        
        'address': 'Address',
        'permanent_address': 'Address',
        'residential_address': 'Address',
        'full_address': 'Address',
        
        'father_name': 'FatherName',
        'fathers_name': 'FatherName',
        'parent_name': 'FatherName',
        
        'gender': 'Gender',
        'sex': 'Gender',
        
        'mobile_number': 'MobileNumber',
        'mobile': 'MobileNumber',
        'phone_number': 'MobileNumber',
        'contact': 'MobileNumber',
    },
    
    'marksheet_10th': {
        'student_name': 'Name',
        'name': 'Name',
        'candidate_name': 'Name',
        'full_name': 'Name',
        
        'roll_number': 'RollNumber',
        'roll_no': 'RollNumber',
        'admission_number': 'RollNumber',
        'enrollment_number': 'RollNumber',
        
        'board_name': 'BoardName',
        'board': 'BoardName',
        'education_board': 'BoardName',
        
        'passing_year': 'ExamYear',
        'year_of_passing': 'ExamYear',
        'exam_year': 'ExamYear',
        'year': 'ExamYear',
        
        'subjects_marks': 'Subjects',
        'marks': 'Subjects',
        'subject_wise_marks': 'Subjects',
        'grades': 'Subjects',
        
        'school_name': 'SchoolName',
        'institution_name': 'SchoolName',
        'institution': 'SchoolName',
        
        'father_name': 'FatherName',
        'fathers_name': 'FatherName',
        
        'mother_name': 'MotherName',
        'mothers_name': 'MotherName',
        
        'total_marks': 'TotalMarks',
        'maximum_marks': 'TotalMarks',
        'full_marks': 'TotalMarks',
        
        'percentage': 'Percentage',
        'percent': 'Percentage',
        'marks_percentage': 'Percentage',
        
        'result': 'Result',
        'exam_result': 'Result',
        'status': 'Result',
    },
    
    'marksheet_12th': {
        'student_name': 'Name',
        'name': 'Name',
        'candidate_name': 'Name',
        'full_name': 'Name',
        
        'roll_number': 'RollNumber',
        'roll_no': 'RollNumber',
        'admission_number': 'RollNumber',
        'enrollment_number': 'RollNumber',
        
        'board_name': 'BoardName',
        'board': 'BoardName',
        'education_board': 'BoardName',
        
        'stream': 'Stream',
        'course': 'Stream',
        'subject_combination': 'Stream',
        'specialization': 'Stream',
        
        'passing_year': 'ExamYear',
        'year_of_passing': 'ExamYear',
        'exam_year': 'ExamYear',
        'year': 'ExamYear',
        
        'subjects_marks': 'Subjects',
        'marks': 'Subjects',
        'subject_wise_marks': 'Subjects',
        'grades': 'Subjects',
        
        'school_name': 'SchoolName',
        'institution_name': 'SchoolName',
        'institution': 'SchoolName',
        
        'father_name': 'FatherName',
        'fathers_name': 'FatherName',
        
        'mother_name': 'MotherName',
        'mothers_name': 'MotherName',
        
        'total_marks': 'TotalMarks',
        'maximum_marks': 'TotalMarks',
        'full_marks': 'TotalMarks',
        
        'percentage': 'Percentage',
        'percent': 'Percentage',
        'marks_percentage': 'Percentage',
        
        'grade': 'Grade',
        'overall_grade': 'Grade',
        'final_grade': 'Grade',
    },
    
    'transfer_certificate': {
        'student_name': 'Name',
        'name': 'Name',
        'full_name': 'Name',
        
        'father_name': 'FatherName',
        'fathers_name': 'FatherName',
        'parent_name': 'FatherName',
        
        'mother_name': 'MotherName',
        'mothers_name': 'MotherName',
        
        'class_studied': 'ClassStudied',
        'last_class': 'ClassStudied',
        'grade': 'ClassStudied',
        
        'school_name': 'SchoolName',
        'institution_name': 'SchoolName',
        'institution': 'SchoolName',
        
        'date_of_leaving': 'DateOfLeaving',
        'leaving_date': 'DateOfLeaving',
        'tc_date': 'DateOfLeaving',
        
        'date_of_birth': 'DOB',
        'dob': 'DOB',
        'birth_date': 'DOB',
        
        'date_of_admission': 'DateOfAdmission',
        'admission_date': 'DateOfAdmission',
        'joining_date': 'DateOfAdmission',
        
        'caste': 'Caste',
        'category': 'Caste',
        'community': 'Caste',
        
        'religion': 'Religion',
        'religious_belief': 'Religion',
        
        'conduct': 'Conduct',
        'character': 'Conduct',
        'behaviour': 'Conduct',
    },
}

def normalize_fields(raw_fields: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
    """
    Normalize field names based on document type
    
    Args:
        raw_fields: Raw extracted fields from Gemini
        doc_type: Document type (internal format)
        
    Returns:
        Dictionary with normalized field names
    """
    if doc_type not in FIELD_MAPPINGS:
        logger.warning(f"No field mapping found for document type: {doc_type}")
        return raw_fields
    
    mapping = FIELD_MAPPINGS[doc_type]
    normalized = {}
    
    # Apply field name normalization
    for raw_key, value in raw_fields.items():
        # Convert to lowercase for matching
        raw_key_lower = raw_key.lower().replace(' ', '_').replace('-', '_')
        
        # Find normalized field name
        normalized_key = mapping.get(raw_key_lower, raw_key)  # Use original if no mapping found
        
        # Apply value normalization based on field type
        normalized_value = _normalize_field_value(normalized_key, value, doc_type)
        
        normalized[normalized_key] = normalized_value
    
    # Apply post-processing rules
    normalized = _apply_post_processing_rules(normalized, doc_type)
    
    logger.info(f"Normalized {len(raw_fields)} fields to {len(normalized)} for {doc_type}")
    return normalized

def _normalize_field_value(field_name: str, value: Any, doc_type: str) -> Any:
    """Normalize field values based on field type"""
    if value is None or value == "":
        return None
    
    # Convert to string for processing
    str_value = str(value).strip()
    
    # Date normalization (DD/MM/YYYY or DD-MM-YYYY)
    if any(date_field in field_name.lower() for date_field in ['dob', 'date']):
        return _normalize_date(str_value)
    
    # Phone number normalization
    if 'mobile' in field_name.lower() or 'phone' in field_name.lower():
        return _normalize_phone_number(str_value)
    
    # Aadhaar number normalization
    if 'aadhaar' in field_name.lower() and 'number' in field_name.lower():
        return _normalize_aadhaar_number(str_value)
    
    # Percentage normalization
    if 'percentage' in field_name.lower():
        return _normalize_percentage(str_value)
    
    # Name normalization
    if field_name in ['Name', 'FatherName', 'MotherName', 'SchoolName', 'BoardName']:
        return _normalize_name(str_value)
    
    return str_value

def _normalize_date(date_str: str) -> str:
    """Normalize date formats to YYYY-MM-DD"""
    import re
    
    # Remove extra spaces
    date_str = re.sub(r'\s+', ' ', date_str.strip())
    
    # Try different date patterns
    patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2})\s+(\w+)\s+(\d{4})',        # DD Month YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            if len(match.group(1)) == 4:  # Year first
                year, month, day = match.groups()
            else:  # Day first
                day, month, year = match.groups()
            
            # Pad with zeros
            day = day.zfill(2)
            month = month.zfill(2) if month.isdigit() else month
            
            # Convert month names to numbers
            month_names = {
                'january': '01', 'jan': '01',
                'february': '02', 'feb': '02',
                'march': '03', 'mar': '03',
                'april': '04', 'apr': '04',
                'may': '05',
                'june': '06', 'jun': '06',
                'july': '07', 'jul': '07',
                'august': '08', 'aug': '08',
                'september': '09', 'sep': '09',
                'october': '10', 'oct': '10',
                'november': '11', 'nov': '11',
                'december': '12', 'dec': '12',
            }
            
            if month.lower() in month_names:
                month = month_names[month.lower()]
            
            return f"{year}-{month}-{day}"
    
    return date_str  # Return original if no pattern matches

def _normalize_phone_number(phone_str: str) -> str:
    """Normalize phone numbers"""
    import re
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone_str)
    
    # Handle Indian phone numbers
    if digits.startswith('91') and len(digits) == 12:
        return digits[2:]  # Remove country code
    elif digits.startswith('+91') and len(digits) == 13:
        return digits[3:]  # Remove +91
    elif len(digits) == 10:
        return digits
    
    return phone_str  # Return original if can't normalize

def _normalize_aadhaar_number(aadhaar_str: str) -> str:
    """Normalize Aadhaar numbers"""
    import re
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', aadhaar_str)
    
    # Aadhaar should be exactly 12 digits
    if len(digits) == 12:
        # Format as XXXX XXXX XXXX
        return f"{digits[:4]} {digits[4:8]} {digits[8:]}"
    
    return aadhaar_str  # Return original if invalid

def _normalize_percentage(percent_str: str) -> Optional[float]:
    """Normalize percentage values"""
    import re
    
    # Extract numeric value
    match = re.search(r'(\d+\.?\d*)', percent_str)
    if match:
        try:
            value = float(match.group(1))
            return round(value, 2)
        except ValueError:
            pass
    
    return None

def _normalize_name(name_str: str) -> str:
    """Normalize names (proper case)"""
    import re
    
    # Remove extra spaces and convert to title case
    name = re.sub(r'\s+', ' ', name_str.strip()).title()
    
    # Handle special cases
    name = re.sub(r'\bOf\b', 'of', name)
    name = re.sub(r'\bThe\b', 'the', name)
    name = re.sub(r'\bAnd\b', 'and', name)
    
    return name

def _apply_post_processing_rules(fields: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
    """Apply document-specific post-processing rules"""
    
    # Aadhaar Card specific rules
    if doc_type == 'aadhaar_card':
        # Ensure gender is standardized
        if 'Gender' in fields and fields['Gender']:
            gender = fields['Gender'].lower()
            if gender in ['m', 'male']:
                fields['Gender'] = 'Male'
            elif gender in ['f', 'female']:
                fields['Gender'] = 'Female'
    
    # Marksheet specific rules
    elif doc_type in ['marksheet_10th', 'marksheet_12th']:
        # Ensure result is standardized
        if 'Result' in fields and fields['Result']:
            result = fields['Result'].lower()
            if 'pass' in result:
                fields['Result'] = 'Pass'
            elif 'fail' in result:
                fields['Result'] = 'Fail'
        
        # Handle subjects as nested object
        if 'Subjects' in fields and isinstance(fields['Subjects'], str):
            # Try to parse subjects string into structured data
            fields['Subjects'] = _parse_subjects_string(fields['Subjects'])
    
    return fields

def _parse_subjects_string(subjects_str: str) -> Dict[str, Any]:
    """Parse subjects string into structured format"""
    import re
    
    subjects = {}
    
    # Try to find subject-marks patterns
    patterns = [
        r'(\w+(?:\s+\w+)*):?\s*(\d+)',  # Subject: 95 or Subject 95
        r'(\w+(?:\s+\w+)*)\s*-\s*(\d+)',  # Subject - 95
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, subjects_str, re.IGNORECASE)
        for subject, marks in matches:
            subject = subject.strip().title()
            try:
                subjects[subject] = int(marks)
            except ValueError:
                subjects[subject] = marks
    
    # If no patterns matched, return original string
    return subjects if subjects else subjects_str