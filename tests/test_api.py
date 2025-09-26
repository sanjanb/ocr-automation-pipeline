"""
Test FastAPI Application
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
import io
from PIL import Image

# Import the app
from app import app

client = TestClient(app)

class TestAPI:
    """Test FastAPI endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Smart Document Processor" in response.text
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "supported_documents" in data
        assert isinstance(data["supported_documents"], list)
    
    def test_schemas_endpoint(self):
        """Test schemas endpoint"""
        response = client.get("/schemas")
        assert response.status_code == 200
        
        data = response.json()
        assert "aadhaar_card" in data
        assert "marksheet_10th" in data
        
        # Check schema structure
        aadhaar_schema = data["aadhaar_card"]
        assert "required_fields" in aadhaar_schema
        assert "optional_fields" in aadhaar_schema
        assert "validation_rules" in aadhaar_schema
        assert "description" in aadhaar_schema
    
    @patch('app.processor')
    def test_process_document_success(self, mock_processor, sample_aadhaar_image):
        """Test successful document processing via API"""
        # Setup mock processor
        mock_result = Mock()
        mock_result.success = True
        mock_result.document_type = "aadhaar_card"
        mock_result.extracted_data = {
            "name": "JOHN DOE",
            "aadhaar_number": "123456789012",
            "date_of_birth": "15/08/1995",
            "address": "123 Main Street, Bangalore"
        }
        mock_result.processing_time = 2.5
        mock_result.validation_issues = []
        mock_result.confidence_score = 0.85
        mock_result.model_used = "gemini-1.5-flash"
        mock_result.error_message = None
        mock_result.metadata = {"image_size": [800, 500]}
        
        mock_processor.process_document_async.return_value = mock_result
        
        # Test API call
        with open(sample_aadhaar_image, "rb") as image_file:
            response = client.post(
                "/api/process",
                files={"file": ("test.png", image_file, "image/png")},
                data={"document_type": "aadhaar_card"}
            )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["document_type"] == "aadhaar_card"
        assert data["extracted_data"]["name"] == "JOHN DOE"
        assert data["confidence_score"] == 0.85
    
    def test_process_document_invalid_file_type(self):
        """Test processing with invalid file type"""
        # Create a text file instead of image
        text_content = b"This is not an image"
        
        response = client.post(
            "/api/process",
            files={"file": ("test.txt", io.BytesIO(text_content), "text/plain")}
        )
        
        assert response.status_code == 400
        assert "File must be an image" in response.json()["detail"]
    
    def test_process_document_invalid_document_type(self, sample_aadhaar_image):
        """Test processing with invalid document type"""
        with open(sample_aadhaar_image, "rb") as image_file:
            response = client.post(
                "/api/process",
                files={"file": ("test.png", image_file, "image/png")},
                data={"document_type": "invalid_type"}
            )
        
        assert response.status_code == 400
        assert "Unsupported document type" in response.json()["detail"]
    
    def test_process_document_no_file(self):
        """Test processing without file upload"""
        response = client.post("/api/process")
        assert response.status_code == 422  # Validation error
    
    def test_batch_processing_info(self):
        """Test batch processing info endpoint"""
        response = client.get("/api/process/batch")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Batch processing not implemented" in data["message"]

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('app.processor', None)
    def test_processor_not_available(self, sample_aadhaar_image):
        """Test behavior when processor is not available"""
        with open(sample_aadhaar_image, "rb") as image_file:
            response = client.post(
                "/api/process",
                files={"file": ("test.png", image_file, "image/png")}
            )
        
        assert response.status_code == 503
        assert "Document processor not available" in response.json()["detail"]
    
    @patch('app.processor')
    def test_processing_exception(self, mock_processor, sample_aadhaar_image):
        """Test handling of processing exceptions"""
        # Setup mock to raise exception
        mock_processor.process_document_async.side_effect = Exception("Processing failed")
        
        with open(sample_aadhaar_image, "rb") as image_file:
            response = client.post(
                "/api/process",
                files={"file": ("test.png", image_file, "image/png")}
            )
        
        assert response.status_code == 500
        assert "Processing failed" in response.json()["detail"]