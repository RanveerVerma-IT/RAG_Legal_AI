# PDF Conversion Guide

## Overview

The system now converts filled DOCX documents directly to PDF to maintain proper formatting and alignment. This ensures the PDF looks exactly like the DOCX version.

## Conversion Methods (Priority Order)

### 1. **docx2pdf (Windows - Recommended)**
- **How it works**: Uses Microsoft Word COM automation
- **Pros**: 
  - Perfect formatting preservation
  - Maintains all styles, fonts, and layouts
  - Fast conversion
- **Cons**: 
  - Windows only
  - Requires Microsoft Word installed
- **Status**: Primary method on Windows

### 2. **LibreOffice (Cross-platform)**
- **How it works**: Uses LibreOffice headless mode
- **Pros**:
  - Works on Windows, Linux, Mac
  - Good formatting preservation
  - Free and open-source
- **Cons**:
  - Requires LibreOffice installation
  - Slightly slower than docx2pdf
- **Status**: Fallback for non-Windows or when Word not available

### 3. **ReportLab (Fallback)**
- **How it works**: Creates PDF from scratch using document content
- **Pros**:
  - No external dependencies
  - Always available
- **Cons**:
  - May lose some formatting
  - Different layout from DOCX
- **Status**: Last resort fallback

## Installation

### Windows (Recommended)

1. **Install docx2pdf**:
```bash
pip install docx2pdf
```

2. **Ensure Microsoft Word is installed**:
   - docx2pdf uses Word COM automation
   - Any version of Microsoft Word works
   - Office 365, Office 2019, 2016, etc.

### Linux/Mac (Alternative)

1. **Install LibreOffice**:

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

**Mac (Homebrew)**:
```bash
brew install --cask libreoffice
```

**Fedora/RHEL**:
```bash
sudo dnf install libreoffice
```

2. **Verify installation**:
```bash
soffice --version
```

## How It Works

### Conversion Flow

```
1. User requests document generation
2. System fills DOCX template with data
3. DOCX bytes are saved in memory
4. Conversion attempts:
   a. Try docx2pdf (if Windows + Word)
   b. Try LibreOffice (if installed)
   c. Fallback to ReportLab
5. PDF bytes returned to user
6. Both DOCX and PDF available for download
```

### Code Flow

```python
# In template_document_generator.py

def generate_document():
    # 1. Fill DOCX template
    doc = Document(template_path)
    # ... replace placeholders ...
    docx_bytes = save_to_bytes(doc)
    
    # 2. Convert to PDF
    pdf_bytes = _convert_to_pdf(doc, docx_bytes)
    
    # 3. Return both formats
    return GeneratedDocument(
        document_bytes=docx_bytes,
        pdf_bytes=pdf_bytes,
        ...
    )
```

## Troubleshooting

### PDF Not Generated (Windows)

**Problem**: PDF download button not appearing

**Solutions**:
1. Check if Microsoft Word is installed
2. Install docx2pdf: `pip install docx2pdf`
3. Check logs for error messages
4. Try opening Word manually to ensure it works

### PDF Not Generated (Linux/Mac)

**Problem**: PDF download button not appearing

**Solutions**:
1. Install LibreOffice (see installation above)
2. Verify: `soffice --version`
3. Check if `soffice` is in PATH
4. Check logs for error messages

### PDF Formatting Different from DOCX

**Problem**: PDF looks different from DOCX

**Possible Causes**:
1. Using ReportLab fallback (check logs)
2. Missing fonts in LibreOffice
3. Complex formatting not supported

**Solutions**:
1. Install docx2pdf (Windows) for best results
2. Install missing fonts on system
3. Simplify template formatting
4. Use DOCX download instead

### Conversion Timeout

**Problem**: PDF generation takes too long

**Solutions**:
1. Increase timeout in code (currently 30 seconds)
2. Check system resources
3. Simplify document template
4. Use DOCX download instead

## Performance

### Conversion Times (Approximate)

| Method | Time | Quality |
|--------|------|---------|
| docx2pdf | 1-3 seconds | Excellent |
| LibreOffice | 3-5 seconds | Good |
| ReportLab | <1 second | Fair |

### File Sizes (Approximate)

| Format | Size |
|--------|------|
| DOCX | 30-50 KB |
| PDF (docx2pdf) | 50-100 KB |
| PDF (LibreOffice) | 50-100 KB |
| PDF (ReportLab) | 2-5 KB |

## Configuration

### Adjust Timeout

Edit `generators/template_document_generator.py`:

```python
# In _convert_with_libreoffice method
result = subprocess.run(
    [...],
    timeout=30  # Change to 60 for slower systems
)
```

### Disable PDF Generation

Edit `config.py`:

```python
ENABLE_PDF_GENERATION = False  # Add this flag
```

Then update code to check this flag.

### Force Specific Method

Edit `_convert_to_pdf` method to skip certain methods:

```python
def _convert_to_pdf(...):
    # Skip docx2pdf
    # if DOCX2PDF_SUPPORT:
    #     ...
    
    # Use only LibreOffice
    return self._convert_with_libreoffice(docx_bytes)
```

## Logs

Check logs to see which conversion method was used:

```
INFO:generators.template_document_generator:Converting to PDF using docx2pdf (preserves formatting)
INFO:generators.template_document_generator:PDF conversion successful: 85432 bytes
```

Or:

```
INFO:generators.template_document_generator:Attempting PDF conversion with LibreOffice
INFO:generators.template_document_generator:Trying LibreOffice command: soffice
INFO:generators.template_document_generator:LibreOffice conversion successful: 92156 bytes
```

Or (fallback):

```
WARNING:generators.template_document_generator:Using ReportLab fallback - formatting may differ from DOCX
```

## Best Practices

### For Windows Users
1. Install Microsoft Word (any version)
2. Install docx2pdf: `pip install docx2pdf`
3. Enjoy perfect PDF formatting!

### For Linux/Mac Users
1. Install LibreOffice
2. Add to PATH if needed
3. Test with: `soffice --version`

### For All Users
1. Always test PDF output with your templates
2. Keep templates simple for best compatibility
3. Use standard fonts (Arial, Times New Roman, etc.)
4. Avoid complex formatting if possible
5. DOCX is always available as fallback

## Future Enhancements

Potential improvements:
1. **Cloud conversion**: Use online API for conversion
2. **Caching**: Cache converted PDFs
3. **Batch conversion**: Convert multiple documents at once
4. **Custom fonts**: Bundle fonts with application
5. **Preview**: Show PDF preview before download
6. **Compression**: Compress PDFs to reduce size

## Support

If PDF conversion fails:
1. Check logs for error messages
2. Verify dependencies are installed
3. Try DOCX download (always works)
4. Report issue with logs and template

## Summary

The system now prioritizes direct DOCX-to-PDF conversion to maintain formatting:
- ✅ Windows: Uses Microsoft Word (perfect formatting)
- ✅ Linux/Mac: Uses LibreOffice (good formatting)
- ✅ Fallback: Uses ReportLab (basic formatting)
- ✅ Both DOCX and PDF available for download
- ✅ Automatic method selection
- ✅ Graceful degradation
