"""
Simple CLI for API-Only Document Processor
Command line interface for document processing
"""

import os
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

from .api_only_processor import create_api_only_processor, DocumentResult

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def process_single_document(processor, image_path: str, doc_type: Optional[str] = None) -> DocumentResult:
    """Process a single document"""
    print(f"📄 Processing: {image_path}")
    
    if doc_type:
        print(f"📋 Document type: {doc_type}")
    else:
        print("🔍 Auto-detecting document type...")
    
    result = processor.process_document(image_path, doc_type)
    
    # Print results
    if result.success:
        print(f"✅ Success! Processed in {result.processing_time:.2f}s")
        print(f"📊 Document Type: {result.document_type}")
        print(f"🎯 Confidence: {result.confidence:.1%}")
        print(f"⚙️ Method: {result.method_used}")
        print("\n📋 Extracted Data:")
        print(json.dumps(result.extracted_data, indent=2, ensure_ascii=False))
        
        if result.metadata:
            print(f"\n🔍 Processing Details:")
            print(json.dumps(result.metadata, indent=2))
    else:
        print(f"❌ Failed: {result.error_message}")
        print(f"⏱️ Processing time: {result.processing_time:.2f}s")
    
    return result

def process_directory(processor, directory_path: str, doc_type: Optional[str] = None):
    """Process all images in a directory"""
    directory = Path(directory_path)
    if not directory.exists() or not directory.is_dir():
        print(f"❌ Directory not found: {directory_path}")
        return
    
    # Find image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = [
        f for f in directory.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"❌ No image files found in: {directory_path}")
        return
    
    print(f"📁 Found {len(image_files)} image(s) in directory")
    print("=" * 60)
    
    results = []
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}]")
        result = process_single_document(processor, str(image_file), doc_type)
        results.append((str(image_file), result))
        print("-" * 60)
    
    # Summary
    successful = sum(1 for _, r in results if r.success)
    print(f"\n📊 Processing Summary:")
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {len(results) - successful}/{len(results)}")
    
    avg_time = sum(r.processing_time for _, r in results) / len(results)
    print(f"⏱️ Average time: {avg_time:.2f}s")

def save_results_to_file(results: list, output_path: str):
    """Save results to JSON file"""
    output_data = []
    for file_path, result in results:
        output_data.append({
            'file_path': file_path,
            'success': result.success,
            'document_type': result.document_type,
            'extracted_data': result.extracted_data,
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'method_used': result.method_used,
            'error_message': result.error_message,
            'metadata': result.metadata
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_path}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='API-Only Document Processor CLI')
    
    # Input options
    parser.add_argument('path', help='Path to image file or directory')
    parser.add_argument('--type', '-t', dest='doc_type', 
                       choices=[
                           'marksheet_10th', 'marksheet_12th', 'entrance_scorecard',
                           'admit_card', 'caste_certificate', 'aadhar_card',
                           'transfer_certificate', 'migration_certificate', 'domicile_certificate'
                       ],
                       help='Document type (optional, will auto-detect if not specified)')
    
    # API configuration
    parser.add_argument('--gemini-key', help='Gemini API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--ocr-space-key', help='OCR.space API key (optional)')
    
    # Output options
    parser.add_argument('--output', '-o', help='Save results to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Check if path exists
    path = Path(args.path)
    if not path.exists():
        print(f"❌ Path not found: {args.path}")
        return 1
    
    try:
        # Create processor
        print("🚀 Initializing API-Only Document Processor...")
        processor = create_api_only_processor(
            gemini_api_key=args.gemini_key,
            ocr_space_api_key=args.ocr_space_key
        )
        print("✅ Processor initialized successfully")
        
        # Process documents
        results = []
        
        if path.is_file():
            # Single file
            result = process_single_document(processor, str(path), args.doc_type)
            results.append((str(path), result))
        else:
            # Directory
            process_directory(processor, str(path), args.doc_type)
        
        # Save results if requested
        if args.output and results:
            save_results_to_file(results, args.output)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())