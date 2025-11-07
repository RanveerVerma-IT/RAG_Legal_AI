"""
Field Validators
Provides validation and formatting for different field types
"""
import re
from typing import Optional, Tuple
from datetime import datetime
from dateutil import parser as date_parser


class FieldValidator:
    """Validates and formats field values"""
    
    @staticmethod
    def validate_name(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate name field
        
        Returns:
            (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, "Name cannot be empty"
        
        value = value.strip()
        
        if len(value) < 2:
            return False, "Name must be at least 2 characters"
        
        if len(value) > 100:
            return False, "Name is too long (max 100 characters)"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[A-Za-z\s\-'\.]+$", value):
            return False, "Name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_email(value: str) -> Tuple[bool, Optional[str]]:
        """Validate email address"""
        if not value or not value.strip():
            return False, "Email cannot be empty"
        
        value = value.strip()
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_phone(value: str) -> Tuple[bool, Optional[str]]:
        """Validate phone number"""
        if not value or not value.strip():
            return False, "Phone number cannot be empty"
        
        value = value.strip()
        
        # Remove common separators
        cleaned = re.sub(r'[-\s\(\)]', '', value)
        
        # Check for valid Indian phone number
        if re.match(r'^\+91[6-9]\d{9}$', cleaned):
            return True, None
        elif re.match(r'^[6-9]\d{9}$', cleaned):
            return True, None
        else:
            return False, "Invalid phone number format (must be 10 digits starting with 6-9)"
    
    @staticmethod
    def validate_date(value: str) -> Tuple[bool, Optional[str]]:
        """Validate date field"""
        if not value or not value.strip():
            return False, "Date cannot be empty"
        
        value = value.strip()
        
        try:
            parsed_date = date_parser.parse(value, dayfirst=True, fuzzy=True)
            
            # Check if date is not in future (for birth dates)
            if parsed_date > datetime.now():
                return False, "Date cannot be in the future"
            
            # Check if date is reasonable (not too old)
            if parsed_date.year < 1900:
                return False, "Date is too old"
            
            return True, None
        except Exception:
            return False, "Invalid date format"
    
    @staticmethod
    def validate_address(value: str) -> Tuple[bool, Optional[str]]:
        """Validate address field"""
        if not value or not value.strip():
            return False, "Address cannot be empty"
        
        value = value.strip()
        
        if len(value) < 10:
            return False, "Address is too short (minimum 10 characters)"
        
        if len(value) > 500:
            return False, "Address is too long (maximum 500 characters)"
        
        return True, None
    
    @staticmethod
    def validate_age(value: str) -> Tuple[bool, Optional[str]]:
        """Validate age field"""
        if not value or not value.strip():
            return False, "Age cannot be empty"
        
        try:
            age = int(value)
            if age < 0:
                return False, "Age cannot be negative"
            if age > 150:
                return False, "Age is unrealistic"
            if age < 18:
                return False, "Age must be at least 18 for legal documents"
            return True, None
        except ValueError:
            return False, "Age must be a number"
    
    @staticmethod
    def format_name(value: str) -> str:
        """Format name to title case"""
        return value.strip().title()
    
    @staticmethod
    def format_email(value: str) -> str:
        """Format email to lowercase"""
        return value.strip().lower()
    
    @staticmethod
    def format_phone(value: str) -> str:
        """Format phone number"""
        cleaned = re.sub(r'[-\s\(\)]', '', value.strip())
        if not cleaned.startswith('+91'):
            cleaned = '+91' + cleaned.lstrip('+91')
        return cleaned
    
    @staticmethod
    def format_date(value: str) -> str:
        """Format date to DD-MM-YYYY"""
        try:
            parsed = date_parser.parse(value, dayfirst=True, fuzzy=True)
            return parsed.strftime("%d-%m-%Y")
        except Exception:
            return value
    
    @staticmethod
    def format_address(value: str) -> str:
        """Format address"""
        # Remove extra whitespace
        formatted = re.sub(r'\s+', ' ', value.strip())
        return formatted


class FieldValidatorFactory:
    """Factory to get appropriate validator for field type"""
    
    VALIDATORS = {
        'name': FieldValidator.validate_name,
        'email': FieldValidator.validate_email,
        'phone': FieldValidator.validate_phone,
        'date': FieldValidator.validate_date,
        'address': FieldValidator.validate_address,
        'age': FieldValidator.validate_age,
    }
    
    FORMATTERS = {
        'name': FieldValidator.format_name,
        'email': FieldValidator.format_email,
        'phone': FieldValidator.format_phone,
        'date': FieldValidator.format_date,
        'address': FieldValidator.format_address,
    }
    
    @classmethod
    def get_validator(cls, field_type: str):
        """Get validator function for field type"""
        return cls.VALIDATORS.get(field_type)
    
    @classmethod
    def get_formatter(cls, field_type: str):
        """Get formatter function for field type"""
        return cls.FORMATTERS.get(field_type)
    
    @classmethod
    def validate_and_format(cls, field_type: str, value: str) -> Tuple[bool, Optional[str], str]:
        """
        Validate and format a field value
        
        Returns:
            (is_valid, error_message, formatted_value)
        """
        validator = cls.get_validator(field_type)
        formatter = cls.get_formatter(field_type)
        
        if validator:
            is_valid, error = validator(value)
            if not is_valid:
                return False, error, value
        
        formatted_value = formatter(value) if formatter else value
        return True, None, formatted_value
