#!/bin/bash

# OCR Automation Pipeline Setup Script
# MIT Hackathon Project

echo "Setting up OCR Automation Pipeline for MIT Hackathon..."

# Check Python version
python_version=$(python --version 2>&1)
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Create necessary directories
echo " Creating necessary directories..."
mkdir -p data/uploads
mkdir -p data/temp
mkdir -p logs
mkdir -p models/trained

echo "✅ Setup complete! Virtual environment is ready."
echo "To activate the environment, run:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  venv\\Scripts\\activate"
else
    echo "  source venv/bin/activate"
fi