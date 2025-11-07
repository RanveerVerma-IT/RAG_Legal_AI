"""
Enhanced Entity Extractor
Provides robust entity extraction with multiple patterns and validation
"""
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from dateutil import parser as date_parser


class EntityExtractor:
    """Enhanced entity extraction with multiple pattern matching"""
    
    # Comprehensive regex patterns
    NAME_PATTERNS = [
        r"(?:name is|name:|my name is|called)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)",
        r"(?:I am|I'm)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)",
        r"for\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)",
    ]
    
    EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    
    PHONE_PATTERNS = [
        r"\+91[-\s]?[6-9]\d{9}",
        r"[6-9]\d{9}",
        r"\(\+91\)[-\s]?[6-9]\d{9}",
    ]
    
    DATE_PATTERNS = [
        r"(?:dob|date of birth|born on|birth date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        r"(?:dob|date of birth|born on|birth date)\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})",
    ]
    
    GROOM_NAME_PATTERNS = [
        r"groom['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"groom[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"husband['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
    ]
    
    BRIDE_NAME_PATTERNS = [
        r"bride['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"bride[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"wife['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
    ]
    
    FATHER_NAME_PATTERNS = [
        r"father['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"father[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"son of\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
    ]
    
    MOTHER_NAME_PATTERNS = [
        r"mother['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"mother[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"daughter of\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
    ]
    
    CHILD_NAME_PATTERNS = [
        r"child['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"child[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"baby['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        r"newborn['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
    ]
    
    MARRIAGE_DATE_PATTERNS = [
        r"marriage\s+date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        r"married\s+on[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        r"wedding\s+date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        r"marriage\s+date[:\s]+([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})",
    ]
    
    ADDRESS_PATTERNS = [
        r"address[:\s]+(.+?)(?:\n|$)",
        r"residing at[:\s]+(.+?)(?:\n|$)",
        r"living at[:\s]+(.+?)(?:\n|$)",
    ]
    
    def __init__(self):
        """Initialize the entity extractor"""
        pass
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract all possible entities from text
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Extract names
        entities.update(self._extract_names(text))
        
        # Extract contact information
        entities.update(self._extract_contact_info(text))
        
        # Extract dates
        entities.update(self._extract_dates(text))
        
        # Extract addresses
        entities.update(self._extract_addresses(text))
        
        # Extract marriage-specific entities
        entities.update(self._extract_marriage_entities(text))
        
        return entities
    
    def _extract_names(self, text: str) -> Dict[str, str]:
        """Extract various name fields"""
        names = {}
        
        # Child name (specific for birth certificates)
        for pattern in self.CHILD_NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                names["child_name"] = name
                names["applicant_name"] = name  # Backward compatibility
                break
        
        # General name (if child name not found)
        if "child_name" not in names:
            for pattern in self.NAME_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    names["applicant_name"] = name
                    names["child_name"] = name  # Also map to child_name
                    break
        
        # Father's name
        for pattern in self.FATHER_NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                names["father_name"] = match.group(1).strip()
                break
        
        # Mother's name
        for pattern in self.MOTHER_NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                names["mother_name"] = match.group(1).strip()
                break
        
        return names
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract email and phone"""
        contact = {}
        
        # Email
        email_match = re.search(self.EMAIL_PATTERN, text, re.IGNORECASE)
        if email_match:
            email = email_match.group(0)
            contact["email"] = email
            contact["contact_email"] = email
        
        # Phone
        for pattern in self.PHONE_PATTERNS:
            phone_match = re.search(pattern, text)
            if phone_match:
                phone = phone_match.group(0)
                # Normalize phone format
                phone = re.sub(r'[-\s\(\)]', '', phone)
                if not phone.startswith('+91'):
                    phone = '+91' + phone.lstrip('+91')
                contact["phone"] = phone
                contact["contact_phone"] = phone
                break
        
        return contact
    
    def _extract_dates(self, text: str) -> Dict[str, str]:
        """Extract date fields"""
        dates = {}
        
        # Date of birth
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    parsed = date_parser.parse(match.group(1), dayfirst=True, fuzzy=True)
                    dob_str = parsed.strftime("%d-%m-%Y")
                    dates["date_of_birth"] = dob_str
                    dates["groom_date_of_birth"] = dob_str
                    dates["bride_date_of_birth"] = dob_str
                except Exception:
                    pass
                break
        
        return dates
    
    def _extract_addresses(self, text: str) -> Dict[str, str]:
        """Extract address fields"""
        addresses = {}
        
        for pattern in self.ADDRESS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                addr = match.group(1).strip()
                # Clean up address
                addr = re.sub(r'\s+', ' ', addr)
                addresses["address"] = addr[:300]
                break
        
        return addresses
    
    def _extract_marriage_entities(self, text: str) -> Dict[str, str]:
        """Extract marriage-specific entities"""
        entities = {}
        
        # Groom name
        for pattern in self.GROOM_NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities["groom_name"] = match.group(1).strip()
                break
        
        # Bride name
        for pattern in self.BRIDE_NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities["bride_name"] = match.group(1).strip()
                break
        
        # Marriage date
        for pattern in self.MARRIAGE_DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    parsed = date_parser.parse(match.group(1), dayfirst=True, fuzzy=True)
                    entities["marriage_date"] = parsed.strftime("%d-%m-%Y")
                except Exception:
                    pass
                break
        
        return entities


# Global instance
entity_extractor = EntityExtractor()
