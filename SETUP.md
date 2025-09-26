# Installation and Setup Guide

## Prerequisites

- Python 3.8 or higher
- Git
- 4GB RAM minimum (8GB recommended)
- Internet connection for API calls

## Environment Setup

### Option 1: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Conda Environment
```bash
# Create conda environment
conda create -n document-processor python=3.10
conda activate document-processor

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### 1. Gemini API Key
Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey):

1. Sign in with Google account
2. Create new project (if needed)
3. Generate API key
4. Copy the key

### 2. Environment Variables
Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional configuration
GEMINI_MODEL=gemini-2.0-flash-exp
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB in bytes
PROCESSING_TIMEOUT=60   # seconds
MIN_CONFIDENCE_THRESHOLD=0.5
```

### 3. Alternative Configuration Methods

#### Environment Variables (Production)
```bash
# Linux/macOS
export GEMINI_API_KEY=your_api_key_here
export DEBUG=false

# Windows
set GEMINI_API_KEY=your_api_key_here
set DEBUG=false
```

#### Configuration File
You can also use a `config.yml` file:
```yaml
gemini:
  api_key: your_api_key_here
  model: gemini-2.0-flash-exp

server:
  host: 0.0.0.0
  port: 8000
  debug: false

processing:
  max_file_size: 10485760
  timeout: 60
  min_confidence: 0.5
```

## Verification

### Quick Test
```bash
# Test installation
python -c "import src.document_processor.core; print('✅ Installation successful')"

# Test API key
python -c "
import os
from src.document_processor.core import create_processor
try:
    processor = create_processor()
    print('✅ API key valid')
except Exception as e:
    print(f'❌ API key issue: {e}')
"
```

### Run Test Suite
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Start Application
```bash
# Development server
uvicorn app:app --reload

# Production server
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'src'
# Solution: Run from project root directory
cd /path/to/ocr-automation-pipeline
python app.py
```

#### 2. API Key Issues
```bash
# Error: Gemini API key required
# Solution: Check .env file exists and has correct key
ls -la .env
cat .env | grep GEMINI_API_KEY
```

#### 3. Package Installation Issues
```bash
# Error: Failed building wheel for package
# Solution: Upgrade pip and try again
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 4. Port Already in Use
```bash
# Error: Port 8000 is already in use
# Solution: Use different port or kill process
uvicorn app:app --port 8001
# Or find and kill process using port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

### Performance Issues

#### 1. Slow Processing
- Check internet connection
- Verify Gemini API quotas
- Consider using faster model variants

#### 2. High Memory Usage
- Reduce image sizes before processing
- Implement batch processing limits
- Use Docker with memory constraints

#### 3. API Rate Limits
- Implement exponential backoff
- Use multiple API keys with rotation
- Cache results when appropriate

### Logging

Enable detailed logging for debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

### Docker Issues

#### 1. Build Failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t document-processor .
```

#### 2. Container Won't Start
```bash
# Check logs
docker logs document-processor

# Interactive debugging
docker run -it document-processor /bin/bash
```

## Advanced Configuration

### Custom Model Selection
```python
from src.document_processor.core import create_processor

# Use specific model
processor = create_processor(model_name="gemini-1.5-pro")
```

### Processing Timeouts
```python
from src.document_processor.config import Settings

settings = Settings()
settings.processing_timeout = 120  # 2 minutes
```

### Custom Validation Rules
```python
# Add custom validation in schemas.py
DOCUMENT_SCHEMAS['custom_document'] = {
    'required_fields': ['custom_field'],
    'validation_rules': {
        'custom_field': 'Custom validation rule'
    }
}
```

## Production Deployment

### Security Considerations
- Use HTTPS in production
- Implement rate limiting
- Set up proper error logging
- Use secrets management for API keys
- Enable CORS only for trusted origins

### Performance Optimization
- Use multiple workers
- Implement caching
- Set up load balancing
- Monitor API quotas and usage

### Monitoring
- Set up health checks
- Monitor processing times
- Track error rates
- Log API usage and costs

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review the logs for error details
3. Search existing [GitHub Issues](https://github.com/sanjanb/ocr-automation-pipeline/issues)
4. Create a new issue with:
   - Python version
   - Operating system
   - Error message
   - Steps to reproduce