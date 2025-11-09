# Self-Learning System

## Overview

The system now includes an intelligent self-learning component that automatically improves from user interactions, making the experience better over time.

## What It Learns

### 1. **Query Patterns**
- Tracks how users phrase their requests
- Identifies common document types
- Learns popular query formats

### 2. **Field Values**
- Remembers common field inputs
- Provides suggestions based on history
- Learns naming patterns

### 3. **Error Patterns**
- Tracks which fields cause most errors
- Identifies problematic validations
- Provides extra help for difficult fields

### 4. **Skip Behavior**
- Monitors which fields users skip most
- Can suggest making frequently skipped fields optional
- Optimizes field collection order

### 5. **Success Rates**
- Tracks completion rates
- Monitors user satisfaction
- Identifies improvement areas

## How It Works

### Learning from Queries
```python
User: "I want to generate marriage certificate"
System: Learns that "marriage certificate" is a popular request
```

### Learning from Field Inputs
```python
User enters: "Rajesh Kumar"
System: Remembers "Rajesh Kumar" as common name
Next time: Suggests "Rajesh Kumar" for similar fields
```

### Learning from Errors
```python
User enters: "15/08/90" for date
System: Validation fails
Learning: Date field has high error rate
Next time: Adds extra tip about DD-MM-YYYY format
```

### Learning from Skips
```python
User skips: "Middle Name" field 80% of the time
System: Learns this field is often skipped
Suggestion: Make "Middle Name" optional
```

## Features

### 1. **Smart Suggestions**
System provides suggestions based on past inputs:

```
📱 **Groom's Phone Number**

Please enter 10-digit mobile number (e.g., 9876543210)
Type 'skip' to leave blank

💡 **Common values**: 9876543210, 9123456789
```

### 2. **Extra Help for Problematic Fields**
For fields with high error rates:

```
📅 **Date of Birth**

Please enter in DD-MM-YYYY format (e.g., 15-08-1990)
Type 'skip' to leave blank

⚠️ **Tip**: This field often has errors. Please double-check your input.
```

### 3. **Adaptive Field Requirements**
System can suggest making fields optional:

```python
# After 100 sessions, if "Middle Name" is skipped 70% of the time
system.should_make_field_optional("middle_name")  # Returns True
```

### 4. **Performance Insights**
Track system performance:

```python
insights = learning_system.get_insights()
# Returns:
{
    "total_sessions": 150,
    "successful_completions": 142,
    "success_rate": 0.947,
    "popular_documents": [("marriage", 85), ("birth", 45)],
    "problematic_fields": [("date_of_birth", 23), ("phone", 15)],
    "frequently_skipped": [("middle_name", 105), ("email", 67)]
}
```

## Data Storage

### Learning Data File
Location: `learning_data.json`

Structure:
```json
{
  "query_patterns": {
    "generate marriage certificate": 45,
    "i want birth certificate": 23
  },
  "field_values": {
    "groom_name": {
      "Rajesh Kumar": 12,
      "Amit Sharma": 8
    }
  },
  "common_errors": {
    "date_of_birth:format": 23,
    "phone:invalid": 15
  },
  "document_preferences": {
    "marriage": 85,
    "birth": 45
  },
  "field_skip_rates": {
    "middle_name": 105,
    "email": 67
  },
  "successful_completions": 142,
  "total_sessions": 150,
  "last_updated": "2024-11-09T20:30:00"
}
```

## Privacy & Security

### What's Stored
- ✅ Field names (e.g., "groom_name")
- ✅ Common values (e.g., "Rajesh Kumar")
- ✅ Error types (e.g., "format_error")
- ✅ Skip counts
- ✅ Success rates

### What's NOT Stored
- ❌ Personal identifiable information
- ❌ Complete documents
- ❌ User identities
- ❌ Session details
- ❌ Sensitive data

### Data Protection
- All data stored locally
- No cloud synchronization
- User can delete learning data anytime
- Aggregated statistics only

## Benefits

### For Users
1. **Faster Input**: Suggestions based on common values
2. **Fewer Errors**: Extra help for problematic fields
3. **Better Experience**: System improves over time
4. **Smart Defaults**: Common values suggested

### For System
1. **Continuous Improvement**: Gets better with use
2. **Error Reduction**: Identifies and fixes problem areas
3. **Optimization**: Learns optimal field order
4. **Insights**: Understands user behavior

## Usage Examples

### Example 1: First-Time User
```
Session 1:
User: "Generate marriage certificate"
System: Standard questions, no suggestions

Session 50:
User: "Generate marriage certificate"
System: 
- Suggests common names
- Provides extra help for date fields
- Optimized question order
```

### Example 2: Error Learning
```
Sessions 1-10:
- 8 users enter wrong date format
- System tracks this error

Session 11+:
System adds: "⚠️ Tip: This field often has errors. Please use DD-MM-YYYY format"
Result: Error rate drops to 2/10
```

### Example 3: Skip Learning
```
Sessions 1-100:
- 85 users skip "Middle Name"
- System learns this field is often skipped

System Insight:
"Middle Name" has 85% skip rate
Recommendation: Make field optional
```

## API

### Learn from Query
```python
learning_system.learn_from_query(
    query="generate marriage certificate",
    document_type="marriage"
)
```

### Learn from Field Input
```python
learning_system.learn_from_field_input(
    field_name="groom_name",
    field_value="Rajesh Kumar",
    field_type="text"
)
```

### Learn from Error
```python
learning_system.learn_from_error(
    field_name="date_of_birth",
    error_type="format_error"
)
```

### Learn from Skip
```python
learning_system.learn_from_skip(
    field_name="middle_name"
)
```

### Learn from Completion
```python
learning_system.learn_from_completion(
    success=True
)
```

### Get Suggestions
```python
suggestions = learning_system.get_field_suggestions(
    field_name="groom_name",
    limit=3
)
# Returns: ["Rajesh Kumar", "Amit Sharma", "Vijay Singh"]
```

### Get Insights
```python
insights = learning_system.get_insights()
```

## Configuration

### Disable Learning
Set in code:
```python
# In main.py, comment out learning calls
# learning_system.learn_from_query(...)
```

### Clear Learning Data
Delete file:
```bash
rm learning_data.json
```

### Adjust Thresholds
Edit `core/learning_system.py`:
```python
def should_make_field_optional(self, field_name: str, threshold: float = 0.7):
    # Change threshold from 0.7 to your preferred value
```

## Monitoring

### View Learning Data
```bash
cat learning_data.json | python -m json.tool
```

### Check Success Rate
```python
rate = learning_system.get_success_rate()
print(f"Success rate: {rate:.1%}")
```

### View Popular Documents
```python
popular = learning_system.get_popular_documents()
for doc_type, count in popular:
    print(f"{doc_type}: {count} requests")
```

### View Problematic Fields
```python
problems = learning_system.get_problematic_fields()
for field_error, count in problems:
    print(f"{field_error}: {count} errors")
```

## Future Enhancements

Potential improvements:
1. **ML-based Predictions**: Use machine learning for better suggestions
2. **Personalization**: Learn individual user preferences
3. **A/B Testing**: Test different question formats
4. **Sentiment Analysis**: Detect user frustration
5. **Auto-optimization**: Automatically adjust based on metrics
6. **Cloud Sync**: Optional cloud backup (with privacy)
7. **Analytics Dashboard**: Visual insights into learning data

## Summary

The self-learning system:
- ✅ Learns from every user interaction
- ✅ Provides smart suggestions
- ✅ Identifies and fixes problem areas
- ✅ Improves success rates over time
- ✅ Respects user privacy
- ✅ Works automatically in background
- ✅ No configuration needed
- ✅ Continuous improvement

The more the system is used, the better it becomes!
