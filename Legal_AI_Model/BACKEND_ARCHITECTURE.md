# Advanced Backend Architecture

## Overview

The system now features an intelligent document processing backend that dynamically analyzes DOCX templates, extracts required fields, matches user queries to templates, and generates filled documents with skip functionality.

## Key Features

### 1. **Dynamic Template Analysis**
- Automatically reads DOCX files from the `documents/` folder
- Identifies placeholders: `{{field_name}}`, `[field_name]`, `__field_name__`, `{field_name}`
- Infers field types (date, phone, email, address, text)
- No JSON configuration needed!

### 2. **Intelligent Query Processing**
- Analyzes user queries to extract document type and location
- Automatically extracts field values from the query (names, dates, addresses, etc.)
- Smart field matching with fuzzy logic and synonyms

### 3. **Skip Functionality**
- Users can skip any field by typing: "skip", "pass", "next", "leave blank"
- Skipped fields are left empty in the generated document
- Full flexibility in form completion

### 4. **Smart Field Matching**
- Compares extracted fields with required fields
- Handles field name variations (snake_case, camelCase, spaces)
- Semantic matching (groom ↔ husband, bride ↔ wife)
- Only asks for missing information

## Architecture Components

### Core Components

1. **Document Analyzer** (`documents/document_analyzer.py`)
   - Reads DOCX templates
   - Extracts placeholders from paragraphs, tables, headers, footers
   - Infers field types from context

2. **Template Matcher** (`documents/template_matcher.py`)
   - Finds matching templates in documents folder
   - Supports location-based prioritization
   - Fuzzy filename matching

3. **Query Analyzer** (`utils/query_analyzer.py`)
   - Parses user queries
   - Extracts document type, location, and field values
   - Integrates with existing IntentDetector and EntityExtractor

4. **Field Comparator** (`utils/field_comparator.py`)
   - Compares extracted vs required fields
   - Fuzzy matching with Levenshtein distance
   - Synonym support

5. **Data Collector** (`utils/data_collector.py`)
   - Manages interactive field collection
   - Generates contextual questions
   - Handles skip requests

6. **Document Generator** (`generators/template_document_generator.py`)
   - Fills DOCX templates with collected data
   - Preserves formatting
   - Handles skipped fields gracefully

7. **Document Processor** (`core/document_processor.py`)
   - Orchestrates the entire pipeline
   - Manages processing context
   - Comprehensive error handling

## How to Use

### Adding a New Document Template

1. Create a DOCX file with placeholders:
   ```
   Name: {{applicant_name}}
   Date of Birth: {{date_of_birth}}
   Address: {{address}}
   Phone: {{phone}}
   ```

2. Save it in the `documents/` folder with a descriptive name:
   ```
   Jaipur_Marriage_Registration_Form.docx
   Delhi_Birth_Certificate_Form.docx
   ```

3. That's it! The system will automatically:
   - Detect the document type from filename
   - Extract all placeholders
   - Infer field types
   - Generate appropriate questions

### User Flow Example

**User:** "I need a marriage registration form for Jaipur. My name is John Doe and my phone is 9876543210"

**System:**
- Finds: `Jaipur_Marriage_Registration_Form.docx`
- Extracts: name="John Doe", phone="9876543210"
- Identifies missing fields: bride_name, marriage_date, address
- Asks: "Please provide Bride Name or type 'skip' to leave blank"

**User:** "Jane Smith"

**System:** "Please provide Marriage Date (format: DD-MM-YYYY) or type 'skip' to leave blank"

**User:** "skip"

**System:** "Please provide Address (full address) or type 'skip' to leave blank"

**User:** "123 Main St, Jaipur"

**System:** "All required information collected. Generating your document now."

## Configuration

Edit `config.py` to customize:

```python
# Enable/disable new backend
ENABLE_DOCX_PROCESSING = True

# Placeholder patterns
PLACEHOLDER_PATTERNS = [
    r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}",  # {{field_name}}
    # Add more patterns...
]

# Field type keywords
FIELD_TYPE_KEYWORDS = {
    "date": ["date", "dob", "birth"],
    # Add more types...
}

# Skip keywords
SKIP_KEYWORDS = ["skip", "pass", "next"]
```

## Backward Compatibility

The system maintains full backward compatibility:
- Old JSON-based templates still work
- Set `ENABLE_DOCX_PROCESSING = False` to use only old backend
- Both systems can coexist

## Error Handling

Comprehensive error handling with:
- `TemplateNotFoundError`: No matching template
- `TemplateParseError`: Corrupted DOCX file
- `QueryAnalysisError`: Query parsing failed
- `ValidationError`: Invalid field value
- `GenerationError`: Document generation failed

All errors are logged and user-friendly messages are displayed.

## File Structure

```
Legal_AI_Model/
├── documents/
│   ├── document_analyzer.py       # NEW: Analyzes DOCX templates
│   ├── template_matcher.py        # NEW: Finds matching templates
│   ├── document_reader.py         # Existing
│   └── *.docx                     # Template files
├── core/
│   ├── document_processor.py      # NEW: Orchestration layer
│   ├── models.py                  # NEW: Data models
│   └── exceptions.py              # NEW: Custom exceptions
├── utils/
│   ├── query_analyzer.py          # NEW: Query analysis
│   ├── field_comparator.py        # NEW: Field matching
│   ├── data_collector.py          # NEW: Data collection
│   ├── entity_extractor.py        # Existing (enhanced)
│   └── intent_detector.py         # Existing
├── generators/
│   ├── template_document_generator.py  # NEW: DOCX generation
│   └── document_factory.py        # Existing
├── config.py                      # NEW: Configuration
└── main.py                        # Updated with new backend
```

## Next Steps

1. **Add More Templates**: Drop DOCX files in `documents/` folder
2. **Customize Questions**: Edit placeholder labels in templates
3. **Add Field Types**: Update `FIELD_TYPE_KEYWORDS` in config
4. **Test**: Try various queries and document types
5. **Monitor**: Check logs for any issues

## Benefits

✅ **No Code Changes Needed**: Just add DOCX templates
✅ **Intelligent**: Extracts data from queries automatically
✅ **Flexible**: Skip any field during collection
✅ **User-Friendly**: Clear questions with format hints
✅ **Robust**: Comprehensive error handling
✅ **Backward Compatible**: Works with existing system
