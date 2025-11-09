# Intelligent Question System - Examples

## Overview

The system now asks highly intelligent, context-rich questions that help users understand exactly what data to enter and why.

## Question Structure

Each question includes:
1. **📋 What to enter** - Clear description of the field
2. **❓ Why needed** - Explanation of why this information is required
3. **✏️ Example** - Real-world example to follow
4. **💡 Tip** - Helpful advice for entering the data correctly

## Real Examples

### Example 1: Groom's Name

**Before (Basic):**
```
✏️ **Groom's Name**

Type 'skip' to leave blank
```

**After (Intelligent):**
```
✏️ **Groom's Name**

Please enter in DD-MM-YYYY format (e.g., 15-08-1990)
Type 'skip' to leave blank

📋 **What to enter**: Full legal name of the groom

❓ **Why needed**: This will appear on the official marriage certificate

✏️ **Example**: Rajesh Kumar Sharma

💡 **Tip**: Use the exact name as it appears on your Aadhaar card or passport
```

### Example 2: Marriage Date

**Before (Basic):**
```
📅 **Marriage Date**

Please enter in DD-MM-YYYY format (e.g., 15-08-1990)
Type 'skip' to leave blank
```

**After (Intelligent):**
```
📅 **Marriage Date**

Please enter in DD-MM-YYYY format (e.g., 15-08-1990)
Type 'skip' to leave blank

📋 **What to enter**: The date when your marriage ceremony took place

❓ **Why needed**: This is the official date of your marriage

✏️ **Example**: 10-11-2024 (for November 10, 2024)

💡 **Tip**: Use the date of your wedding ceremony, not the registration date
```

### Example 3: Groom's Address

**Before (Basic):**
```
🏠 **Groom's Address**

Please enter complete address with PIN code
Type 'skip' to leave blank
```

**After (Intelligent):**
```
🏠 **Groom's Address**

Please enter complete address with PIN code
Type 'skip' to leave blank

📋 **What to enter**: Complete residential address of the groom

❓ **Why needed**: Required for official correspondence and records

✏️ **Example**: 123 Main Street, Malviya Nagar, Jaipur, Rajasthan - 302017

💡 **Tip**: Include house number, street, area, city, state, and PIN code
```

### Example 4: Groom's Phone

**Before (Basic):**
```
📱 **Groom's Phone Number**

Please enter 10-digit mobile number (e.g., 9876543210)
Type 'skip' to leave blank
```

**After (Intelligent):**
```
📱 **Groom's Phone Number**

Please enter 10-digit mobile number (e.g., 9876543210)
Type 'skip' to leave blank

📋 **What to enter**: Mobile number of the groom

❓ **Why needed**: For contact regarding the certificate

✏️ **Example**: 9876543210

💡 **Tip**: Enter 10-digit mobile number without +91 or spaces
```

### Example 5: Child's Name (Birth Certificate)

**Before (Basic):**
```
✏️ **Child's Name**

Type 'skip' to leave blank
```

**After (Intelligent):**
```
✏️ **Child's Name**

Type 'skip' to leave blank

📋 **What to enter**: Full name of the child

❓ **Why needed**: This will be the official name on the birth certificate

✏️ **Example**: Aarav Kumar Sharma

💡 **Tip**: Choose carefully as this becomes the legal name
```

### Example 6: Groom's Age

**Before (Basic):**
```
✏️ **Groom's Age**

Type 'skip' to leave blank
```

**After (Intelligent):**
```
✏️ **Groom's Age**

Type 'skip' to leave blank

📋 **What to enter**: Age of the groom at the time of marriage

❓ **Why needed**: Required to verify legal age for marriage

✏️ **Example**: 28

💡 **Tip**: Must be 21 years or above for males
```

### Example 7: Witness Name

**Before (Basic):**
```
✏️ **First Witness Name**

Type 'skip' to leave blank
```

**After (Intelligent):**
```
✏️ **First Witness Name**

Type 'skip' to leave blank

📋 **What to enter**: Full name of the first witness to the marriage

❓ **Why needed**: Legal requirement for marriage registration

✏️ **Example**: Amit Kumar Verma

💡 **Tip**: Must be an adult who was present at the ceremony
```

### Example 8: Gram Panchayat

**Before (Basic):**
```
✏️ **Gram Panchayat**

Type 'skip' to leave blank
```

**After (Intelligent):**
```
✏️ **Gram Panchayat**

Type 'skip' to leave blank

📋 **What to enter**: Name of the Gram Panchayat (village council)

❓ **Why needed**: Required to identify the local administrative body

✏️ **Example**: Sanganer Gram Panchayat

💡 **Tip**: Enter the name of your local Gram Panchayat office
```

## Complete User Flow Example

### Marriage Certificate Generation

**User**: "I want to generate marriage certificate"

**System**: "Great! I'll help you create your **Marriage Registration Certificate**."

---

**System**:
```
✏️ **Groom's Name**

Please enter in DD-MM-YYYY format (e.g., 15-08-1990)
Type 'skip' to leave blank

📋 **What to enter**: Full legal name of the groom

❓ **Why needed**: This will appear on the official marriage certificate

✏️ **Example**: Rajesh Kumar Sharma

💡 **Tip**: Use the exact name as it appears on your Aadhaar card or passport
```

**User**: "Rajesh Kumar Sharma"

---

**System**:
```
✏️ **Groom's Father Name**

Type 'skip' to leave blank

📋 **What to enter**: Full name of the groom's father

❓ **Why needed**: Required for official marriage registration records

✏️ **Example**: Ramesh Kumar Sharma

💡 **Tip**: Include first name, middle name (if any), and surname
```

**User**: "Ramesh Kumar Sharma"

---

**System**:
```
📅 **Marriage Date**

Please enter in DD-MM-YYYY format (e.g., 15-08-1990)
Type 'skip' to leave blank

📋 **What to enter**: The date when your marriage ceremony took place

❓ **Why needed**: This is the official date of your marriage

✏️ **Example**: 10-11-2024 (for November 10, 2024)

💡 **Tip**: Use the date of your wedding ceremony, not the registration date
```

**User**: "10-11-2024"

---

## Benefits

### For Users

1. **Clear Understanding**: Know exactly what to enter
2. **Context Awareness**: Understand why each field is needed
3. **Real Examples**: See actual examples to follow
4. **Helpful Tips**: Get advice for correct entry
5. **Confidence**: Feel confident about data accuracy
6. **Reduced Errors**: Less likely to enter wrong information

### For System

1. **Better Data Quality**: Users provide correct information
2. **Fewer Validation Errors**: Clear instructions reduce mistakes
3. **Higher Completion Rates**: Users don't abandon forms
4. **Professional Image**: Shows attention to detail
5. **User Trust**: Builds confidence in the system

## Field Coverage

The system provides intelligent questions for:

### Marriage Certificate
- ✅ Groom's name, father's name, mother's name
- ✅ Bride's name, father's name, mother's name
- ✅ Marriage date and place
- ✅ Ages and occupations
- ✅ Addresses and contact details
- ✅ Witness information

### Birth Certificate
- ✅ Child's name
- ✅ Father's and mother's names
- ✅ Date and place of birth
- ✅ Contact information

### General Fields
- ✅ Names (all types)
- ✅ Dates (birth, marriage, etc.)
- ✅ Addresses (residential)
- ✅ Contact (phone, email)
- ✅ Administrative (Gram Panchayat, etc.)

## Customization

### Adding New Field Descriptions

Edit `utils/data_collector.py`:

```python
FIELD_DESCRIPTIONS = {
    "your_field_name": {
        "what": "What the user should enter",
        "why": "Why this information is needed",
        "example": "A real example",
        "tip": "Helpful advice"
    },
}
```

### Simple Description (Backward Compatible)

```python
FIELD_DESCRIPTIONS = {
    "simple_field": "Simple description text"
}
```

## Technical Details

### Question Generation Logic

```python
def generate_question(field_name, field_type, field_label):
    # 1. Get basic template
    template = QUESTION_TEMPLATES[field_type]
    
    # 2. Format with label
    question = template.format(label=label)
    
    # 3. Add detailed description if available
    if field_name in FIELD_DESCRIPTIONS:
        desc = FIELD_DESCRIPTIONS[field_name]
        
        if isinstance(desc, dict):
            # Add: What, Why, Example, Tip
            question += detailed_info
        else:
            # Add simple note
            question += simple_note
    
    return question
```

### Data Structure

```python
{
    "field_name": {
        "what": str,      # What to enter
        "why": str,       # Why it's needed
        "example": str,   # Example value
        "tip": str        # Helpful tip
    }
}
```

## Future Enhancements

Potential improvements:
1. **Dynamic Examples**: Show examples based on user's location
2. **Video Tutorials**: Link to video guides for complex fields
3. **Auto-fill Suggestions**: Suggest values based on previous inputs
4. **Field Dependencies**: Show/hide tips based on other fields
5. **Multi-language**: Provide descriptions in multiple languages
6. **Voice Guidance**: Audio instructions for each field
7. **Visual Aids**: Show images of where to find information

## Summary

The intelligent question system:
- ✅ Provides comprehensive context for each field
- ✅ Explains what to enter and why
- ✅ Shows real-world examples
- ✅ Offers helpful tips
- ✅ Reduces user confusion
- ✅ Improves data quality
- ✅ Increases completion rates
- ✅ Builds user confidence

Users now have all the information they need to provide accurate data with confidence!
