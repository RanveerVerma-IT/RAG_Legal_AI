#!/bin/bash
# run_poc.sh - Git Bash compatible setup and run script

echo "=========================================="
echo "Legal Assistant POC - Setup & Run"
echo "=========================================="
echo ""

# Detect Python command (Windows/Git Bash compatible)
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Error: Python not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✅ Using Python: $($PYTHON_CMD --version)"
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    echo "Please ensure you're in the correct directory"
    exit 1
fi

# Check and upgrade pip
echo "📦 Checking and upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip --quiet
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: pip upgrade failed, continuing anyway..."
fi
echo ""

# Remove existing environment if any
if [ -d "legal_poc_env" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf legal_poc_env
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
$PYTHON_CMD -m venv legal_poc_env
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create virtual environment"
    exit 1
fi
echo ""

# Activate virtual environment (Git Bash compatible)
echo "🔌 Activating virtual environment..."
if [ -f "legal_poc_env/Scripts/activate" ]; then
    # Windows/Git Bash
    source legal_poc_env/Scripts/activate
elif [ -f "legal_poc_env/bin/activate" ]; then
    # Linux/Mac
    source legal_poc_env/bin/activate
else
    echo "❌ Error: Could not find activation script"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Upgrade pip in virtual environment
echo "📦 Upgrading pip in virtual environment..."
pip install --upgrade pip --quiet
echo ""

# Install dependencies from requirements.txt
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/documents
mkdir -p data/vector_db
echo ""

echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "🚀 Starting Legal Assistant POC..."
echo "🌐 The application will open in your browser"
echo "📍 URL: http://localhost:8501 or http://localhost:8502"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit (Git Bash compatible)
if command -v streamlit &> /dev/null; then
    streamlit run main.py
else
    python -m streamlit run main.py
fi
