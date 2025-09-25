#!/usr/bin/env python3
"""
Debug script to see what OCR text was extracted from the PUC document
"""
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from ocr_pipeline.extractors.ocr_engine import MultiEngineOCR, OCREngine

def debug_ocr_extraction():
    """Debug what text is actually extracted from the document"""
    
    # Path to your uploaded document (adjust if needed)
    image_path = "data/uploads/8665be9a-5019-439b-a047-3a8013abcf88_12th MC (1).jpg"
    
    if not Path(image_path).exists():
        print(f"❌ Image not found at: {image_path}")
        # Try to find any recent upload
        uploads_dir = Path("data/uploads")
        if uploads_dir.exists():
            jpg_files = list(uploads_dir.glob("*12th*.jpg"))
            if jpg_files:
                image_path = str(jpg_files[0])
                print(f"📁 Found alternative image: {image_path}")
            else:
                print("❌ No 12th MC files found in uploads")
                return
        else:
            print("❌ Uploads directory not found")
            return
    
    print("🔍 Extracting OCR Text from PUC Document")
    print("=" * 60)
    
    try:
        # Initialize OCR engine
        ocr_engine = MultiEngineOCR([OCREngine.EASYOCR])
        
        # Extract text
        result = ocr_engine.extract_text(image_path, use_best_result=True)
        
        print(f"📄 OCR Engine Used: {result.engine_used.value}")
        print(f"🎯 Confidence: {result.confidence:.3f}")
        print(f"📏 Text Length: {len(result.text)} characters")
        print("\n" + "="*60)
        print("📝 EXTRACTED TEXT:")
        print("="*60)
        print(result.text)
        print("="*60)
        
        # Analyze the text for key patterns
        print("\n🧐 ANALYSIS:")
        print("-" * 30)
        
        lines = result.text.split('\n')
        print(f"📄 Total lines: {len(lines)}")
        
        # Look for key information
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Check for name patterns
            if any(pattern in line_clean.lower() for pattern in ['candidate', 'name', 'sanjan']):
                print(f"👤 Line {i+1} (Name related): {line_clean}")
            
            # Check for marks/subjects
            if any(pattern in line_clean.lower() for pattern in ['kannada', 'english', 'physics', 'chemistry', 'mathematics']):
                print(f"📚 Line {i+1} (Subject): {line_clean}")
            
            # Check for key identifiers
            if any(pattern in line_clean.lower() for pattern in ['400529', 'april', '2022', 'register']):
                print(f"🔢 Line {i+1} (ID/Date): {line_clean}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_ocr_extraction()