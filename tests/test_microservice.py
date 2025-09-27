"""
Tests for Document Processing Microservice
Tests the new MongoDB-based document processing endpoints
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app import app
from src.document_processor.database import StudentDocument, DocumentEntry
from src.document_processor.models import ProcessDocumentRequest

class TestDocumentProcessingMicroservice:
    """Test cases for the document processing microservice endpoints"""
    
    @pytest.fixture
    def sample_request(self):
        """Sample request data"""
        return {
            "studentId": "12345",
            "docType": "AadharCard",
            "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/aadhaar.jpg"
        }
    
    @pytest.fixture
    def sample_normalized_fields(self):
        """Sample normalized fields"""
        return {
            "Name": "Sanjan Acharya",
            "AadhaarNumber": "1234 5678 9012",
            "DOB": "2002-06-15",
            "Address": "Bangalore, Karnataka",
            "Gender": "Male"
        }
    
    @pytest.fixture
    def sample_document_entry(self, sample_normalized_fields):
        """Sample document entry"""
        return DocumentEntry(
            docType="AadharCard",
            cloudinaryUrl="https://res.cloudinary.com/demo/image/upload/v1234567890/aadhaar.jpg",
            fields=sample_normalized_fields,
            confidence=0.95,
            validationIssues=[]
        )
    
    @pytest.fixture
    async def client(self):
        """Async HTTP client for testing"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        with patch('src.document_processor.database.DatabaseManager.health_check', return_value=True):
            response = await client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
            assert "database_connected" in data
            assert "gemini_configured" in data
    
    @pytest.mark.asyncio
    async def test_process_document_success(self, client, sample_request, sample_normalized_fields):
        """Test successful document processing"""
        with patch('src.document_processor.cloudinary_service.download_image_from_url') as mock_download, \
             patch('src.document_processor.core.DocumentProcessor.process_document_async') as mock_process, \
             patch('src.document_processor.database.StudentDocument.find_or_create_student') as mock_student, \
             patch('src.document_processor.normalizer.normalize_fields') as mock_normalize:
            
            # Setup mocks
            mock_download.return_value = "/tmp/test_image.jpg"
            
            from src.document_processor.core import ProcessingResult
            mock_result = ProcessingResult(
                success=True,
                document_type="aadhaar_card",
                extracted_data={"name": "Sanjan Acharya", "aadhaar_number": "1234567890123"},
                processing_time=2.5,
                validation_issues=[],
                confidence_score=0.95
            )
            mock_process.return_value = mock_result
            mock_normalize.return_value = sample_normalized_fields
            
            # Mock student document
            mock_student_doc = AsyncMock()
            mock_student_doc.studentId = "12345"
            mock_student_doc.add_document = AsyncMock(return_value=mock_student_doc)
            mock_student_doc.get_latest_document = AsyncMock(return_value=DocumentEntry(
                docType="AadharCard",
                cloudinaryUrl=sample_request["cloudinaryUrl"],
                fields=sample_normalized_fields,
                processedAt=datetime.utcnow(),
                confidence=0.95,
                validationIssues=[]
            ))
            mock_student.return_value = mock_student_doc
            
            # Make request
            response = await client.post("/process-doc", json=sample_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["studentId"] == "12345"
            assert data["savedDocument"]["docType"] == "AadharCard"
            assert data["savedDocument"]["fields"]["Name"] == "Sanjan Acharya"
            assert data["savedDocument"]["confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_process_document_invalid_cloudinary_url(self, client):
        """Test processing with invalid Cloudinary URL"""
        invalid_request = {
            "studentId": "12345",
            "docType": "AadharCard",
            "cloudinaryUrl": "https://example.com/invalid.jpg"  # Not a Cloudinary URL
        }
        
        response = await client.post("/process-doc", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_process_document_unsupported_doc_type(self, client):
        """Test processing with unsupported document type"""
        invalid_request = {
            "studentId": "12345",
            "docType": "UnsupportedDocument",
            "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v123/test.jpg"
        }
        
        response = await client.post("/process-doc", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_process_document_gemini_failure(self, client, sample_request):
        """Test handling of Gemini processing failure"""
        with patch('src.document_processor.cloudinary_service.download_image_from_url') as mock_download, \
             patch('src.document_processor.core.DocumentProcessor.process_document_async') as mock_process:
            
            mock_download.return_value = "/tmp/test_image.jpg"
            
            # Mock processing failure
            from src.document_processor.core import ProcessingResult
            mock_result = ProcessingResult(
                success=False,
                document_type="aadhaar_card",
                extracted_data={},
                processing_time=1.0,
                validation_issues=[],
                confidence_score=0.0,
                error_message="Failed to process document"
            )
            mock_process.return_value = mock_result
            
            response = await client.post("/process-doc", json=sample_request)
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_student_documents(self, client, sample_document_entry):
        """Test retrieving all documents for a student"""
        with patch('src.document_processor.database.StudentDocument.find_one') as mock_find:
            # Mock student with documents
            mock_student = AsyncMock()
            mock_student.studentId = "12345"
            mock_student.documents = [sample_document_entry]
            mock_student.createdAt = datetime.utcnow()
            mock_student.updatedAt = datetime.utcnow()
            mock_find.return_value = mock_student
            
            response = await client.get("/students/12345/documents")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["studentId"] == "12345"
            assert data["totalDocuments"] == 1
            assert len(data["documents"]) == 1
            assert data["documents"][0]["docType"] == "AadharCard"
    
    @pytest.mark.asyncio
    async def test_get_student_documents_not_found(self, client):
        """Test retrieving documents for non-existent student"""
        with patch('src.document_processor.database.StudentDocument.find_one') as mock_find:
            mock_find.return_value = None
            
            response = await client.get("/students/nonexistent/documents")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_student_document_by_type(self, client, sample_document_entry):
        """Test retrieving specific document type for a student"""
        with patch('src.document_processor.database.StudentDocument.find_one') as mock_find:
            # Mock student
            mock_student = AsyncMock()
            mock_student.studentId = "12345"
            mock_student.get_latest_document = AsyncMock(return_value=sample_document_entry)
            mock_find.return_value = mock_student
            
            response = await client.get("/students/12345/documents/AadharCard")
            assert response.status_code == 200
            
            data = response.json()
            assert data["docType"] == "AadharCard"
            assert data["fields"]["Name"] == "Sanjan Acharya"
    
    @pytest.mark.asyncio
    async def test_get_student_document_type_not_found(self, client):
        """Test retrieving non-existent document type"""
        with patch('src.document_processor.database.StudentDocument.find_one') as mock_find:
            # Mock student without requested document type
            mock_student = AsyncMock()
            mock_student.studentId = "12345"
            mock_student.get_latest_document = AsyncMock(return_value=None)
            mock_find.return_value = mock_student
            
            response = await client.get("/students/12345/documents/NonExistentType")
            assert response.status_code == 404

class TestFieldNormalization:
    """Test field normalization functionality"""
    
    def test_aadhaar_card_normalization(self):
        """Test Aadhaar card field normalization"""
        from src.document_processor.normalizer import normalize_fields
        
        raw_fields = {
            "full_name": "sanjan acharya",
            "aadhaar_number": "123456789012",
            "date_of_birth": "15/06/2002",
            "address": "Bangalore, Karnataka",
            "gender": "m"
        }
        
        normalized = normalize_fields(raw_fields, "aadhaar_card")
        
        assert normalized["Name"] == "Sanjan Acharya"
        assert normalized["AadhaarNumber"] == "1234 5678 9012"
        assert normalized["DOB"] == "2002-06-15"
        assert normalized["Address"] == "Bangalore, Karnataka"
        assert normalized["Gender"] == "Male"
    
    def test_marksheet_normalization(self):
        """Test marksheet field normalization"""
        from src.document_processor.normalizer import normalize_fields
        
        raw_fields = {
            "student_name": "sanjan acharya",
            "roll_number": "12345",
            "board_name": "CBSE",
            "passing_year": "2020",
            "subjects_marks": "Math: 95, Science: 90, English: 88",
            "percentage": "91.0%"
        }
        
        normalized = normalize_fields(raw_fields, "marksheet_10th")
        
        assert normalized["Name"] == "Sanjan Acharya"
        assert normalized["RollNumber"] == "12345"
        assert normalized["BoardName"] == "CBSE"
        assert normalized["ExamYear"] == "2020"
        assert normalized["Percentage"] == 91.0

class TestCloudinaryService:
    """Test Cloudinary service functionality"""
    
    @pytest.mark.asyncio
    async def test_valid_cloudinary_url_format(self):
        """Test validation of Cloudinary URL format"""
        from src.document_processor.cloudinary_service import CloudinaryService
        
        service = CloudinaryService()
        
        # Valid URL should not raise exception during validation
        valid_url = "https://res.cloudinary.com/demo/image/upload/v1234567890/test.jpg"
        
        # Mock the actual HTTP call since we're testing URL format validation
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {'content-type': 'image/jpeg'}
            mock_response.read = AsyncMock(return_value=b'fake_image_data')
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with patch('src.document_processor.cloudinary_service.CloudinaryService._validate_image'):
                # This should not raise an exception
                result = await service.download_image(valid_url)
                assert result  # Should return a file path
    
    @pytest.mark.asyncio
    async def test_invalid_cloudinary_url_format(self):
        """Test rejection of invalid Cloudinary URL format"""
        from src.document_processor.cloudinary_service import CloudinaryService
        
        service = CloudinaryService()
        invalid_url = "https://example.com/image.jpg"
        
        with pytest.raises(Exception) as exc_info:
            await service.download_image(invalid_url)
        
        assert "Invalid Cloudinary URL format" in str(exc_info.value)

if __name__ == "__main__":
    pytest.main([__file__])