"""
Simple Web Interface for Gemini Document Processor
Clean, hackathon-ready interface for document processing
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

try:
    from flask import Flask, request, jsonify, render_template_string, flash
    import werkzeug.utils
except ImportError:
    raise ImportError("Flask not installed. Run: pip install flask")

from gemini_processor import create_processor
from document_schemas import DocumentSchemas

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎓 Smart Document Processor | MIT Hackathon</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: #333;
        }
        .container { 
            max-width: 1000px; margin: 0 auto; background: white; 
            border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; 
            padding: 30px; text-align: center;
        }
        .header h1 { margin: 0; font-size: 2.5em; font-weight: 700; }
        .header p { margin: 10px 0 0; opacity: 0.9; font-size: 1.1em; }
        
        .content { padding: 30px; }
        .upload-section { 
            background: #f8f9fa; border-radius: 15px; padding: 30px; margin-bottom: 30px;
            border: 2px dashed #dee2e6; transition: all 0.3s;
        }
        .upload-section:hover { border-color: #4CAF50; }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        input[type="file"] { 
            width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px;
            font-size: 16px; transition: border-color 0.3s;
        }
        input[type="file"]:focus { border-color: #4CAF50; outline: none; }
        
        select { 
            width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px;
            font-size: 16px; background: white;
        }
        
        .btn { 
            background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; 
            padding: 15px 30px; border: none; border-radius: 50px; font-size: 18px;
            cursor: pointer; transition: transform 0.3s; font-weight: 600;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        
        .result { 
            margin-top: 30px; padding: 30px; border-radius: 15px; 
            border-left: 5px solid #4CAF50;
        }
        .result.success { background: #e8f5e8; }
        .result.error { background: #ffebee; border-left-color: #f44336; }
        
        .result-header { display: flex; align-items: center; margin-bottom: 20px; }
        .result-header h3 { margin: 0; font-size: 1.5em; }
        .status-badge { 
            padding: 5px 15px; border-radius: 20px; font-size: 0.9em; margin-left: 15px;
            background: #4CAF50; color: white; font-weight: 600;
        }
        .status-badge.error { background: #f44336; }
        
        .metrics { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
        .metric { 
            background: white; padding: 15px; border-radius: 10px; text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); flex: 1; min-width: 150px;
        }
        .metric-value { font-size: 1.5em; font-weight: 700; color: #4CAF50; }
        .metric-label { font-size: 0.9em; color: #666; margin-top: 5px; }
        
        .json-display { 
            background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 10px; 
            padding: 20px; font-family: 'Courier New', monospace; white-space: pre-wrap;
            max-height: 500px; overflow-y: auto;
        }
        
        .validation-issues { margin-top: 20px; }
        .issue { 
            background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px;
            padding: 10px; margin-bottom: 10px; color: #856404;
        }
        
        .api-status { 
            background: #e3f2fd; border-radius: 10px; padding: 20px; margin-bottom: 30px;
        }
        .api-status h4 { margin-top: 0; color: #1976d2; }
        .status-item { display: flex; align-items: center; margin-bottom: 10px; }
        .status-icon { margin-right: 10px; font-size: 1.2em; }
        
        .features { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-top: 30px;
        }
        .feature { 
            background: #f8f9fa; border-radius: 10px; padding: 20px; text-align: center;
            border: 1px solid #e9ecef;
        }
        .feature h4 { color: #4CAF50; margin-bottom: 10px; }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2em; }
            .content { padding: 20px; }
            .metrics { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Smart Document Processor</h1>
            <p>AI-powered document extraction using Gemini 1.5 Flash | MIT Hackathon 2025</p>
        </div>
        
        <div class="content">
            <!-- API Status -->
            <div class="api-status">
                <h4>🔧 System Status</h4>
                <div class="status-item">
                    <span class="status-icon">{% if gemini_configured %}✅{% else %}❌{% endif %}</span>
                    <span>Gemini API: {% if gemini_configured %}Connected{% else %}Not configured{% endif %}</span>
                </div>
                {% if not gemini_configured %}
                <p><strong>⚠️ Setup Required:</strong> Set GEMINI_API_KEY environment variable</p>
                {% endif %}
            </div>
            
            <!-- Upload Form -->
            <div class="upload-section">
                <form method="POST" enctype="multipart/form-data" action="/process">
                    <div class="form-group">
                        <label for="document">📄 Select Document Image</label>
                        <input type="file" name="document" id="document" accept="image/*" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="doc_type">📋 Document Type (optional - auto-detect if not selected)</label>
                        <select name="doc_type" id="doc_type">
                            <option value="">🔍 Auto-detect</option>
                            <option value="aadhaar_card">🆔 Aadhaar Card</option>
                            <option value="marksheet_10th">📜 10th Marksheet</option>
                            <option value="marksheet_12th">📜 12th Marksheet</option>
                            <option value="transfer_certificate">📄 Transfer Certificate</option>
                            <option value="migration_certificate">🎓 Migration Certificate</option>
                            <option value="entrance_scorecard">📊 Entrance Scorecard</option>
                            <option value="admit_card">🎫 Admit Card</option>
                            <option value="caste_certificate">📋 Caste Certificate</option>
                            <option value="domicile_certificate">🏠 Domicile Certificate</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn">🚀 Process Document</button>
                </form>
            </div>
            
            <!-- Results -->
            {% if result %}
            <div class="result {% if result.success %}success{% else %}error{% endif %}">
                <div class="result-header">
                    <h3>Processing Result</h3>
                    <span class="status-badge {% if not result.success %}error{% endif %}">
                        {% if result.success %}✅ SUCCESS{% else %}❌ FAILED{% endif %}
                    </span>
                </div>
                
                {% if result.success %}
                <!-- Metrics -->
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{{ result.document_type.replace('_', ' ').title() }}</div>
                        <div class="metric-label">Document Type</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ "%.0f"|format(result.confidence_score * 100) }}%</div>
                        <div class="metric-label">Confidence</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ "%.2f"|format(result.processing_time) }}s</div>
                        <div class="metric-label">Processing Time</div>
                    </div>
                </div>
                
                <!-- Extracted Data -->
                <h4>📋 Extracted Data</h4>
                <div class="json-display">{{ result.extracted_data | tojson(indent=2) }}</div>
                
                <!-- Validation Issues -->
                {% if result.validation_issues %}
                <div class="validation-issues">
                    <h4>⚠️ Validation Issues</h4>
                    {% for issue in result.validation_issues %}
                    <div class="issue">{{ issue }}</div>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% else %}
                <p><strong>Error:</strong> {{ result.error_message }}</p>
                {% endif %}
            </div>
            {% endif %}
            
            <!-- Features -->
            <div class="features">
                <div class="feature">
                    <h4>🤖 AI-Powered</h4>
                    <p>Uses Gemini 1.5 Flash for direct image-to-JSON extraction without separate OCR</p>
                </div>
                <div class="feature">
                    <h4>⚡ Fast Processing</h4>
                    <p>Typically processes documents in 2-5 seconds with high accuracy</p>
                </div>
                <div class="feature">
                    <h4>🎯 Smart Validation</h4>
                    <p>Automatically validates extracted data and flags missing fields</p>
                </div>
                <div class="feature">
                    <h4>📱 Multiple Types</h4>
                    <p>Supports all major Indian documents: Aadhaar, marksheets, certificates</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // File upload preview
        document.getElementById('document').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                console.log('File selected:', e.target.files[0].name);
            }
        });
    </script>
</body>
</html>
'''

# Global processor instance
processor = None

def init_processor():
    """Initialize Gemini processor"""
    global processor
    if processor is None:
        try:
            processor = create_processor()
            return True
        except Exception as e:
            print(f"Failed to initialize processor: {e}")
            return False
    return True

@app.route('/')
def index():
    """Home page"""
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    return render_template_string(HTML_TEMPLATE, 
                                result=None, 
                                gemini_configured=gemini_configured)

@app.route('/process', methods=['POST'])
def process_document():
    """Process uploaded document"""
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    
    if not init_processor():
        return render_template_string(HTML_TEMPLATE, 
                                    result={'success': False, 'error_message': 'Processor initialization failed'},
                                    gemini_configured=gemini_configured)
    
    try:
        # Get uploaded file
        if 'document' not in request.files:
            raise ValueError("No document uploaded")
        
        file = request.files['document']
        if file.filename == '':
            raise ValueError("No file selected")
        
        # Get document type
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
            result = processor.process_document(str(temp_path), doc_type)
            
            # Convert to dict for template
            result_dict = {
                'success': result.success,
                'document_type': result.document_type,
                'extracted_data': result.extracted_data,
                'processing_time': result.processing_time,
                'validation_issues': result.validation_issues,
                'confidence_score': result.confidence_score,
                'error_message': result.error_message
            }
            
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
        
        return render_template_string(HTML_TEMPLATE, 
                                    result=result_dict,
                                    gemini_configured=gemini_configured)
        
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, 
                                    result={'success': False, 'error_message': str(e)},
                                    gemini_configured=gemini_configured)

@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for programmatic access"""
    if not init_processor():
        return jsonify({'error': 'Processor initialization failed'}), 500
    
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
            result = processor.process_document(str(temp_path), doc_type)
            
            return jsonify({
                'success': result.success,
                'document_type': result.document_type,
                'extracted_data': result.extracted_data,
                'processing_time': result.processing_time,
                'validation_issues': result.validation_issues,
                'confidence_score': result.confidence_score,
                'error_message': result.error_message
            })
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/schemas')
def get_schemas():
    """Get all document schemas"""
    schemas = DocumentSchemas.get_all_schemas()
    return jsonify({
        doc_type: {
            'description': schema.description,
            'required_fields': schema.required_fields,
            'optional_fields': schema.optional_fields,
            'validation_rules': schema.validation_rules
        }
        for doc_type, schema in schemas.items()
    })

if __name__ == '__main__':
    print("🚀 Starting Smart Document Processor...")
    print("📱 Web interface will be available at: http://127.0.0.1:5000")
    print("📋 API endpoint: http://127.0.0.1:5000/api/process")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables")
        print("   Set it with: set GEMINI_API_KEY=your_api_key_here")
    
    app.run(debug=True, host='127.0.0.1', port=5000)