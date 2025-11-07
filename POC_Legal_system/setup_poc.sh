#!/bin/bash
# setup_poc.sh

echo "=== Legal Assistant POC Setup ==="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv legal_poc_env

# Activate environment
echo "Activating virtual environment..."
source legal_poc_env/Scripts/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install streamlit pandas numpy fpdf langchain chromadb sentence-transformers

# Create directories
echo "Creating necessary directories..."
mkdir -p data/documents
mkdir -p data/vector_db

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To run the POC:"
echo "1. source legal_poc_env/Scripts/activate"
echo "2. streamlit run main.py"
echo ""
echo "📁 The application will create PDF documents in the download section!"
echo "🌐 Open http://localhost:8501 in your browser after running the above commands."

