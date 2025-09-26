"""
Test Core Processor Module
"""

import pytest
import os
from unittest.mock import Mock, patch
from src.document_processor.core import DocumentProcessor, create_processor

class TestDocumentProcessor:
    """Test cases for DocumentProcessor"""
    
    def test_processor_initialization_with_api_key(self):
        """Test processor initialization with API key"""
        with patch('src.document_processor.core.genai') as mock_genai:
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            processor = DocumentProcessor(api_key="test_key_123")
            
            assert processor.api_key == "test_key_123"
            assert processor.model == mock_model
            mock_genai.configure.assert_called_once_with(api_key="test_key_123")
    
    def test_processor_initialization_without_api_key(self):
        """Test processor initialization fails without API key"""
        with pytest.raises(ValueError, match="Gemini API key required"):
            DocumentProcessor()
    
    def test_processor_initialization_with_env_var(self, mock_env_vars):
        """Test processor initialization with environment variable"""
        with patch('src.document_processor.core.genai') as mock_genai:
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            processor = DocumentProcessor()
            
            assert processor.api_key == "test_api_key_123"
            mock_genai.configure.assert_called_once_with(api_key="test_api_key_123")
    
    @patch('src.document_processor.core.genai')
    def test_document_type_detection(self, mock_genai, sample_aadhaar_image):
        """Test document type detection"""
        # Setup mocks
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "aadhaar_card"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        processor = DocumentProcessor(api_key="test_key")
        
        # Test detection
        from PIL import Image
        image = Image.open(sample_aadhaar_image)
        doc_type = processor._detect_document_type(image)
        
        assert doc_type == "aadhaar_card"
        mock_model.generate_content.assert_called_once()
    
    @patch('src.document_processor.core.genai')
    def test_process_document_success(self, mock_genai, sample_aadhaar_image):
        """Test successful document processing"""
        # Setup mocks
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''
        {
            "name": "JOHN DOE",
            "aadhaar_number": "123456789012",
            "date_of_birth": "15/08/1995",
            "address": "123 Main Street, Bangalore"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        processor = DocumentProcessor(api_key="test_key")
        
        # Test processing
        result = processor.process_document(sample_aadhaar_image, "aadhaar_card")
        
        assert result.success is True
        assert result.document_type == "aadhaar_card"
        assert "name" in result.extracted_data
        assert result.extracted_data["name"] == "JOHN DOE"
        assert result.confidence_score > 0
        assert result.processing_time > 0
    
    def test_create_processor_factory(self):
        """Test processor factory function"""
        with patch('src.document_processor.core.DocumentProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            
            processor = create_processor(api_key="test_key")
            
            assert processor == mock_processor
            mock_processor_class.assert_called_once_with(api_key="test_key", model_name=None)

class TestDataValidation:
    """Test data validation functionality"""
    
    @patch('src.document_processor.core.genai')
    def test_validation_with_missing_required_fields(self, mock_genai):
        """Test validation identifies missing required fields"""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        processor = DocumentProcessor(api_key="test_key")
        
        # Test with incomplete data
        data = {"name": "John Doe"}  # Missing required fields
        issues = processor._validate_data(data, "aadhaar_card")
        
        assert len(issues) > 0
        assert any("Missing required field" in issue for issue in issues)
    
    @patch('src.document_processor.core.genai') 
    def test_confidence_calculation(self, mock_genai):
        """Test confidence score calculation"""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        processor = DocumentProcessor(api_key="test_key")
        
        # Test with complete data
        complete_data = {
            "name": "John Doe",
            "aadhaar_number": "123456789012",
            "date_of_birth": "15/08/1995",
            "address": "123 Main Street",
            "father_name": "Robert Doe"
        }
        confidence = processor._calculate_confidence(complete_data, [])
        assert confidence > 0.8
        
        # Test with incomplete data
        incomplete_data = {"name": "John Doe"}
        low_confidence = processor._calculate_confidence(incomplete_data, ["Missing field"])
        assert low_confidence < confidence