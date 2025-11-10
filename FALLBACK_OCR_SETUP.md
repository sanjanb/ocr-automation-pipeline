# OCR Fallback Setup Guide

## Install Tesseract OCR (Optional - for quota fallback)

### Windows

```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract

# Add to PATH or set environment variable
# Then install Python wrapper:
pip install pytesseract
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
pip install pytesseract
```

### macOS

```bash
brew install tesseract
pip install pytesseract
```

## Quick Test

```python
import pytesseract
from PIL import Image

# Test if tesseract is working
image = Image.open("test_document.jpg")
text = pytesseract.image_to_string(image)
print(text)
```

## Benefits

- Provides basic text extraction when Gemini API quota is exceeded
- No API costs for fallback processing
- Works offline
- Handles basic document text extraction

## Limitations

- Lower accuracy compared to Gemini AI
- No structured data extraction
- Requires manual field mapping
- Best effort text recognition only
