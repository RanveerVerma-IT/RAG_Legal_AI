# Usage Guide - Advanced Backend System

## Quick Start

### 1. Run the Application

```bash
streamlit run main.py
```

### 2. Try These Example Queries

#### Example 1: Marriage Registration with Partial Data
```
User: "I need a marriage registration form for Jaipur. Groom name is John Doe, phone 9876543210"

System: 
- Finds: Sample_Jaipur_Marriage_Form.docx
- Extracts: groom_name="John Doe", groom_phone="9876543210"
- Asks for: bride_name, marriage_date, addresses, etc.
```

#### Example 2: Using Skip Functionality
```
User: "Generate marriage certificate for Jaipur"
System: "Please provide Groom Name or type 'skip' to leave blank"

User: "John Smith"
System: "Please provide Groom Father Name or type 'skip' to leave blank"

User: "skip"  ← Skips this field
System: "Please provide Groom Date of Birth..."

User: "15-05-1990"
System: "Please provide Groom Address or type 'skip' to leave blank"

User: "skip"  ← Skips this field too
...continues with remaining fields
```

#### Example 3: Maximum Information Upfront
```
User: "Marriage form for Jaipur. Groom: John Doe, son of Robert Doe, DOB 15-05-1990, 
      phone 9876543210. Bride: Jane Smith, daughter of Michael Smith, DOB 20-08-1992, 
      phone 9876543211. Marriage date 10-11-2024"

System:
- Extracts all provided information
- Only asks for missing fields (addresses, marriage place)
```

## Skip Keywords

You can skip any field by typing:
- `skip`
- `pass`
- `next`
- `leave blank`
- `leave empty`
- `n/a`
- `na`

## Supported Placeholder Formats

When creating templates, use any of these formats:

1. `{{field_name}}` - Primary format (recommended)
2. `[field_name]` - Alternative format
3. `__field_name__` - Alternative format
4. `{field_name}` - Simple format

Example template:
```
Groom Name: {{groom_name}}
Bride Name: {{bride_name}}
Marriage Date: {{marriage_date}}
Address: {{address}}
Phone: {{phone}}
```

## Field Type Auto-Detection

The system automatically detects field types:

| Field Name Contains | Detected Type | Format Expected |
|---------------------|---------------|-----------------|
| date, dob, birth | date | DD-MM-YYYY |
| phone, mobile, contact | phone | +91XXXXXXXXXX |
| email, mail | email | email@example.com |
| address, residence | address | Full address |
| name, title | text | Any text |

## Creating New Templates

### Step 1: Create DOCX File

Open Microsoft Word or LibreOffice and create your form:

```
MARRIAGE REGISTRATION FORM

Groom Details:
Name: {{groom_name}}
Father's Name: {{groom_father_name}}
Date of Birth: {{groom_date_of_birth}}
Address: {{groom_address}}
Phone: {{groom_phone}}

Bride Details:
Name: {{bride_name}}
Father's Name: {{bride_father_name}}
Date of Birth: {{bride_date_of_birth}}
Address: {{bride_address}}
Phone: {{bride_phone}}

Marriage Details:
Date of Marriage: {{marriage_date}}
Place of Marriage: {{marriage_place}}
```

### Step 2: Save with Descriptive Name

Save as: `Location_DocumentType_Form.docx`

Examples:
- `Jaipur_Marriage_Registration_Form.docx`
- `Delhi_Birth_Certificate_Form.docx`
- `Mumbai_Income_Certificate_Form.docx`

### Step 3: Place in Documents Folder

Copy the file to: `documents/`

That's it! The system will automatically:
- Detect the document type
- Extract all placeholders
- Infer field types
- Generate appropriate questions

## Testing Your Template

1. Start the application
2. Type: "Generate [document type] for [location]"
3. Example: "Generate marriage form for Jaipur"
4. The system will:
   - Find your template
   - Show you what fields it found
   - Ask for each field with appropriate format hints

## Troubleshooting

### Template Not Found

**Problem:** "No template found for 'marriage'"

**Solution:**
- Check filename includes document type keyword (marriage, birth, etc.)
- Check file is in `documents/` folder
- Check file extension is `.docx` (not `.doc`)

### Placeholders Not Detected

**Problem:** Fields not being asked for

**Solution:**
- Check placeholder format: `{{field_name}}`
- No spaces inside braces: `{{name}}` not `{{ name }}`
- Use underscores for multi-word fields: `{{groom_name}}`

### Field Type Wrong

**Problem:** Date field treated as text

**Solution:**
- Include type keyword in field name: `{{date_of_birth}}` not `{{dob_value}}`
- Or update `FIELD_TYPE_KEYWORDS` in `config.py`

### Skip Not Working

**Problem:** "skip" is being treated as a value

**Solution:**
- Type exactly: `skip` (lowercase)
- Or use alternatives: `pass`, `next`, `leave blank`

## Advanced Configuration

Edit `config.py` to customize:

```python
# Add new document type
DOCUMENT_TYPE_KEYWORDS = {
    "marriage": ["marriage", "wedding", "nikah"],
    "birth": ["birth", "janam"],
    "custom": ["custom", "special"],  # Add your type
}

# Add new location
LOCATION_KEYWORDS = {
    "jaipur": ["jaipur"],
    "mycity": ["mycity", "my_city"],  # Add your location
}

# Add new field type
FIELD_TYPE_KEYWORDS = {
    "date": ["date", "dob", "birth"],
    "custom_type": ["custom", "special"],  # Add your type
}

# Customize questions
QUESTION_TEMPLATES = {
    "date": "Please provide {label} (DD-MM-YYYY) or 'skip'",
    "custom_type": "Please provide {label} or 'skip'",
}
```

## Tips for Best Results

1. **Be Specific in Queries**: Include location and document type
   - Good: "Marriage form for Jaipur"
   - Better: "Jaipur marriage registration form"

2. **Provide Data Upfront**: Include known information in first message
   - "Marriage form for Jaipur. Groom: John Doe, phone 9876543210"

3. **Use Consistent Field Names**: In templates, use standard names
   - `{{groom_name}}` not `{{name_of_groom}}`
   - `{{date_of_birth}}` not `{{birth_date}}`

4. **Skip Wisely**: Skip optional fields, provide required ones
   - Required: names, dates
   - Optional: middle names, alternate phones

5. **Check Generated Document**: Always review before using officially
   - Verify all fields filled correctly
   - Check skipped fields are acceptable

## Example Session

```
User: "I need a marriage certificate for Jaipur"

System: "I will help you generate a Sample_Jaipur_Marriage_Form.

I need 10 field(s).

Please provide Groom Name or type 'skip' to leave blank"

User: "John Doe"

System: "Please provide Groom Father Name or type 'skip' to leave blank"

User: "Robert Doe"

System: "Please provide Groom Date of Birth (format: DD-MM-YYYY) or type 'skip' to leave blank"

User: "15-05-1990"

System: "Please provide Groom Address (full address) or type 'skip' to leave blank"

User: "123 Main St, Jaipur, Rajasthan"

System: "Please provide Groom Phone (format: +91XXXXXXXXXX) or type 'skip' to leave blank"

User: "9876543210"

System: "Please provide Bride Name or type 'skip' to leave blank"

User: "Jane Smith"

System: "Please provide Bride Father Name or type 'skip' to leave blank"

User: "skip"

System: "Please provide Bride Date of Birth (format: DD-MM-YYYY) or type 'skip' to leave blank"

User: "20-08-1992"

System: "Please provide Bride Address (full address) or type 'skip' to leave blank"

User: "skip"

System: "Please provide Bride Phone (format: +91XXXXXXXXXX) or type 'skip' to leave blank"

User: "9876543211"

System: "Please provide Date of Marriage (format: DD-MM-YYYY) or type 'skip' to leave blank"

User: "10-11-2024"

System: "All required information collected. Generating your document now."

System: "Your document is ready! (8 fields filled, 2 skipped). Download using the button below."

[Download DOCX button appears]
```

## Support

For issues or questions:
1. Check logs in console
2. Review `BACKEND_ARCHITECTURE.md` for technical details
3. Check `config.py` for configuration options
4. Verify template format matches examples
