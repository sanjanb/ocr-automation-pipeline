"""
Simple Web Interface for API-Only Document Processor
Lightweight Flask app for document upload and processing
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

try:
    from flask import Flask, request, jsonify, render_template_string, redirect, url_for
    import werkzeug
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available. Install flask for web interface")

from .api_only_processor import create_api_only_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>API-Only Document Processor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
        .result { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .success { border-left: 4px solid #4CAF50; }
        .error { border-left: 4px solid #f44336; }
        .processing { color: #2196F3; }
        pre { background: white; padding: 10px; border-radius: 3px; overflow-x: auto; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        .metadata { font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <h1>📄 API-Only Document Processor</h1>
    <p>Upload document images for automated text extraction and data parsing using AI APIs.</p>
    
    <div class="upload-area">
        <form action="/process" method="post" enctype="multipart/form-data">
            <h3>Select Document Image</h3>
            <input type="file" name="document" accept="image/*" required>
            <br><br>
            
            <label for="doc_type">Document Type (optional):</label>
            <select name="doc_type" id="doc_type">
                <option value="">Auto-detect</option>
                <option value="marksheet_10th">10th Marksheet</option>
                <option value="marksheet_12th">12th Marksheet</option>
                <option value="entrance_scorecard">Entrance Scorecard</option>
                <option value="admit_card">Admit Card</option>
                <option value="caste_certificate">Caste Certificate</option>
                <option value="aadhar_card">Aadhar Card</option>
                <option value="transfer_certificate">Transfer Certificate</option>
                <option value="migration_certificate">Migration Certificate</option>
                <option value="domicile_certificate">Domicile Certificate</option>
            </select>
            <br><br>
            
            <button type="submit">🚀 Process Document</button>
        </form>
    </div>
    
    {% if result %}
    <div class="result {% if result.success %}success{% else %}error{% endif %}">
        <h3>{% if result.success %}✅ Processing Complete{% else %}❌ Processing Failed{% endif %}</h3>
        
        {% if result.success %}
        <div class="metadata">
            <strong>Document Type:</strong> {{ result.document_type }}<br>
            <strong>Confidence:</strong> {{ "%.1f"|format(result.confidence * 100) }}%<br>
            <strong>Processing Time:</strong> {{ "%.2f"|format(result.processing_time) }}s<br>
            <strong>Method:</strong> {{ result.method_used }}
        </div>
        
        <h4>📋 Extracted Data:</h4>
        <pre>{{ result.extracted_data | tojson(indent=2) }}</pre>
        
        {% if result.metadata %}
        <h4>🔍 Processing Details:</h4>
        <pre>{{ result.metadata | tojson(indent=2) }}</pre>
        {% endif %}
        
        {% else %}
        <p><strong>Error:</strong> {{ result.error_message }}</p>
        {% endif %}
    </div>
    {% endif %}
    
    <div style="margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
        <h3>🔧 API Configuration</h3>
        <p><strong>Gemini API:</strong> {% if gemini_configured %}✅ Configured{% else %}❌ Missing API key{% endif %}</p>
        <p><strong>OCR.space API:</strong> {% if ocr_space_configured %}✅ Configured{% else %}⚠️ Optional (using Gemini vision){% endif %}</p>
        
        {% if not gemini_configured %}
        <div style="background: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0;">
            <strong>⚠️ Configuration Required:</strong><br>
            Set your Gemini API key in the environment variable <code>GEMINI_API_KEY</code> or <code>gemini_api_key</code>
        </div>
        {% endif %}
    </div>
    
    <div style="margin-top: 20px; color: #666; font-size: 0.9em;">
        <p>📚 <strong>Supported Documents:</strong> Academic marksheets, entrance scorecards, certificates, ID cards</p>
        <p>🔒 <strong>Privacy:</strong> Documents processed via secure APIs, not stored locally</p>
        <p>⚡ <strong>Performance:</strong> Lightweight processing using cloud APIs only</p>
    </div>
</body>
</html>
"""

class DocumentProcessorApp:
    """Simple Flask web app for document processing"""
    
    def __init__(self):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not installed. Run: pip install flask")
        
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        
        # Initialize processor
        try:
            self.processor = create_api_only_processor()
            self.processor_available = True
        except Exception as e:
            logger.error(f"Failed to initialize processor: {e}")
            self.processor_available = False
            self.processor_error = str(e)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE, 
                                        result=None,
                                        gemini_configured=bool(os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")),
                                        ocr_space_configured=bool(os.getenv("OCR_SPACE_API_KEY")))
        
        @self.app.route('/process', methods=['POST'])
        def process_document():
            if not self.processor_available:
                return render_template_string(HTML_TEMPLATE, 
                                            result={
                                                'success': False,
                                                'error_message': f'Processor not available: {self.processor_error}'
                                            },
                                            gemini_configured=False,
                                            ocr_space_configured=False)
            
            try:
                # Get uploaded file
                if 'document' not in request.files:
                    raise ValueError("No document uploaded")
                
                file = request.files['document']
                if file.filename == '':
                    raise ValueError("No file selected")
                
                # Get document type hint
                doc_type = request.form.get('doc_type', '').strip() or None
                
                # Save uploaded file temporarily
                temp_dir = Path("temp_uploads")
                temp_dir.mkdir(exist_ok=True)
                
                filename = werkzeug.utils.secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_path = temp_dir / f"{timestamp}_{filename}"
                
                file.save(temp_path)
                
                try:
                    # Process document
                    result = self.processor.process_document(str(temp_path), doc_type)
                    
                    # Convert to dict for template
                    result_dict = {
                        'success': result.success,
                        'document_type': result.document_type,
                        'extracted_data': result.extracted_data,
                        'confidence': result.confidence,
                        'processing_time': result.processing_time,
                        'method_used': result.method_used,
                        'error_message': result.error_message,
                        'metadata': result.metadata
                    }
                    
                finally:
                    # Clean up temp file
                    if temp_path.exists():
                        temp_path.unlink()
                
                return render_template_string(HTML_TEMPLATE, 
                                            result=result_dict,
                                            gemini_configured=bool(os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")),
                                            ocr_space_configured=bool(os.getenv("OCR_SPACE_API_KEY")))
                
            except Exception as e:
                logger.error(f"Processing error: {e}")
                return render_template_string(HTML_TEMPLATE, 
                                            result={
                                                'success': False,
                                                'error_message': str(e)
                                            },
                                            gemini_configured=bool(os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")),
                                            ocr_space_configured=bool(os.getenv("OCR_SPACE_API_KEY")))
        
        @self.app.route('/api/process', methods=['POST'])
        def api_process():
            """API endpoint for programmatic access"""
            if not self.processor_available:
                return jsonify({'error': f'Processor not available: {self.processor_error}'}), 500
            
            try:
                file = request.files.get('document')
                if not file:
                    return jsonify({'error': 'No document provided'}), 400
                
                doc_type = request.form.get('doc_type')
                
                # Save and process
                temp_dir = Path("temp_uploads")
                temp_dir.mkdir(exist_ok=True)
                
                filename = werkzeug.utils.secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_path = temp_dir / f"{timestamp}_{filename}"
                
                file.save(temp_path)
                
                try:
                    result = self.processor.process_document(str(temp_path), doc_type)
                    
                    return jsonify({
                        'success': result.success,
                        'document_type': result.document_type,
                        'extracted_data': result.extracted_data,
                        'confidence': result.confidence,
                        'processing_time': result.processing_time,
                        'method_used': result.method_used,
                        'error_message': result.error_message,
                        'metadata': result.metadata
                    })
                    
                finally:
                    if temp_path.exists():
                        temp_path.unlink()
                        
            except Exception as e:
                logger.error(f"API processing error: {e}")
                return jsonify({'error': str(e)}), 500
    
    def run(self, host='127.0.0.1', port=5000, debug=True):
        """Run the Flask app"""
        self.app.run(host=host, port=port, debug=debug)

def create_app():
    """Factory function to create Flask app"""
    return DocumentProcessorApp()

if __name__ == '__main__':
    app = create_app()
    app.run()