"""
Test Configuration and Fixtures
"""

import pytest
import tempfile
import os
from pathlib import Path
from PIL import Image, ImageDraw

@pytest.fixture
def sample_aadhaar_image():
    """Create a sample Aadhaar card image for testing"""
    img = Image.new('RGB', (800, 500), color='white')
    draw = ImageDraw.Draw(img)
    
    # Sample Aadhaar content
    lines = [
        "GOVERNMENT OF INDIA",
        "Unique Identification Authority of India",
        "",
        "Name: JOHN DOE",
        "Date of Birth: 15/08/1995",
        "Aadhaar Number: 1234 5678 9012",
        "Address: 123 Main Street",
        "         Bangalore, Karnataka",
        "         PIN: 560001"
    ]
    
    y = 50
    for line in lines:
        draw.text((50, y), line, fill='black')
        y += 35
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        img.save(temp_file.name)
        yield temp_file.name
    
    # Cleanup
    Path(temp_file.name).unlink(missing_ok=True)

@pytest.fixture
def sample_marksheet_image():
    """Create a sample marksheet image for testing"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    lines = [
        "BOARD OF SECONDARY EDUCATION",
        "SECONDARY EXAMINATION - 2023",
        "",
        "Student Name: JANE SMITH",
        "Roll Number: 123456",
        "Father's Name: ROBERT SMITH",
        "Board: CBSE",
        "Passing Year: 2023",
        "",
        "SUBJECTS:",
        "Mathematics: 95",
        "Physics: 88", 
        "Chemistry: 92",
        "English: 87",
        "Biology: 90",
        "",
        "Total: 452/500",
        "Percentage: 90.4%",
        "Result: PASS"
    ]
    
    y = 40
    for line in lines:
        draw.text((50, y), line, fill='black')
        y += 28
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        img.save(temp_file.name)
        yield temp_file.name
    
    Path(temp_file.name).unlink(missing_ok=True)

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["GEMINI_API_KEY"] = "test_api_key_123"
    os.environ["DEBUG"] = "true"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)