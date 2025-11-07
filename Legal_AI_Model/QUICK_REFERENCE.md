# Quick Reference Guide - Backend Components

## Component Overview

### 1. Entity Extractor
**File**: `utils/entity_extractor.py`
**Purpose**: Extract entities from user input
**Usage**:
```python
from utils.entity_extractor import entity_extractor

entities = entity_extractor.extract_entities("My name is John Doe, email: john@example.com")
# Returns: {'applicant_name': 'John Doe', 'email': 'john@example.com', ...}
```

### 2. Field Validators
**File**: `utils/validators.py`
**Purpose**: Validate and format field values
**Usage**:
```python
from utils.validators import FieldValidatorFactory

is_valid, error, formatted = FieldValidatorFactory.validate_and_format('email', 'test@example.com')
# Returns: (True, None, 'test@example.com')
```

**Supported Field Types**:
- `name` - Person names
- `email` - Email addresses
- `phone` - Phone numbers (Indian format)
- `date` - Dates
- `address` - Addresses
- `age` - Age values

### 3. Template Manager
**File**: `utils/template_manager.py`
**Purpose**: Load and manage document templates
**Usage**:
```python
from utils.template_manager import template_manager

# Load template
template = template_manager.load_template('rajasthan', 'birth_certificate')

# Get required fields
fields = template_manager.get_required_fields('rajasthan', 'birth_certificate')

# Get field question
question = template_manager.get_field_question('rajasthan', 'birth_certificate', 'applicant_name')
```

### 4. Intent Detector
**File**: `utils/intent_detector.py`
**Purpose**: Detect document type and state from user input
**Usage**:
```python
from utils.intent_detector import intent_detector

doc_type, state = intent_detector.detect_intent("I need a birth certificate for Jaipur")
# Returns: ('birth_certificate', 'rajasthan')
```

### 5. Document Factory
**File**: `generators/document_factory.py`
**Purpose**: Generate documents dynamically
**Usage**:
```python
from generators.document_factory import DocumentGeneratorFactory

# Create generator
generator = DocumentGeneratorFactory.create_generator('birth_certificate', 'rajasthan')

# Generate documents
docx, pdf, filename = generator.generate(data)

# Get document name
name = DocumentGeneratorFactory.get_document_name('birth_certificate')
```

## Common Workflows

### Adding a New Validator
1. Add validation method to `FieldValidator` class
2. Add formatter method (optional)
3. Register in `VALIDATORS` and `FORMATTERS` dictionaries

### Adding a New Document Type
1. Add keywords to `IntentDetector.DOCUMENT_KEYWORDS`
2. Create generator class inheriting from `DocumentGenerator`
3. Register in `DocumentGeneratorFactory.GENERATORS`
4. Create template JSON file

### Adding a New State
1. Add keywords to `IntentDetector.STATE_KEYWORDS`
2. Create state directory in `templates/`
3. Add document templates for that state

## Error Handling

All components use consistent error handling:
```python
try:
    result = component.method()
except ValueError as e:
    # Validation or input errors
    logger.error(f"Validation error: {e}")
except FileNotFoundError as e:
    # Missing templates or files
    logger.error(f"File not found: {e}")
except Exception as e:
    # Unexpected errors
    logger.error(f"Unexpected error: {e}")
```

## Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Log levels used:
- `DEBUG`: Detailed tracing
- `INFO`: Normal operations
- `WARNING`: Validation issues
- `ERROR`: Failures

## Configuration

### Template Directory
Default: `templates/`
Change in `template_manager.py`:
```python
template_manager = TemplateManager(templates_dir="custom_path")
```

### Default State
Default: `rajasthan`
Change in `intent_detector.py`:
```python
intent_detector = IntentDetector(default_state="delhi")
```

## Performance Tips

1. **Template Caching**: Automatically enabled, clear with:
   ```python
   template_manager.clear_cache()
   ```

2. **Validation**: Validate early to prevent unnecessary processing

3. **Logging**: Use appropriate log levels (avoid DEBUG in production)

## Troubleshooting

### Entity Not Extracted
- Check if pattern exists in `entity_extractor.py`
- Add new pattern if needed
- Test with various input formats

### Validation Failing
- Check validator logic in `validators.py`
- Verify input format
- Check error message for details

### Template Not Found
- Verify template file exists
- Check file path and naming
- Ensure JSON is valid

### Document Generation Fails
- Check all required fields are present
- Verify data format
- Check generator implementation
- Review logs for details

## Best Practices

1. **Always validate input** before processing
2. **Use logging** for debugging
3. **Handle errors gracefully** with user-friendly messages
4. **Format data consistently** using validators
5. **Cache templates** for better performance
6. **Test edge cases** thoroughly
7. **Keep patterns updated** in extractors and detectors
