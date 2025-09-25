@echo off
REM OCR Automation Pipeline Setup Script for Windows
REM MIT Hackathon Project

echo Setting up OCR Automation Pipeline for MIT Hackathon...

REM Check Python version
python --version
if errorlevel 1 (
    echo Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Download spaCy model
echo Downloading spaCy English model...
python -m spacy download en_core_web_sm

REM Create necessary directories
echo Creating necessary directories...
if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\temp" mkdir "data\temp"
if not exist "logs" mkdir "logs"
if not exist "models\trained" mkdir "models\trained"

echo ✅ Setup complete! Virtual environment is ready.
echo To activate the environment, run:
echo   venv\Scripts\activate

pause