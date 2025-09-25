#!/usr/bin/env python3
"""
OCR Automation Pipeline Demo Startup Script
MIT Hackathon Project

This script starts the web application with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the OCR automation pipeline web application"""
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    web_app_dir = script_dir
    
    # Change to the web app directory
    os.chdir(web_app_dir)
    
    # Add the src directory to Python path
    src_dir = project_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    print("Starting OCR Automation Pipeline Web Application...")
    print(f"Project root: {project_root}")
    print(f"Web app directory: {web_app_dir}")
    print(f"Source directory: {src_dir}")
    print()
    print("Web Interface: http://localhost:8000")
    print("API Documentation: http://localhost:8000/api/docs")
    print("Alternative API Docs: http://localhost:8000/api/redoc")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Import and run the FastAPI app
        from app import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have activated the virtual environment and installed dependencies")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()