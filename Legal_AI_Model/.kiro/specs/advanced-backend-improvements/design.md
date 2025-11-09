# Design Document

## Overview

This design document outlines the architecture for an intelligent document processing backend system that dynamically analyzes DOCX templates from the documents folder, extracts required fields, matches user queries to templates, collects missing data interactively, and generates filled documents. The system eliminates the need for hardcoded JSON templates by directly analyzing document files.

## Architecture

### High-Level Architecture

```
User Query → Query Analyzer → Template Matcher → Document Analyzer
                                                         ↓
User ← Document Generator ← Data Collector ← Field Comparator
```

### Component Flow

1. **Query Analyzer**: Parses user input to extract document type, location, and any provided field values
2. **Template Matcher**: Searches documents folder for matching DOCX templates
3. **Document Analyzer**: Reads template structure and identifies all required fields with placeholders
4. **Field Comparator**: Compares extracted values against required fields to identify missing data
5. **Data Collector**: Interactively collects missing fields with skip functionality
6. **Document Generator**: Fills template with collected data and prepares for download

## Components and Interfaces

### 1. Query Analyzer Component

**Purpose**: Parse user queries to extract document intent and field values

**Class**: `QueryAnalyzer`

**Methods**:
- `analyze_query(user_input: str) -> QueryAnalysis`
  - Extracts document type keywords
  - Extracts location/state keywords
  - Extracts field values (names, dates, addresses, etc.)
  - Returns structured analysis object

**Data Structure**:
```python
@dataclass
class QueryAnalysis:
    document_type: Optional[str]
    location: Optional[str]
    extracted_fields: Dict[str, Any]
    confidence_score: float
```

**Integration Points**:
- Uses existing `IntentDetector` for document type detection
- Uses existing `EntityExtractor` for field extraction
- Extends both with fuzzy matching capabilities

### 2. Template Matcher Component

**Purpose**: Find matching document templates in the documents folder

**Class**: `TemplateMatcher`

**Methods**:
- `find_template(doc_type: str, location: str) -> Optional[Path]`
  - Searches documents folder for matching files
  - Supports fuzzy filename matching
  - Prioritizes location-specific templates
  - Returns template file path

- `list_available_templates() -> List[TemplateInfo]`
  - Scans documents folder
  - Returns list of available templates with metadata

- `get_template_metadata(template_path: Path) -> TemplateMetadata`
  - Extracts basic info from filename
  - Returns document type and location

**Data Structure**:
```python
@dataclass
class TemplateInfo:
    file_path: Path
    document_type: str
    location: Optional[str]
    file_size: int
    last_modified: datetime

@dataclass
class TemplateMetadata:
    document_type: str
    location: Optional[str]
    filename: str
```

**Matching Strategy**:
- Filename pattern matching (e.g., "Jaipur_Marriage_Registration_Form.docx")
- Keyword extraction from filename
- Location prefix matching
- Document type keyword matching

### 3. Document Analyzer Component

**Purpose**: Analyze DOCX templates to identify required fields and placeholders

**Class**: `DocumentAnalyzer`

**Methods**:
- `analyze_template(template_path: Path) -> TemplateStructure`
  - Opens DOCX file
  - Identifies placeholders in paragraphs and tables
  - Extracts field names and labels
  - Determines field types from context
  - Returns structured template information

- `extract_placeholders(doc: Document) -> List[Placeholder]`
  - Finds text patterns like {{field_name}}, [field_name], __field_name__
  - Extracts from paragraphs, tables, headers, footers
  - Returns list of unique placeholders

- `infer_field_type(field_name: str, context: str) -> str`
  - Analyzes field name and surrounding text
  - Infers type (text, date, phone, email, address, etc.)
  - Returns field type string

**Data Structure**:
```python
@dataclass
class Placeholder:
    field_name: str
    placeholder_text: str
    field_type: str
    label: Optional[str]
    required: bool
    location: str  # paragraph, table, header, footer

@dataclass
class TemplateStructure:
    template_path: Path
    placeholders: List[Placeholder]
    required_fields: List[str]
    optional_fields: List[str]
    document_metadata: Dict[str, Any]
```

**Placeholder Patterns**:
- `{{field_name}}` - Primary pattern
- `[field_name]` - Alternative pattern
- `__field_name__` - Alternative pattern
- `{field_name}` - Simple pattern

**Field Type Inference Rules**:
- Contains "date", "dob", "birth": → date
- Contains "phone", "mobile", "contact": → phone
- Contains "email", "mail": → email
- Contains "address", "residence": → address
- Contains "name": → text
- Default: → text

### 4. Field Comparator Component

**Purpose**: Compare extracted fields with required fields to identify missing data

**Class**: `FieldComparator`

**Methods**:
- `compare_fields(required: List[str], extracted: Dict[str, Any]) -> FieldComparison`
  - Matches extracted fields to required fields
  - Handles field name variations (e.g., "groom_name" vs "groomName")
  - Identifies missing fields
  - Returns comparison result

- `normalize_field_name(field_name: str) -> str`
  - Converts to standard format
  - Handles snake_case, camelCase, spaces
  - Returns normalized name

- `match_field_names(required_name: str, extracted_names: List[str]) -> Optional[str]`
  - Fuzzy matching between field names
  - Returns best match or None

**Data Structure**:
```python
@dataclass
class FieldComparison:
    matched_fields: Dict[str, Any]  # field_name: value
    missing_fields: List[str]
    skippable_fields: List[str]
    field_mapping: Dict[str, str]  # extracted_name: required_name
```

**Matching Strategy**:
- Exact match (case-insensitive)
- Normalized match (remove underscores, spaces)
- Fuzzy match (Levenshtein distance < 3)
- Semantic match (synonyms: "groom" ↔ "husband")

### 5. Data Collector Component

**Purpose**: Interactively collect missing field values from users

**Class**: `DataCollector`

**Methods**:
- `collect_missing_fields(missing: List[str], template_structure: TemplateStructure) -> Dict[str, Any]`
  - Iterates through missing fields
  - Generates contextual questions
  - Validates user input
  - Handles skip requests
  - Returns collected data

- `generate_question(field_name: str, field_type: str) -> str`
  - Creates user-friendly question
  - Includes format hints
  - Returns question string

- `validate_field_value(value: str, field_type: str) -> Tuple[bool, Optional[str], Any]`
  - Validates based on field type
  - Formats value appropriately
  - Returns (is_valid, error_message, formatted_value)

- `handle_skip(field_name: str) -> None`
  - Marks field as skipped
  - Logs skip action
  - Continues to next field

**Data Structure**:
```python
@dataclass
class CollectionState:
    missing_fields: List[str]
    current_field_index: int
    collected_data: Dict[str, Any]
    skipped_fields: List[str]
    validation_errors: Dict[str, str]
```

**Question Generation Templates**:
- Date fields: "Please provide {field_label} (format: DD-MM-YYYY)"
- Phone fields: "Please provide {field_label} (format: +91XXXXXXXXXX)"
- Email fields: "Please provide {field_label} (format: email@example.com)"
- Text fields: "Please provide {field_label}"
- Address fields: "Please provide {field_label} (full address)"

### 6. Document Generator Component

**Purpose**: Fill template with collected data and generate downloadable document

**Class**: `DocumentGenerator`

**Methods**:
- `generate_document(template_path: Path, field_data: Dict[str, Any], placeholders: List[Placeholder]) -> bytes`
  - Loads template DOCX
  - Replaces all placeholders with values
  - Handles skipped fields (leaves blank or default)
  - Preserves formatting
  - Returns document bytes

- `replace_placeholder(doc: Document, placeholder: Placeholder, value: Any) -> None`
  - Finds placeholder in document
  - Replaces with formatted value
  - Maintains styling

- `format_value(value: Any, field_type: str) -> str`
  - Formats value based on type
  - Handles dates, phones, etc.
  - Returns formatted string

- `generate_filename(doc_type: str, location: str, primary_field: str) -> str`
  - Creates descriptive filename
  - Includes key identifiers
  - Returns filename string

**Data Structure**:
```python
@dataclass
class GeneratedDocument:
    document_bytes: bytes
    filename: str
    document_type: str
    generation_timestamp: datetime
    fields_filled: List[str]
    fields_skipped: List[str]
```

**Replacement Strategy**:
- Search in paragraphs, tables, headers, footers
- Replace all occurrences of placeholder
- Preserve text formatting (bold, italic, font, size)
- Handle empty values gracefully

## Data Models

### Core Data Models

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

@dataclass
class DocumentRequest:
    """User's document generation request"""
    user_query: str
    session_id: str
    timestamp: datetime

@dataclass
class ProcessingContext:
    """Context maintained throughout processing"""
    request: DocumentRequest
    query_analysis: Optional[QueryAnalysis]
    template_path: Optional[Path]
    template_structure: Optional[TemplateStructure]
    field_comparison: Optional[FieldComparison]
    collected_data: Dict[str, Any]
    collection_state: Optional[CollectionState]
    generated_document: Optional[GeneratedDocument]
```

## Error Handling

### Error Types

1. **Template Not Found Error**
   - Occurs when no matching template exists
   - Response: List available templates
   - Allow user to retry with different query

2. **Template Parse Error**
   - Occurs when DOCX file is corrupted or invalid
   - Response: Log error, notify admin
   - Fallback: Suggest alternative templates

3. **Field Extraction Error**
   - Occurs when entity extraction fails
   - Response: Log warning, continue with manual collection
   - No user-facing error

4. **Validation Error**
   - Occurs when user input doesn't match field type
   - Response: Show specific error message
   - Re-prompt for same field

5. **Document Generation Error**
   - Occurs when filling template fails
   - Response: Log error with details
   - Allow user to retry or download partial document

### Error Handling Strategy

```python
class DocumentProcessingError(Exception):
    """Base exception for document processing"""
    pass

class TemplateNotFoundError(DocumentProcessingError):
    """Template matching failed"""
    pass

class TemplateParseError(DocumentProcessingError):
    """Template analysis failed"""
    pass

class ValidationError(DocumentProcessingError):
    """Field validation failed"""
    pass

class GenerationError(DocumentProcessingError):
    """Document generation failed"""
    pass
```

### Error Recovery

- **Graceful Degradation**: Continue with partial data when possible
- **User Feedback**: Clear, actionable error messages
- **Logging**: Comprehensive error logging for debugging
- **Retry Logic**: Allow users to retry failed operations
- **Fallback Options**: Suggest alternatives when primary path fails

## Testing Strategy

### Unit Tests

1. **Query Analyzer Tests**
   - Test document type detection
   - Test location extraction
   - Test field value extraction
   - Test edge cases (empty input, special characters)

2. **Template Matcher Tests**
   - Test exact filename matching
   - Test fuzzy matching
   - Test location prioritization
   - Test with multiple templates

3. **Document Analyzer Tests**
   - Test placeholder extraction
   - Test field type inference
   - Test with various DOCX structures
   - Test with tables, headers, footers

4. **Field Comparator Tests**
   - Test exact matching
   - Test fuzzy matching
   - Test field normalization
   - Test with missing fields

5. **Data Collector Tests**
   - Test question generation
   - Test validation logic
   - Test skip functionality
   - Test state management

6. **Document Generator Tests**
   - Test placeholder replacement
   - Test formatting preservation
   - Test with skipped fields
   - Test filename generation

### Integration Tests

1. **End-to-End Flow**
   - Test complete document generation flow
   - Test with real DOCX templates
   - Test with various user queries
   - Verify generated documents

2. **Error Scenarios**
   - Test with missing templates
   - Test with corrupted DOCX files
   - Test with invalid user input
   - Verify error handling

3. **Performance Tests**
   - Test with large DOCX files
   - Test with many placeholders
   - Test concurrent requests
   - Measure response times

### Test Data

- Sample DOCX templates with various structures
- Sample user queries (valid and invalid)
- Sample field data (valid and invalid)
- Expected output documents

## Implementation Notes

### Phase 1: Core Components
- Implement Document Analyzer to read DOCX templates
- Implement Template Matcher for file discovery
- Integrate with existing Query Analyzer (IntentDetector + EntityExtractor)

### Phase 2: Field Processing
- Implement Field Comparator for smart matching
- Enhance Data Collector with skip functionality
- Add comprehensive validation

### Phase 3: Document Generation
- Implement Document Generator with placeholder replacement
- Add formatting preservation
- Implement download functionality

### Phase 4: Polish & Testing
- Add comprehensive error handling
- Implement logging and monitoring
- Write unit and integration tests
- Performance optimization

### Dependencies

**New Dependencies**:
- `python-docx` (already installed) - For DOCX manipulation
- `fuzzywuzzy` or `rapidfuzz` - For fuzzy string matching (optional)

**Existing Dependencies**:
- `streamlit` - UI framework
- `pydantic` - Data validation
- `python-dateutil` - Date parsing

### Configuration

```python
# config.py
DOCUMENTS_FOLDER = Path("documents")
PLACEHOLDER_PATTERNS = [
    r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}",  # {{field_name}}
    r"\[([a-zA-Z_][a-zA-Z0-9_]*)\]",      # [field_name]
    r"__([a-zA-Z_][a-zA-Z0-9_]*)__",      # __field_name__
]
FIELD_TYPE_KEYWORDS = {
    "date": ["date", "dob", "birth", "marriage", "wedding"],
    "phone": ["phone", "mobile", "contact", "telephone"],
    "email": ["email", "mail"],
    "address": ["address", "residence", "location"],
}
MAX_FUZZY_DISTANCE = 3
SKIP_KEYWORDS = ["skip", "pass", "next", "leave blank"]
```

## Security Considerations

1. **File Access**: Restrict document folder access to prevent directory traversal
2. **Input Validation**: Sanitize all user inputs before processing
3. **File Size Limits**: Limit DOCX file size to prevent DoS
4. **Path Validation**: Validate all file paths before access
5. **Data Privacy**: Don't log sensitive user data (PII)

## Performance Considerations

1. **Template Caching**: Cache analyzed template structures
2. **Lazy Loading**: Load DOCX files only when needed
3. **Async Processing**: Use async for I/O operations
4. **Connection Pooling**: Reuse resources where possible
5. **Memory Management**: Stream large files instead of loading entirely

## Migration Strategy

### From Current System

1. **Keep Existing JSON Templates**: Support both JSON and DOCX-based workflows
2. **Gradual Migration**: Add DOCX support alongside existing system
3. **Backward Compatibility**: Ensure existing functionality continues to work
4. **Feature Flag**: Use flag to enable/disable DOCX-based processing

### Migration Steps

1. Implement new components without breaking existing code
2. Add configuration to choose between JSON and DOCX modes
3. Test thoroughly with both modes
4. Gradually migrate templates from JSON to DOCX
5. Deprecate JSON templates once DOCX is stable
