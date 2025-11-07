#!/bin/bash

# Legal AI Assistant - Setup Script
echo "Setting up Legal AI Assistant..."

# Create directory structure
echo "Creating directory structure..."
mkdir -p utils
mkdir -p generators
mkdir -p documents
mkdir -p templates/rajasthan
mkdir -p uploads

# Check if Python is installed (try python3 first, then python)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Found Python: $PYTHON_CMD"

# Check Python version (require 3.8+)
python_version=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python version $python_version is too old. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version: $python_version"

# Check if pip is available (will use pip from venv after activation)
PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "WARNING: pip not found in PATH, will use pip from venv after creation"
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found. Please create it with required dependencies."
    exit 1
fi

# Deactivate any existing virtual environment if active
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating existing virtual environment..."
    deactivate 2>/dev/null || true
fi

# Remove old virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "Creating new virtual environment..."
$PYTHON_CMD -m venv venv

# Verify virtual environment was created
if [ ! -d "venv" ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
# Check OS and use appropriate activation script
if [ -f "venv/bin/activate" ]; then
    # Linux/Mac
source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
else
    echo "ERROR: Virtual environment activation script not found"
    exit 1
fi

# Upgrade pip using python -m pip install --upgrade pip
echo "Upgrading pip..."
VENV_PYTHON_UPGRADE=""
if [ -f "venv/bin/python" ]; then
    VENV_PYTHON_UPGRADE="venv/bin/python"
elif [ -f "venv/Scripts/python.exe" ]; then
    VENV_PYTHON_UPGRADE="venv/Scripts/python.exe"
elif [ -f "venv/Scripts/python" ]; then
    VENV_PYTHON_UPGRADE="venv/Scripts/python"
fi

if [ -n "$VENV_PYTHON_UPGRADE" ]; then
    echo "   Using: $VENV_PYTHON_UPGRADE -m pip install --upgrade pip"
    $VENV_PYTHON_UPGRADE -m pip install --upgrade pip --quiet
else
    echo "   Using: $PYTHON_CMD -m pip install --upgrade pip"
    $PYTHON_CMD -m pip install --upgrade pip --quiet
fi

# Read requirements.txt and check each package
echo "Checking and installing dependencies from requirements.txt..."
missing_packages=0

while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    
    # Extract package name (remove version specifiers)
    package_name=$(echo "$line" | sed -E 's/^([^=<>!]+).*/\1/' | xargs)
    
    if [ -z "$package_name" ]; then
                continue
    fi
    
    echo "  Checking $package_name..."
    
    # Get the correct import name for checking
    import_name="${package_name//-/_}"
    if [ "$package_name" = "python-docx" ]; then
        import_name="docx"
    elif [ "$package_name" = "python-dateutil" ]; then
        import_name="dateutil"
    fi
    
    # Check if package is installed (use python from venv if available)
    VENV_PYTHON_CHECK="python"
    if [ -f "venv/bin/python" ]; then
        VENV_PYTHON_CHECK="venv/bin/python"
    elif [ -f "venv/Scripts/python.exe" ]; then
        VENV_PYTHON_CHECK="venv/Scripts/python.exe"
    elif [ -f "venv/Scripts/python" ]; then
        VENV_PYTHON_CHECK="venv/Scripts/python"
    fi
    
    if ! $VENV_PYTHON_CHECK -c "import $import_name" 2>/dev/null; then
        echo "  WARNING: $package_name not found, will install..."
        missing_packages=$((missing_packages + 1))
    else
        echo "  OK: $package_name is already installed"
    fi
done < requirements.txt

# Install all dependencies from requirements.txt
echo ""
echo "Installing all packages from requirements.txt..."
if [ -n "$VENV_PIP" ]; then
    $VENV_PIP install -r requirements.txt
else
    $PIP_CMD install -r requirements.txt
fi

# Verify all packages are installed
echo ""
echo "Verifying all packages are installed..."
all_installed=true

# Map package names to their import names
get_import_name() {
    local pkg_name="$1"
    case "$pkg_name" in
        python-docx)
            echo "docx"
            ;;
        python-dateutil)
            echo "dateutil"
            ;;
        *)
            echo "${pkg_name//-/_}"
            ;;
    esac
}

while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    
    # Extract package name (remove version specifiers)
    package_name=$(echo "$line" | sed -E 's/^([^=<>!]+).*/\1/' | xargs)
    
    if [ -z "$package_name" ]; then
        continue
    fi
    
    # Get the correct import name
    import_name=$(get_import_name "$package_name")
    
    # Try to import the package (use python from venv)
    VENV_PYTHON=""
    if [ -f "venv/bin/python" ]; then
        VENV_PYTHON="venv/bin/python"
    elif [ -f "venv/Scripts/python.exe" ]; then
        VENV_PYTHON="venv/Scripts/python.exe"
    elif [ -f "venv/Scripts/python" ]; then
        VENV_PYTHON="venv/Scripts/python"
    else
        VENV_PYTHON="python"
    fi
    
    if $VENV_PYTHON -c "import $import_name" 2>/dev/null; then
        echo "OK: $package_name is installed"
    else
        echo "ERROR: $package_name is NOT installed"
        all_installed=false
    fi
done < requirements.txt

if [ "$all_installed" = false ]; then
    echo ""
    echo "ERROR: Some packages failed to install. Please check the errors above."
    exit 1
fi

# Create __init__.py files for Python packages if they don't exist
echo "Creating Python package files..."
[ ! -f "utils/__init__.py" ] && touch utils/__init__.py && echo "Created utils/__init__.py"
[ ! -f "generators/__init__.py" ] && touch generators/__init__.py && echo "Created generators/__init__.py"
[ ! -f "documents/__init__.py" ] && touch documents/__init__.py && echo "Created documents/__init__.py"

# Verify critical files exist
echo ""
echo "Verifying project structure..."
missing_files=0

critical_files=(
    "main.py"
    "requirements.txt"
    "utils/parser.py"
    "generators/birth_certificate.py"
    "generators/marriage_certificate.py"
    "documents/document_reader.py"
    "documents/upload_handler.py"
    "templates/rajasthan/birth_certificate.json"
    "templates/rajasthan/marriage_certificate_application.json"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "OK: $file exists"
    else
        echo "WARNING: $file is missing"
        missing_files=$((missing_files + 1))
    fi
done

# Additional verification (packages already checked above, this is just a summary)
echo ""
echo "All packages from requirements.txt verified"

# Summary
echo ""
if [ $missing_files -eq 0 ] && [ "$all_installed" = true ]; then
    echo "Setup completed successfully!"
    echo ""
    echo "Starting Streamlit application..."
    echo ""
    
    # Verify virtual environment exists
    if [ ! -d "venv" ]; then
        echo "ERROR: Virtual environment not found. Please run the setup script again."
        exit 1
    fi
    
    # Activate virtual environment (if not already active)
    if [ -z "$VIRTUAL_ENV" ]; then
        # Check OS and use appropriate activation script
        if [ -f "venv/bin/activate" ]; then
            # Linux/Mac
            source venv/bin/activate
        elif [ -f "venv/Scripts/activate" ]; then
            # Windows
            source venv/Scripts/activate
        else
            echo "ERROR: Virtual environment activation script not found"
            exit 1
        fi
    fi
    
    # Verify streamlit is available (check in venv)
    STREAMLIT_CMD=""
    if [ -f "venv/bin/streamlit" ]; then
        STREAMLIT_CMD="venv/bin/streamlit"
    elif [ -f "venv/Scripts/streamlit.exe" ]; then
        STREAMLIT_CMD="venv/Scripts/streamlit.exe"
    elif [ -f "venv/Scripts/streamlit" ]; then
        STREAMLIT_CMD="venv/Scripts/streamlit"
    elif command -v streamlit &> /dev/null; then
        STREAMLIT_CMD="streamlit"
    else
        echo "ERROR: Streamlit command not found. Please ensure all packages are installed."
        echo "   Try running: source venv/bin/activate (or venv\\Scripts\\activate on Windows)"
        echo "   Then run: pip install -r requirements.txt"
        exit 1
    fi
    
    # Run the Streamlit application
    echo "Starting Streamlit server..."
    $STREAMLIT_CMD run main.py
else
    echo "WARNING: Setup completed with issues. Please review the warnings above."
    if [ "$all_installed" = false ]; then
        echo "ERROR: Some packages are not installed correctly."
    fi
    if [ $missing_files -gt 0 ]; then
        echo "ERROR: Some critical files are missing."
    fi
    exit 1
fi





