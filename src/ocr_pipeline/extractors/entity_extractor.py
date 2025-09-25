"""
Entity Extraction Module for OCR Automation Pipeline
MIT Hackathon Project

This module extracts structured entities from different document types
using NLP, regex patterns, and document-specific templates.
"""

import re
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum
import logging
import spacy
from spacy import displacy
import json
from pathlib import Path

from ..classifiers.document_classifier import DocumentType

logger = logging.getLogger(__name__)

@dataclass
class EntityResult:
    """Result from entity extraction"""
    entities: Dict[str, Any]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_method: str = "hybrid"
    processing_time: float = 0.0

class EntityExtractor:
    """
    Main entity extraction system that uses document-specific templates
    and AI/NLP to extract structured information from OCR text.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize entity extractor.
        
        Args:
            model_name: spaCy model name to use
        """
        self.model_name = model_name
        
        # Load spaCy model
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.error(f"spaCy model '{model_name}' not found. Please install it.")
            raise
        
        # Initialize extraction templates
        self.extraction_templates = self._initialize_extraction_templates()
        self.validation_patterns = self._initialize_validation_patterns()
    
    def extract_entities(self, 
                        text: str, 
                        document_type: DocumentType,
                        additional_context: Optional[Dict[str, Any]] = None) -> EntityResult:
        """
        Extract entities from OCR text based on document type.
        
        Args:
            text: OCR extracted text
            document_type: Type of document being processed
            additional_context: Additional context or metadata
            
        Returns:
            EntityResult with extracted entities
        """
        import time
        start_time = time.time()
        
        try:
            # Get extraction template for document type
            template = self.extraction_templates.get(document_type)
            if not template:
                logger.warning(f"No template found for document type: {document_type}")
                return self._empty_result()
            
            # Extract entities using multiple methods
            entities = {}
            
            # Method 1: Regex-based extraction
            regex_entities = self._extract_with_regex(text, template)
            entities.update(regex_entities)
            
            # Method 2: NLP-based extraction
            nlp_entities = self._extract_with_nlp(text, template)
            entities.update(nlp_entities)
            
            # Method 3: Template-based extraction
            template_entities = self._extract_with_template(text, template)
            entities.update(template_entities)
            
            # Validate extracted entities
            validated_entities = self._validate_entities(entities, document_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(validated_entities, text, template)
            
            processing_time = time.time() - start_time
            
            return EntityResult(
                entities=validated_entities,
                confidence=confidence,
                metadata={
                    "document_type": document_type.value,
                    "text_length": len(text),
                    "extraction_methods": ["regex", "nlp", "template"],
                    "template_used": template.get("name", "unknown")
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            processing_time = time.time() - start_time
            return EntityResult(
                entities={},
                confidence=0.0,
                metadata={"error": str(e)},
                processing_time=processing_time
            )
    
    def _initialize_extraction_templates(self) -> Dict[DocumentType, Dict]:
        """Initialize document-specific extraction templates"""
        return {
            DocumentType.MARKSHEET_10TH: {
                "name": "10th_marksheet",
                "required_fields": ["name", "roll_number", "board", "year", "subjects"],
                "optional_fields": ["dob", "father_name", "school_name"],
                "regex_patterns": {
                    "roll_number": [
                        r"roll\s*no\.?\s*:?\s*(\d{6,12})",
                        r"roll\s*number\s*:?\s*(\d{6,12})",
                        r"enrolment\s*no\.?\s*:?\s*(\d{6,12})"
                    ],
                    "year": [
                        r"(?:year|examination)\s*:?\s*(\d{4})",
                        r"(\d{4})\s*examination"
                    ],
                    "board": [
                        r"(cbse|icse|state\s*board|bihar\s*board|up\s*board)",
                        r"board\s*:?\s*([a-zA-Z\s]+)"
                    ]
                },
                "subject_patterns": [
                    r"(mathematics|math|maths)\s*:?\s*(\d{1,3})",
                    r"(science|physics|chemistry|biology)\s*:?\s*(\d{1,3})",
                    r"(english|hindi|social\s*science)\s*:?\s*(\d{1,3})"
                ]
            },
            
            DocumentType.MARKSHEET_12TH: {
                "name": "12th_marksheet",
                "required_fields": ["name", "roll_number", "board", "year", "subjects", "stream"],
                "optional_fields": ["dob", "father_name", "mother_name", "school_name", "percentage", "register_number"],
                "regex_patterns": {
                    "roll_number": [
                        r"roll\s*no\.?\s*:?\s*(\d{6,12})",
                        r"roll\s*number\s*:?\s*(\d{6,12})",
                        r"register\s*no\.?\s*:?\s*(\d{6,12})",
                        r"reg\.?\s*no\.?\s*:?\s*(\d{6,12})",
                        r"(?:register|reg)\s*(?:no|number)\.?\s*:?\s*(\d{6,12})"
                    ],
                    "name": [
                        r"candidate[''']?s\s*name\s*:?\s*}\s*([A-Z][A-Z\s]{2,30})",
                        r"candidate[''']?s\s*name\s*:?\s*([A-Z][A-Z\s]{2,30})",
                        r"name\s*of\s*candidate\s*:?\s*}\s*([A-Z][A-Z\s]{2,30})",
                        r"name\s*of\s*candidate\s*:?\s*([A-Z][A-Z\s]{2,30})",
                        r"student\s*name\s*:?\s*}\s*([A-Z][A-Z\s]{2,30})",
                        r"student\s*name\s*:?\s*([A-Z][A-Z\s]{2,30})",
                        r"candidate.*name.*}\s*([A-Z][A-Z\s]{2,30})",
                        r"candidate.*name.*([A-Z][A-Z\s]{2,30})",
                        # More specific patterns that avoid father/mother context
                        r"([A-Z]{3,15}\s+[A-Z]\s+[A-Z])(?=.*father[''']?s\s*name)",  # Before father's name
                        r"name\s*}\s*([A-Z][A-Z\s]{2,30})"
                    ],
                    "father_name": [
                        r"father[''']?s\s*name\s*:?\s*}\s*([A-Z][A-Z\s]{2,30})",
                        r"father.*name.*}\s*([A-Z][A-Z\s]{2,30})"
                    ],
                    "mother_name": [
                        r"mother[''']?s\s*name\s*:?\s*}\s*([A-Z][A-Z\s]{2,30})",
                        r"mother.*name.*}\s*([A-Z][A-Z\s]{2,30})"
                    ],
                    "stream": [
                        r"stream\s*:?\s*(science|commerce|arts|humanities)",
                        r"(science|commerce|arts|humanities)\s*stream",
                        r"combination\s*:?\s*([A-Z\s]+)",
                        r"group\s*:?\s*([A-Z\s]+)",
                        r"(PCMC|PCM|PCMB|CEC|HEP|ARTS)",  # Common PUC combinations
                        r"(?:physics|chemistry|mathematics|computer|biology|economics|commerce|arts)"
                    ],
                    "percentage": [
                        r"percentage\s*:?\s*(\d{1,3}(?:\.\d{1,2})?)\s*%?",
                        r"total\s*marks\s*:?\s*(\d{1,3}(?:\.\d{1,2})?)\s*%?",
                        r"class\s*obtained\s*:?\s*([A-Z\s]+)",
                        r"(distinction|first\s*class|second\s*class|third\s*class|pass)",
                        r"(\d{3}/\d{3})"  # Like 535/600
                    ],
                    "year": [
                        r"month/year\s*:?\s*([A-Z]+\s*\d{4})",
                        r"(APRIL|MAY|JUNE|MARCH)\s*(\d{4})",
                        r"examination\s*held\s*in\s*([A-Z]+\s*\d{4})",
                        r"(20\d{2})"  # Any year like 2022
                    ],
                    "board": [
                        r"(karnataka|cbse|icse|state\s*board)",
                        r"department\s*of\s*pre[\-\s]*university",
                        r"government\s*of\s*karnataka",
                        r"puc?\s*board",
                        r"pre[\-\s]*university\s*education"
                    ],
                    "college": [
                        r"college\s*:?\s*([A-Z][A-Z\s,]{5,50})",
                        r"([A-Z]+\s+PU\s+COLLEGE)",
                        r"([A-Z\s]+COLLEGE[A-Z\s,]*)"
                    ]
                },
                "subject_patterns": [
                    r"(KANNADA|kannada)\s*.*?(\d{2,3})",
                    r"(ENGLISH|english)\s*.*?(\d{2,3})",
                    r"(PHYSICS|physics)\s*.*?(\d{2,3})",
                    r"(CHEMISTRY|chemistry)\s*.*?(\d{2,3})",
                    r"(MATHEMATICS|mathematics)\s*.*?(\d{2,3})",
                    r"(COMPUTER[\-\s]*SC|computer)\s*.*?(\d{2,3})",
                    r"(BIOLOGY|biology)\s*.*?(\d{2,3})"
                ]
            },
            
            DocumentType.ENTRANCE_SCORECARD: {
                "name": "entrance_scorecard",
                "required_fields": ["name", "roll_number", "exam_name", "rank", "score"],
                "optional_fields": ["percentile", "category", "date"],
                "regex_patterns": {
                    "exam_name": [
                        r"(jee\s*main|jee\s*advanced|neet|cat|gate)",
                        r"(joint\s*entrance\s*examination)"
                    ],
                    "rank": [
                        r"rank\s*:?\s*(\d{1,7})",
                        r"all\s*india\s*rank\s*:?\s*(\d{1,7})",
                        r"crl\s*:?\s*(\d{1,7})"
                    ],
                    "percentile": [
                        r"percentile\s*:?\s*(\d{1,3}(?:\.\d{1,4})?)",
                        r"nta\s*score\s*:?\s*(\d{1,3}(?:\.\d{1,4})?)"
                    ]
                }
            },
            
            DocumentType.CASTE_CERTIFICATE: {
                "name": "caste_certificate",
                "required_fields": ["name", "category", "caste", "issuing_authority"],
                "optional_fields": ["certificate_number", "date", "father_name"],
                "regex_patterns": {
                    "category": [
                        r"category\s*:?\s*(sc|st|obc|general|ews)",
                        r"(scheduled\s*caste|scheduled\s*tribe|other\s*backward)"
                    ],
                    "certificate_number": [
                        r"certificate\s*no\.?\s*:?\s*([A-Z0-9/-]+)",
                        r"cert\.?\s*no\.?\s*:?\s*([A-Z0-9/-]+)"
                    ]
                }
            },
            
            DocumentType.AADHAR_CARD: {
                "name": "aadhar_card",
                "required_fields": ["name", "aadhar_number", "dob"],
                "optional_fields": ["address", "father_name", "gender"],
                "regex_patterns": {
                    "aadhar_number": [
                        r"(\d{4}\s*\d{4}\s*\d{4})",
                        r"uid\s*:?\s*(\d{4}\s*\d{4}\s*\d{4})"
                    ]
                }
            }
        }
    
    def _initialize_validation_patterns(self) -> Dict[str, Dict]:
        """Initialize validation patterns for extracted entities"""
        return {
            "name": {
                "pattern": r"^[A-Za-z\s\.]+$",
                "min_length": 3,
                "max_length": 50
            },
            "roll_number": {
                "pattern": r"^\d{6,12}$",
                "min_length": 6,
                "max_length": 12
            },
            "year": {
                "pattern": r"^(19|20)\d{2}$",
                "min_value": 1990,
                "max_value": datetime.now().year
            },
            "dob": {
                "pattern": r"^\d{2}[-/]\d{2}[-/]\d{4}$",
                "format": ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]
            },
            "aadhar_number": {
                "pattern": r"^\d{4}\s*\d{4}\s*\d{4}$",
                "length": 12  # when spaces removed
            },
            "percentage": {
                "min_value": 0,
                "max_value": 100
            },
            "rank": {
                "min_value": 1,
                "max_value": 10000000
            }
        }
    
    def _extract_with_regex(self, text: str, template: Dict) -> Dict[str, Any]:
        """Extract entities using regex patterns with OCR error handling"""
        entities = {}
        
        # Preprocess text to handle common OCR errors
        clean_text = self._preprocess_ocr_text(text)
        
        regex_patterns = template.get("regex_patterns", {})
        
        for field_name, patterns in regex_patterns.items():
            for pattern in patterns:
                # Try on both original and cleaned text
                for text_variant in [text, clean_text]:
                    matches = re.finditer(pattern, text_variant, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        if match.groups():
                            value = match.group(1).strip()
                            # Clean up the extracted value
                            if field_name == "name":
                                value = self._clean_name(value)
                            elif field_name in ["roll_number", "register_number"]:
                                value = re.sub(r'[^\d]', '', value)  # Keep only digits
                            elif field_name == "year":
                                year_match = re.search(r'(20\d{2})', value)
                                if year_match:
                                    value = year_match.group(1)
                                    
                            if value and len(value.strip()) > 0:
                                entities[field_name] = value
                                break
                    if field_name in entities:
                        break  # Found match, move to next field
            
            # Special handling for subject patterns
            if field_name == "subjects" and "subject_patterns" in template:
                subjects = {}
                for subject_pattern in template["subject_patterns"]:
                    for text_variant in [text, clean_text]:
                        matches = re.finditer(subject_pattern, text_variant, re.IGNORECASE | re.DOTALL)
                        for match in matches:
                            if len(match.groups()) >= 2:
                                subject_name = match.group(1).strip().title()
                                try:
                                    score_text = match.group(2).strip()
                                    # Extract just the numeric part
                                    score_match = re.search(r'(\d{1,3})', score_text)
                                    if score_match:
                                        subject_score = int(score_match.group(1))
                                        if 0 <= subject_score <= 100:  # Valid score range
                                            subjects[subject_name] = subject_score
                                except (ValueError, AttributeError):
                                    continue
                
                # Additional subject extraction for better coverage
                if not subjects:
                    subjects = self._extract_subjects_fallback(text)
                
                if subjects:
                    entities["subjects"] = subjects
        
        # Try fallback extraction for critical fields if not found
        if "name" not in entities:
            entities["name"] = self._extract_name_fallback(text)
        
        if "roll_number" not in entities and template.get("name") == "12th_marksheet":
            entities["roll_number"] = self._extract_roll_number_fallback(text)
        
        return entities
    
    def _extract_with_nlp(self, text: str, template: Dict) -> Dict[str, Any]:
        """Extract entities using spaCy NLP"""
        entities = {}
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract named entities - but be smarter about person names
        person_candidates = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON" and "name" in template.get("required_fields", []):
                # Collect all person names with context
                person_name = ent.text.strip()
                start_pos = ent.start_char
                # Get context around the person name
                context_before = text[max(0, start_pos-50):start_pos].lower()
                context_after = text[start_pos+len(person_name):start_pos+len(person_name)+50].lower()
                
                # Score the person name based on context
                score = 0
                if any(keyword in context_before for keyword in ['candidate', 'student', 'name of']):
                    score += 10
                if any(keyword in context_before for keyword in ['father', 'mother', 'parent']):
                    score -= 5  # Penalize parent names
                    
                person_candidates.append((person_name, score, start_pos))
            
            elif ent.label_ == "DATE":
                # Try to extract year or date of birth
                date_text = ent.text.strip()
                
                # Check if it's a year
                year_match = re.search(r'\b(19|20)\d{2}\b', date_text)
                if year_match and "year" not in entities:
                    entities["year"] = year_match.group()
                
                # Check if it's a date of birth
                if any(keyword in text.lower() for keyword in ["birth", "born", "dob"]):
                    if "dob" not in entities:
                        entities["dob"] = date_text
            
            elif ent.label_ in ["ORG", "GPE"]:
                # Could be board, school, or institution
                org_text = ent.text.strip().lower()
                if any(keyword in org_text for keyword in ["board", "cbse", "icse", "state"]):
                    if "board" not in entities:
                        entities["board"] = ent.text.strip()
                elif any(keyword in org_text for keyword in ["school", "college", "university"]):
                    if "school_name" not in entities:
                        entities["school_name"] = ent.text.strip()
        
        # Choose the best person name candidate (highest score, or first if tied)
        if person_candidates and "name" not in entities:
            best_candidate = max(person_candidates, key=lambda x: (x[1], -x[2]))  # Highest score, then earliest position
            entities["name"] = self._clean_name(best_candidate[0])
        
        return entities
    
    def _extract_with_template(self, text: str, template: Dict) -> Dict[str, Any]:
        """Extract entities using template-based patterns"""
        entities = {}
        
        # Template-specific extraction logic
        template_name = template.get("name", "")
        
        if "marksheet" in template_name:
            entities.update(self._extract_marksheet_entities(text, template))
        elif "scorecard" in template_name:
            entities.update(self._extract_scorecard_entities(text, template))
        elif "certificate" in template_name:
            entities.update(self._extract_certificate_entities(text, template))
        
        return entities
    
    def _extract_marksheet_entities(self, text: str, template: Dict) -> Dict[str, Any]:
        """Extract marksheet-specific entities"""
        entities = {}
        
        # Look for common marksheet patterns
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Look for name pattern (usually near the top)
            if any(keyword in line_lower for keyword in ["name", "student"]) and i < len(lines) // 3:
                # Extract name from this line or next line
                name_match = re.search(r"name\s*:?\s*([a-zA-Z\s\.]+)", line, re.IGNORECASE)
                if name_match:
                    entities["name"] = name_match.group(1).strip()
                elif i + 1 < len(lines):
                    # Name might be on next line
                    next_line = lines[i + 1].strip()
                    if re.match(r"^[A-Za-z\s\.]+$", next_line) and len(next_line) > 3:
                        entities["name"] = next_line
            
            # Look for father's name
            if "father" in line_lower and "name" in line_lower:
                father_match = re.search(r"father['\s]*s?\s*name\s*:?\s*([a-zA-Z\s\.]+)", line, re.IGNORECASE)
                if father_match:
                    entities["father_name"] = father_match.group(1).strip()
        
        return entities
    
    def _extract_scorecard_entities(self, text: str, template: Dict) -> Dict[str, Any]:
        """Extract entrance exam scorecard entities"""
        entities = {}
        
        # Look for score patterns
        score_patterns = [
            r"total\s*score\s*:?\s*(\d{1,4})",
            r"score\s*:?\s*(\d{1,4})",
            r"marks\s*obtained\s*:?\s*(\d{1,4})"
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities["score"] = int(match.group(1))
                break
        
        return entities
    
    def _extract_certificate_entities(self, text: str, template: Dict) -> Dict[str, Any]:
        """Extract certificate-specific entities"""
        entities = {}
        
        # Look for issuing authority
        authority_patterns = [
            r"issued\s*by\s*:?\s*([a-zA-Z\s,\.]+)",
            r"authority\s*:?\s*([a-zA-Z\s,\.]+)",
            r"government\s*of\s*([a-zA-Z\s]+)"
        ]
        
        for pattern in authority_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities["issuing_authority"] = match.group(1).strip()
                break
        
        return entities
    
    def _validate_entities(self, entities: Dict[str, Any], document_type: DocumentType) -> Dict[str, Any]:
        """Validate and clean extracted entities"""
        validated = {}
        
        for field_name, value in entities.items():
            if field_name in self.validation_patterns:
                validation_rule = self.validation_patterns[field_name]
                
                # Pattern validation
                if "pattern" in validation_rule:
                    if not re.match(validation_rule["pattern"], str(value)):
                        logger.warning(f"Field {field_name} failed pattern validation: {value}")
                        continue
                
                # Length validation
                if "min_length" in validation_rule and len(str(value)) < validation_rule["min_length"]:
                    logger.warning(f"Field {field_name} too short: {value}")
                    continue
                
                if "max_length" in validation_rule and len(str(value)) > validation_rule["max_length"]:
                    logger.warning(f"Field {field_name} too long: {value}")
                    continue
                
                # Numeric range validation
                if "min_value" in validation_rule or "max_value" in validation_rule:
                    try:
                        numeric_value = float(value)
                        if "min_value" in validation_rule and numeric_value < validation_rule["min_value"]:
                            logger.warning(f"Field {field_name} below minimum: {value}")
                            continue
                        if "max_value" in validation_rule and numeric_value > validation_rule["max_value"]:
                            logger.warning(f"Field {field_name} above maximum: {value}")
                            continue
                    except (ValueError, TypeError):
                        logger.warning(f"Field {field_name} not numeric: {value}")
                        continue
            
            # If validation passes, add to validated entities
            validated[field_name] = value
        
        return validated
    
    def _preprocess_ocr_text(self, text: str) -> str:
        """Preprocess OCR text to fix common errors"""
        # Common OCR error corrections
        corrections = {
            # Common character substitutions
            'Educejio': 'Education',
            'Educatio': 'Education', 
            'Educafion': 'Education',
            'Govemment': 'Government',
            'Govemrnent': 'Government',
            'Departrnent': 'Department',
            'Depariment': 'Department',
            'Karnateka': 'Karnataka',
            'Kamataka': 'Karnataka',
            'Pre-Unlversity': 'Pre-University',
            'Pre-Unlverslty': 'Pre-University',
            'Reglster': 'Register',
            'Reglstratlon': 'Registration',
            'Candldate': 'Candidate',
            'Cendldate': 'Candidate',
            'Studenl': 'Student',
            'Siudent': 'Student',
            'Fathe1': 'Father',
            'Mothe1': 'Mother',
            'Ma1ks': 'Marks',
            'Malks': 'Marks',
            'Subjecl': 'Subject',
            'Subjecis': 'Subjects',
            # Numbers that might be confused
            'O': '0',  # Letter O to zero
            'l': '1',  # Letter l to one
            'S': '5',  # Sometimes S is confused with 5
            'G': '6',  # Sometimes G is confused with 6
        }
        
        cleaned_text = text
        for wrong, correct in corrections.items():
            cleaned_text = re.sub(rf'\b{re.escape(wrong)}\b', correct, cleaned_text, flags=re.IGNORECASE)
        
        # Fix spacing issues
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Multiple spaces to single
        cleaned_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned_text)  # Add space between lowercase and uppercase
        
        return cleaned_text
    
    def _clean_name(self, name: str) -> str:
        """Clean extracted name"""
        if not name:
            return "Unknown"
            
        # Remove extra spaces and special characters
        cleaned = re.sub(r'[^\w\s]', '', name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Capitalize properly
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        # Validate it looks like a name (at least 2 parts, each at least 1 char)
        parts = cleaned.split()
        if len(parts) >= 2 and all(len(part) >= 1 for part in parts):
            return cleaned
        
        return "Unknown"
    
    def _extract_name_fallback(self, text: str) -> str:
        """Fallback method to extract name from text"""
        # Look for common name patterns in PUC documents - prioritize Candidate's Name
        patterns = [
            r"candidate[''']?s\s*name\s*[:\}]\s*([A-Z][A-Z\s]{5,30})",
            r"name\s*of\s*candidate\s*[:\}]\s*([A-Z][A-Z\s]{5,30})",
            r"student\s*name\s*[:\}]\s*([A-Z][A-Z\s]{5,30})",
            # Look for patterns before Father's/Mother's name context
            r"([A-Z]{3,15}\s+[A-Z]\s+[A-Z])(?=.*father[''']?s\s*name)",  # Like SANJAN B M before Father's Name
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                name_candidate = match.group(1).strip() if match.groups() else match.group(0).strip()
                name = self._clean_name(name_candidate)
                if name != "Unknown" and len(name.split()) >= 2:
                    return name
        
        # If no specific pattern matches, try the general pattern but filter out parents' names
        general_pattern = r"([A-Z]{3,15}\s+[A-Z]\s+[A-Z])"
        matches = re.finditer(general_pattern, text, re.IGNORECASE)
        candidate_names = []
        
        for match in matches:
            name_candidate = match.group(1).strip()
            match_start = match.start()
            # Check context around the match
            context_before = text[max(0, match_start-30):match_start].lower()
            context_after = text[match.end():match.end()+30].lower()
            
            # Skip if this looks like father's or mother's name
            if any(keyword in context_before for keyword in ['father', 'mother', 'parent']):
                continue
                
            name = self._clean_name(name_candidate)
            if name != "Unknown" and len(name.split()) >= 2:
                candidate_names.append(name)
        
        # Return first valid candidate name
        if candidate_names:
            return candidate_names[0]
        
        return "Unknown"
    
    def _extract_roll_number_fallback(self, text: str) -> str:
        """Fallback method to extract roll/register number"""
        # Look for 6-digit numbers (common in PUC)
        patterns = [
            r'(\d{6,8})',  # Any 6-8 digit number
            r'No[:\.\s]*(\d{6,8})',
            r'Register[:\.\s]*(\d{6,8})',
            r'Roll[:\.\s]*(\d{6,8})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                number = match.group(1).strip()
                if 6 <= len(number) <= 8:  # Reasonable length for roll number
                    return number
        
        return "Unknown"
    
    def _extract_subjects_fallback(self, text: str) -> dict:
        """Fallback method to extract subjects and scores"""
        subjects = {}
        
        # Look for subject-score patterns in the text
        # Pattern: SUBJECT_NAME followed by numbers (possibly on next line)
        subject_patterns = [
            r"(KANNADA|ENGLISH|PHYSICS|CHEMISTRY|MATHEMATICS|COMPUTER\s*SC?|BIOLOGY|ELECTRONICS|ACCOUNTANCY|ECONOMICS|BUSINESS|STATISTICS|PSYCHOLOGY)\s*[:\-\s]*(\d{2,3})",
            r"([A-Z]{4,15})\s+(\d{2,3})",  # Generic subject pattern
        ]
        
        for pattern in subject_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) >= 2:
                    subject_name = match.group(1).strip().title()
                    try:
                        score = int(match.group(2).strip())
                        if 0 <= score <= 100:  # Valid score range
                            # Clean up subject name
                            subject_name = subject_name.replace("Sc", "Science")
                            if "Computer" in subject_name:
                                subject_name = "Computer Science"
                            subjects[subject_name] = score
                    except ValueError:
                        continue
        
        return subjects
    
    def _calculate_confidence(self, entities: Dict[str, Any], text: str, template: Dict) -> float:
        """Calculate confidence score for extracted entities"""
        required_fields = set(template.get("required_fields", []))
        extracted_fields = set(entities.keys())
        
        # Base confidence on coverage of required fields
        if not required_fields:
            return 0.8  # Default confidence if no requirements
        
        required_coverage = len(extracted_fields.intersection(required_fields)) / len(required_fields)
        
        # Bonus for optional fields
        optional_fields = set(template.get("optional_fields", []))
        optional_coverage = len(extracted_fields.intersection(optional_fields)) / max(len(optional_fields), 1)
        
        # Final confidence calculation
        confidence = required_coverage * 0.8 + optional_coverage * 0.2
        
        # Penalize if text is too short (might be incomplete OCR)
        if len(text) < 100:
            confidence *= 0.7
        
        return min(confidence, 1.0)
    
    def _empty_result(self) -> EntityResult:
        """Return empty result for unsupported document types"""
        return EntityResult(
            entities={},
            confidence=0.0,
            metadata={"status": "unsupported_document_type"}
        )

def create_entity_extractor(model_name: str = "en_core_web_sm") -> EntityExtractor:
    """
    Factory function to create an entity extractor.
    
    Args:
        model_name: spaCy model name
        
    Returns:
        EntityExtractor instance
    """
    return EntityExtractor(model_name=model_name)