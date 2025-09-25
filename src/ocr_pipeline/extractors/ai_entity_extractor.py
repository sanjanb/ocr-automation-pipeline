#!/usr/bin/env python3
"""
AI-powered OCR entity extractor using Hugging Face document understanding models
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from PIL import Image
import requests
from dataclasses import dataclass
import base64
from io import BytesIO

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class AIExtractionResult:
    """Result from AI-powered extraction"""
    entities: Dict[str, Any]
    confidence: float
    raw_output: Dict[str, Any]
    model_used: str
    metadata: Dict[str, Any]

class AIEntityExtractor:
    """
    AI-powered entity extractor using Hugging Face models
    """
    
    def __init__(self, hf_token: Optional[str] = None):
        """
        Initialize AI entity extractor
        
        Args:
            hf_token: Hugging Face API token (optional, can use environment variable)
        """
        self.hf_token = hf_token or os.getenv("HUGGING_FACE_TOKEN")
        
        # Model configurations for different document types
        self.models = {
            "donut": {
                "api_url": "https://api-inference.huggingface.co/models/naver-clova-ix/donut-base-finetuned-docvqa",
                "model_name": "naver-clova-ix/donut-base-finetuned-docvqa",
                "description": "Donut model for document visual question answering"
            },
            "layoutlmv3": {
                "api_url": "https://api-inference.huggingface.co/models/microsoft/layoutlmv3-base",
                "model_name": "microsoft/layoutlmv3-base",
                "description": "LayoutLMv3 for document understanding"
            },
            "form_recognizer": {
                "api_url": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                "model_name": "microsoft/DialoGPT-medium", 
                "description": "Form recognizer alternative"
            }
        }
        
        # Document-specific extraction prompts
        self.extraction_prompts = {
            "marksheet_12th": {
                "questions": [
                    "What is the candidate's name?",
                    "What is the roll number or registration number?", 
                    "What is the father's name?",
                    "What is the mother's name?",
                    "What year was this examination held?",
                    "What are the subject names and marks?",
                    "What is the total percentage or grade?",
                    "What is the name of the board or institution?",
                    "What is the name of the school or college?"
                ],
                "structured_prompt": "Extract the following information from this marksheet: student name, roll number, father's name, mother's name, examination year, subjects with marks, percentage, board name, and school name. Return as JSON format."
            },
            "marksheet_10th": {
                "questions": [
                    "What is the student's name?",
                    "What is the roll number?",
                    "What is the father's name?", 
                    "What is the mother's name?",
                    "What year was this examination?",
                    "What are the subjects and their marks?",
                    "What is the overall percentage or grade?",
                    "Which board conducted this examination?"
                ],
                "structured_prompt": "Extract student information from this 10th marksheet: name, roll number, parents' names, exam year, subject marks, percentage, and board name. Format as JSON."
            },
            "entrance_scorecard": {
                "questions": [
                    "What is the candidate's name?",
                    "What is the roll number or application number?",
                    "What is the exam name (JEE, NEET, etc.)?",
                    "What is the rank achieved?",
                    "What is the percentile or score?",
                    "What is the examination year?",
                    "What is the category (General, OBC, SC, ST)?"
                ],
                "structured_prompt": "Extract from this entrance exam scorecard: candidate name, roll number, exam name, rank, percentile/score, year, and category. Return as JSON."
            },
            "caste_certificate": {
                "questions": [
                    "What is the person's name?",
                    "What is the caste mentioned?",
                    "What is the category (SC/ST/OBC)?",
                    "What is the certificate number?",
                    "What is the issuing authority?",
                    "What is the issue date?",
                    "What is the father's name?"
                ],
                "structured_prompt": "Extract from this caste certificate: person name, caste, category, certificate number, issuing authority, issue date, and father's name. Format as JSON."
            }
        }
        
    def extract_from_image(self, image_path: str, document_type: str = "marksheet_12th") -> AIExtractionResult:
        """
        Extract structured data from document image using AI models
        
        Args:
            image_path: Path to the document image
            document_type: Type of document for specialized extraction
            
        Returns:
            AIExtractionResult with extracted data
        """
        try:
            logger.info(f"Starting AI extraction for {image_path}, type: {document_type}")
            
            # Load and preprocess image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Try different AI models in order of preference
            results = {}
            best_result = None
            best_confidence = 0.0
            
            # 1. Try Donut model first (best for structured extraction)
            try:
                donut_result = self._extract_with_donut(image, document_type)
                results["donut"] = donut_result
                if donut_result and donut_result.confidence > best_confidence:
                    best_result = donut_result
                    best_confidence = donut_result.confidence
            except Exception as e:
                logger.warning(f"Donut extraction failed: {e}")
            
            # 2. Try LayoutLMv3 as fallback
            try:
                layoutlm_result = self._extract_with_layoutlm(image, document_type)
                results["layoutlm"] = layoutlm_result
                if layoutlm_result and layoutlm_result.confidence > best_confidence:
                    best_result = layoutlm_result
                    best_confidence = layoutlm_result.confidence
            except Exception as e:
                logger.warning(f"LayoutLM extraction failed: {e}")
            
            # 3. Fallback to question-answering approach
            if not best_result or best_confidence < 0.5:
                try:
                    qa_result = self._extract_with_qa(image, document_type)
                    results["qa"] = qa_result
                    if qa_result and qa_result.confidence > best_confidence:
                        best_result = qa_result
                        best_confidence = qa_result.confidence
                except Exception as e:
                    logger.warning(f"Q&A extraction failed: {e}")
            
            # Return best result or empty result
            if best_result:
                best_result.metadata["all_results"] = {k: v.entities if v else None for k, v in results.items()}
                return best_result
            else:
                return AIExtractionResult(
                    entities={},
                    confidence=0.0,
                    raw_output={},
                    model_used="none",
                    metadata={"error": "All AI models failed", "attempts": list(results.keys())}
                )
                
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return AIExtractionResult(
                entities={},
                confidence=0.0,
                raw_output={},
                model_used="error",
                metadata={"error": str(e)}
            )
    
    def _extract_with_donut(self, image: Image.Image, document_type: str) -> Optional[AIExtractionResult]:
        """Extract using Donut model"""
        logger.info("Attempting extraction with Donut model")
        
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Get structured prompt for document type
        prompt = self.extraction_prompts.get(document_type, {}).get("structured_prompt", 
                                                                   "Extract all key information from this document as JSON")
        
        headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        
        # Donut API call
        payload = {
            "inputs": {
                "image": img_base64,
                "question": prompt
            }
        }
        
        response = requests.post(
            self.models["donut"]["api_url"],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            entities = self._parse_ai_response(result, document_type)
            confidence = self._calculate_ai_confidence(entities, document_type)
            
            return AIExtractionResult(
                entities=entities,
                confidence=confidence,
                raw_output=result,
                model_used="donut",
                metadata={"prompt": prompt}
            )
        else:
            logger.warning(f"Donut API error: {response.status_code}, {response.text}")
            return None
    
    def _extract_with_layoutlm(self, image: Image.Image, document_type: str) -> Optional[AIExtractionResult]:
        """Extract using LayoutLMv3 model"""
        logger.info("Attempting extraction with LayoutLMv3 model")
        
        # LayoutLM typically requires OCR text + bounding boxes
        # For simplicity, we'll use it as a document classifier first
        # In production, you'd integrate with OCR output
        
        # Convert image to bytes for API
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        
        headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        
        response = requests.post(
            self.models["layoutlmv3"]["api_url"],
            headers=headers,
            data=image_bytes,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            # LayoutLM might return classification or structured data
            entities = self._parse_layoutlm_response(result, document_type)
            confidence = self._calculate_ai_confidence(entities, document_type)
            
            return AIExtractionResult(
                entities=entities,
                confidence=confidence,
                raw_output=result,
                model_used="layoutlmv3",
                metadata={"document_type": document_type}
            )
        else:
            logger.warning(f"LayoutLM API error: {response.status_code}, {response.text}")
            return None
    
    def _extract_with_qa(self, image: Image.Image, document_type: str) -> Optional[AIExtractionResult]:
        """Extract using question-answering approach"""
        logger.info("Attempting extraction with Q&A approach")
        
        # Use document VQA model to ask specific questions
        questions = self.extraction_prompts.get(document_type, {}).get("questions", [])
        
        entities = {}
        confidence_scores = []
        
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        
        for question in questions:
            try:
                payload = {
                    "inputs": {
                        "image": img_base64,
                        "question": question
                    }
                }
                
                response = requests.post(
                    self.models["donut"]["api_url"],  # Using Donut for VQA
                    headers=headers,
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer", "").strip()
                    if answer and answer.lower() not in ["unknown", "not found", "n/a"]:
                        field_name = self._question_to_field_name(question)
                        entities[field_name] = answer
                        confidence_scores.append(result.get("score", 0.5))
                
            except Exception as e:
                logger.warning(f"Q&A failed for question '{question}': {e}")
                continue
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return AIExtractionResult(
            entities=entities,
            confidence=avg_confidence,
            raw_output={"qa_responses": entities},
            model_used="qa",
            metadata={"questions_asked": len(questions), "answers_found": len(entities)}
        )
    
    def _parse_ai_response(self, response: Dict, document_type: str) -> Dict[str, Any]:
        """Parse AI model response into structured entities"""
        entities = {}
        
        # Try to extract JSON from response
        if isinstance(response, dict):
            if "answer" in response:
                # Try to parse JSON from answer
                try:
                    answer = response["answer"]
                    if isinstance(answer, str):
                        # Try to find JSON in the string
                        import re
                        json_match = re.search(r'\{.*\}', answer, re.DOTALL)
                        if json_match:
                            entities = json.loads(json_match.group())
                        else:
                            # Parse as key-value pairs
                            entities = self._parse_text_response(answer)
                    elif isinstance(answer, dict):
                        entities = answer
                except (json.JSONDecodeError, AttributeError):
                    # Fallback to text parsing
                    entities = self._parse_text_response(str(response.get("answer", "")))
            else:
                # Direct response parsing
                entities = response
        
        # Standardize field names
        entities = self._standardize_field_names(entities, document_type)
        
        return entities
    
    def _parse_layoutlm_response(self, response: Dict, document_type: str) -> Dict[str, Any]:
        """Parse LayoutLM response"""
        # LayoutLM responses vary based on fine-tuning
        # This is a generic parser
        entities = {}
        
        if isinstance(response, list) and response:
            # Classification response
            entities["classification"] = response[0].get("label", "unknown")
            entities["confidence"] = response[0].get("score", 0.0)
        elif isinstance(response, dict):
            entities = response
        
        return self._standardize_field_names(entities, document_type)
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response into key-value pairs"""
        entities = {}
        
        # Look for key-value patterns
        import re
        patterns = [
            r'(\w+(?:\s+\w+)*)\s*:\s*([^\n\r]+)',  # key: value
            r'(\w+(?:\s+\w+)*)\s*=\s*([^\n\r]+)',  # key = value
            r'(\w+(?:\s+\w+)*)\s*-\s*([^\n\r]+)',  # key - value
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                key = match.group(1).strip().lower().replace(" ", "_")
                value = match.group(2).strip()
                if value and len(value) > 1:
                    entities[key] = value
        
        return entities
    
    def _standardize_field_names(self, entities: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """Standardize field names to match our schema"""
        field_mapping = {
            # Name variations
            "student_name": "name",
            "candidate_name": "name", 
            "person_name": "name",
            "full_name": "name",
            
            # Roll number variations
            "roll_no": "roll_number",
            "registration_number": "roll_number",
            "reg_no": "roll_number",
            "application_number": "roll_number",
            
            # Parent names
            "fathers_name": "father_name",
            "mothers_name": "mother_name",
            
            # Exam info
            "exam_year": "year",
            "examination_year": "year",
            "total_marks": "percentage",
            "overall_percentage": "percentage",
            
            # Institution info
            "school_name": "school",
            "college_name": "college",
            "board_name": "board",
            "institution": "board"
        }
        
        standardized = {}
        for key, value in entities.items():
            standard_key = field_mapping.get(key.lower(), key.lower())
            standardized[standard_key] = value
        
        return standardized
    
    def _question_to_field_name(self, question: str) -> str:
        """Convert question to field name"""
        question_lower = question.lower()
        
        if "name" in question_lower and ("candidate" in question_lower or "student" in question_lower):
            return "name"
        elif "father" in question_lower:
            return "father_name"
        elif "mother" in question_lower:
            return "mother_name"
        elif "roll" in question_lower or "registration" in question_lower:
            return "roll_number"
        elif "year" in question_lower:
            return "year"
        elif "subject" in question_lower or "marks" in question_lower:
            return "subjects"
        elif "percentage" in question_lower or "grade" in question_lower:
            return "percentage"
        elif "board" in question_lower or "institution" in question_lower:
            return "board"
        elif "school" in question_lower or "college" in question_lower:
            return "school"
        else:
            # Generate field name from question
            words = question_lower.replace("what is the ", "").replace("?", "").split()
            return "_".join(words[:2])  # Take first 2 words
    
    def _calculate_ai_confidence(self, entities: Dict[str, Any], document_type: str) -> float:
        """Calculate confidence based on extracted entities"""
        if not entities:
            return 0.0
        
        # Define required fields for each document type
        required_fields = {
            "marksheet_12th": ["name", "roll_number", "year"],
            "marksheet_10th": ["name", "roll_number", "year"],
            "entrance_scorecard": ["name", "roll_number", "rank"],
            "caste_certificate": ["name", "caste", "category"]
        }
        
        doc_required = required_fields.get(document_type, ["name"])
        found_required = sum(1 for field in doc_required if field in entities and entities[field])
        
        # Base confidence on required field coverage
        base_confidence = found_required / len(doc_required)
        
        # Bonus for additional fields
        total_fields = len([v for v in entities.values() if v and str(v).strip()])
        bonus = min(0.2, total_fields * 0.05)  # Up to 20% bonus
        
        return min(1.0, base_confidence + bonus)

def create_ai_entity_extractor(hf_token: Optional[str] = None) -> AIEntityExtractor:
    """
    Factory function to create AI entity extractor
    
    Args:
        hf_token: Hugging Face API token
        
    Returns:
        AIEntityExtractor instance
    """
    return AIEntityExtractor(hf_token=hf_token)