# Improved Data Collection System

## Overview

The data collection system has been significantly enhanced to provide clear, user-friendly questions with examples, format instructions, and helpful error messages.

## Key Improvements

### 1. **Enhanced Question Format**

**Before:**
```
Please provide groom_name or type 'skip' to leave blank
```

**After:**
```
✏️ Please provide **Groom's Name**

Type 'skip' to leave blank

💡 **Note**: Full name of the groom (as per official documents)
```

### 2. **Field-Specific Instructions**

Each field type now includes:
- **Icon** for visual identification
- **Clear label** with proper formatting
- **Format requirements** with examples
- **Helpful notes** explaining what's needed

#### Date Fields
```
📅 Please provide **Date of Birth**

Format: DD-MM-YYYY (e.g., 15-08-1990)
Type 'skip' to leave blank

💡 **Note**: Date of birth of the person
```

#### Phone Fields
```
📱 Please provide **Groom's Phone Number**

Format: 10-digit mobile number (e.g., 9876543210)
Type 'skip' to leave blank

💡 **Note**: Contact number of the groom
```

#### Email Fields
```
📧 Please provide **Email Address**

Format: email@example.com
Type 'skip' to leave blank
```

#### Address Fields
```
🏠 Please provide **Groom's Address**

Include: House/Flat No., Street, Area, City, State, PIN Code
Example: 123 Main Street, Malviya Nagar, Jaipur, Rajasthan - 302017
Type 'skip' to leave blank

💡 **Note**: Complete residential address of the groom
```

### 3. **Improved Error Messages**

**Before:**
```
Invalid phone number format
```

**After:**
```
❌ Invalid phone number format

✅ Correct format: 10 digits starting with 6-9
Examples: 9876543210 or +919876543210
```

#### All Error Types:

**Name Validation:**
```
❌ Name contains invalid characters

Only letters, spaces, hyphens, and apostrophes are allowed
Example: Rajesh Kumar, Mary O'Brien, Jean-Pierre
```

**Date Validation:**
```
❌ Invalid date format

✅ Correct format: DD-MM-YYYY
Examples: 15-08-1990, 01-01-2000
```

**Email Validation:**
```
❌ Invalid email format

✅ Correct format: username@domain.com
Examples: john.doe@email.com, user123@gmail.com
```

**Address Validation:**
```
❌ Address is too short

Please provide a complete address with house number, street, area, city, and PIN code
```

### 4. **Field-Specific Descriptions**

Added descriptions for common fields:

| Field | Description |
|-------|-------------|
| groom_name | Full name of the groom (as per official documents) |
| bride_name | Full name of the bride (as per official documents) |
| father_name | Full name of the father (as per official documents) |
| mother_name | Full name of the mother (as per official documents) |
| child_name | Full name of the child (as per birth records) |
| marriage_date | Date when the marriage took place |
| marriage_place | Location where the marriage ceremony was held |
| date_of_birth | Date of birth of the person |
| place_of_birth | City/Town where the person was born |
| address | Complete residential address |
| phone | Contact phone number |
| email | Email address |
| occupation | Occupation/Profession |
| witness_1_name | Full name of first witness |
| witness_2_name | Full name of second witness |

### 5. **Better Field Label Formatting**

**Before:**
```
groom_father_name → Groom Father Name
```

**After:**
```
groom_father_name → Groom's Father Name
```

**Improvements:**
- Proper possessive forms (Groom's, Bride's, Father's)
- Correct abbreviations (DOB → Date of Birth)
- Better readability (PIN Code, not Pincode)

### 6. **Example Values**

System provides contextual examples:

```python
Examples by field type:
- Names: "Rajesh Kumar Sharma", "Priya Singh"
- Dates: "15-08-1990", "10-11-2024"
- Phone: "9876543210"
- Email: "rajesh.kumar@email.com"
- Address: "123 Main Street, Malviya Nagar, Jaipur, Rajasthan - 302017"
- Place: "Jaipur", "Delhi"
- Occupation: "Software Engineer"
- Age: "28"
```

## User Experience Flow

### Example: Marriage Certificate

**Step 1: Initial Request**
```
User: "Generate marriage certificate for Jaipur"
```

**Step 2: First Field**
```
System:
✏️ Please provide **Groom's Name**

Type 'skip' to leave blank

💡 **Note**: Full name of the groom (as per official documents)
```

**Step 3: User Input**
```
User: "Rajesh Kumar"
```

**Step 4: Next Field**
```
System:
✏️ Please provide **Groom's Father Name**

Type 'skip' to leave blank

💡 **Note**: Full name of groom's father
```

**Step 5: Date Field**
```
System:
📅 Please provide **Groom's Date of Birth**

Format: DD-MM-YYYY (e.g., 15-08-1990)
Type 'skip' to leave blank

💡 **Note**: Date of birth of the person
```

**Step 6: Invalid Input**
```
User: "15/08/90"

System:
❌ Invalid date format

✅ Correct format: DD-MM-YYYY
Examples: 15-08-1990, 01-01-2000

Please try again.
```

**Step 7: Correct Input**
```
User: "15-08-1990"

System: ✅ Recorded

📱 Please provide **Groom's Phone Number**

Format: 10-digit mobile number (e.g., 9876543210)
Type 'skip' to leave blank
```

**Step 8: Skip Field**
```
User: "skip"

System: ⏭️ Skipped

🏠 Please provide **Groom's Address**

Include: House/Flat No., Street, Area, City, State, PIN Code
Example: 123 Main Street, Malviya Nagar, Jaipur, Rajasthan - 302017
Type 'skip' to leave blank
```

## Technical Implementation

### Data Collector Enhancements

```python
# Enhanced question templates
QUESTION_TEMPLATES = {
    "date": "📅 Please provide **{label}**\n\n"
            "Format: DD-MM-YYYY (e.g., 15-08-1990)\n"
            "Type 'skip' to leave blank",
    
    "phone": "📱 Please provide **{label}**\n\n"
             "Format: 10-digit mobile number (e.g., 9876543210)\n"
             "Type 'skip' to leave blank",
    # ... more templates
}

# Field-specific descriptions
FIELD_DESCRIPTIONS = {
    "groom_name": "Full name of the groom (as per official documents)",
    "bride_name": "Full name of the bride (as per official documents)",
    # ... more descriptions
}
```

### Validator Enhancements

```python
# Enhanced error messages with emojis and examples
def validate_phone(value: str):
    if invalid:
        return False, (
            "❌ Invalid phone number format\n\n"
            "✅ Correct format: 10 digits starting with 6-9\n"
            "Examples: 9876543210 or +919876543210"
        )
```

## Benefits

### For Users
1. **Clear Instructions**: Know exactly what format is expected
2. **Helpful Examples**: See real examples for each field
3. **Better Errors**: Understand what went wrong and how to fix it
4. **Visual Cues**: Icons help identify field types quickly
5. **Context**: Understand why each field is needed

### For System
1. **Better Data Quality**: Users provide correct format first time
2. **Fewer Errors**: Clear instructions reduce validation failures
3. **Faster Completion**: Users don't need to retry multiple times
4. **Better UX**: Professional, polished interface
5. **Reduced Support**: Self-explanatory questions

## Customization

### Adding New Field Descriptions

Edit `utils/data_collector.py`:

```python
FIELD_DESCRIPTIONS = {
    "your_field_name": "Description of what this field is for",
    # Add more...
}
```

### Adding New Examples

```python
def get_field_examples(self, field_name: str, field_type: str):
    examples = {
        "your_field": "Example: Your example value",
        # Add more...
    }
```

### Customizing Question Templates

```python
QUESTION_TEMPLATES = {
    "your_type": "🎯 Please provide **{label}**\n\n"
                 "Your custom instructions here\n"
                 "Type 'skip' to leave blank",
}
```

### Customizing Error Messages

Edit `utils/validators.py`:

```python
def validate_your_field(value: str):
    if invalid:
        return False, (
            "❌ Your error message\n\n"
            "✅ Correct format: Your format\n"
            "Examples: Your examples"
        )
```

## Testing

Test with various inputs:

```python
# Valid inputs
"Rajesh Kumar"  # Name
"15-08-1990"    # Date
"9876543210"    # Phone
"user@email.com"  # Email
"123 Main St, Jaipur, Rajasthan - 302017"  # Address

# Invalid inputs (should show helpful errors)
"R"  # Name too short
"15/08/90"  # Wrong date format
"12345"  # Invalid phone
"user@"  # Invalid email
"123"  # Address too short
```

## Future Enhancements

Potential improvements:
1. **Auto-complete**: Suggest values based on previous inputs
2. **Smart Defaults**: Pre-fill common values
3. **Field Dependencies**: Show/hide fields based on other inputs
4. **Progress Indicator**: Show how many fields remaining
5. **Bulk Input**: Allow pasting multiple fields at once
6. **Voice Input**: Support voice-to-text for fields
7. **Multi-language**: Support questions in multiple languages

## Summary

The improved data collection system provides:
- ✅ Clear, formatted questions with icons
- ✅ Detailed format instructions and examples
- ✅ Field-specific descriptions and context
- ✅ Helpful, actionable error messages
- ✅ Better field label formatting
- ✅ Professional user experience
- ✅ Reduced errors and faster completion
- ✅ Easy customization and extension

Users now have all the information they need to provide accurate data on the first try!
