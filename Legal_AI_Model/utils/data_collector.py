"""
Data Collector Module
Manages interactive collection of missing field values with skip functionality
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CollectionState:
    """State of data collection process"""
    missing_fields: List[str]
    current_field_index: int = 0
    collected_data: Dict[str, Any] = field(default_factory=dict)
    skipped_fields: List[str] = field(default_factory=list)
    validation_errors: Dict[str, str] = field(default_factory=dict)


class DataCollector:
    """Manages interactive collection of missing field values"""
    
    # Keywords that indicate user wants to skip
    SKIP_KEYWORDS = ["skip", "pass", "next", "leave blank", "leave empty", "n/a", "na"]
    
    # Clean, concise question templates with skip options
    QUESTION_TEMPLATES = {
        "date": "📅 **{label}**\n\n"
                "Please enter in DD-MM-YYYY format (e.g., 15-08-1990)\n"
                "⏭️ Press Enter without typing to skip",
        
        "phone": "📱 **{label}**\n\n"
                 "Please enter 10-digit mobile number (e.g., 9876543210)\n"
                 "⏭️ Press Enter without typing to skip",
        
        "email": "📧 **{label}**\n\n"
                 "Please enter email address (e.g., name@email.com)\n"
                 "⏭️ Press Enter without typing to skip",
        
        "address": "🏠 **{label}**\n\n"
                   "Please enter complete address with PIN code\n"
                   "⏭️ Press Enter without typing to skip",
        
        "text": "✏️ **{label}**\n\n"
                "⏭️ Press Enter without typing to skip",
    }
    
    # Detailed, context-rich field descriptions
    FIELD_DESCRIPTIONS = {
        # Marriage-related fields
        "groom_name": {
            "what": "Full legal name of the groom",
            "why": "This will appear on the official marriage certificate",
            "example": "Rajesh Kumar Sharma",
            "tip": "Use the exact name as it appears on your Aadhaar card or passport"
        },
        "bride_name": {
            "what": "Full legal name of the bride",
            "why": "This will appear on the official marriage certificate",
            "example": "Priya Singh",
            "tip": "Use the exact name as it appears on your Aadhaar card or passport"
        },
        "groom_father_name": {
            "what": "Full name of the groom's father",
            "why": "Required for official marriage registration records",
            "example": "Ramesh Kumar Sharma",
            "tip": "Include first name, middle name (if any), and surname"
        },
        "bride_father_name": {
            "what": "Full name of the bride's father",
            "why": "Required for official marriage registration records",
            "example": "Vikram Singh",
            "tip": "Include first name, middle name (if any), and surname"
        },
        "groom_mother_name": {
            "what": "Full name of the groom's mother",
            "why": "Required for official marriage registration records",
            "example": "Sunita Devi Sharma",
            "tip": "Include first name, middle name (if any), and surname"
        },
        "bride_mother_name": {
            "what": "Full name of the bride's mother",
            "why": "Required for official marriage registration records",
            "example": "Meera Singh",
            "tip": "Include first name, middle name (if any), and surname"
        },
        "marriage_date": {
            "what": "The date when your marriage ceremony took place",
            "why": "This is the official date of your marriage",
            "example": "10-11-2024 (for November 10, 2024)",
            "tip": "Use the date of your wedding ceremony, not the registration date"
        },
        "marriage_place": {
            "what": "Location where the marriage ceremony was performed",
            "why": "Required to identify the jurisdiction of marriage",
            "example": "Jaipur, Rajasthan or City Palace, Jaipur",
            "tip": "Include the venue name and city"
        },
        
        # Birth certificate fields
        "child_name": {
            "what": "Full name of the child",
            "why": "This will be the official name on the birth certificate",
            "example": "Aarav Kumar Sharma",
            "tip": "Choose carefully as this becomes the legal name"
        },
        "father_name": {
            "what": "Full legal name of the father",
            "why": "Required for official birth records",
            "example": "Rajesh Kumar Sharma",
            "tip": "Use the exact name as it appears on official documents"
        },
        "mother_name": {
            "what": "Full legal name of the mother",
            "why": "Required for official birth records",
            "example": "Priya Sharma",
            "tip": "Use the exact name as it appears on official documents"
        },
        "date_of_birth": {
            "what": "The date when the person was born",
            "why": "This becomes the official date of birth",
            "example": "15-08-1990 (for August 15, 1990)",
            "tip": "Verify from hospital records or existing documents"
        },
        "place_of_birth": {
            "what": "City or town where the person was born",
            "why": "Required for official birth records",
            "example": "Jaipur or SMS Hospital, Jaipur",
            "tip": "Include hospital name if birth was in a hospital"
        },
        
        # Contact information
        "groom_address": {
            "what": "Complete residential address of the groom",
            "why": "Required for official correspondence and records",
            "example": "123 Main Street, Malviya Nagar, Jaipur, Rajasthan - 302017",
            "tip": "Include house number, street, area, city, state, and PIN code"
        },
        "bride_address": {
            "what": "Complete residential address of the bride",
            "why": "Required for official correspondence and records",
            "example": "456 Park Avenue, C-Scheme, Jaipur, Rajasthan - 302001",
            "tip": "Include house number, street, area, city, state, and PIN code"
        },
        "address": {
            "what": "Complete residential address",
            "why": "Required for official correspondence",
            "example": "123 Main Street, Malviya Nagar, Jaipur, Rajasthan - 302017",
            "tip": "Include house number, street, area, city, state, and PIN code"
        },
        "groom_phone": {
            "what": "Mobile number of the groom",
            "why": "For contact regarding the certificate",
            "example": "9876543210",
            "tip": "Enter 10-digit mobile number without +91 or spaces"
        },
        "bride_phone": {
            "what": "Mobile number of the bride",
            "why": "For contact regarding the certificate",
            "example": "9123456789",
            "tip": "Enter 10-digit mobile number without +91 or spaces"
        },
        "phone": {
            "what": "Contact mobile number",
            "why": "For communication regarding your application",
            "example": "9876543210",
            "tip": "Enter 10-digit mobile number without +91 or spaces"
        },
        "groom_email": {
            "what": "Email address of the groom",
            "why": "For sending digital copy and updates",
            "example": "rajesh.kumar@email.com",
            "tip": "Use an email you check regularly"
        },
        "bride_email": {
            "what": "Email address of the bride",
            "why": "For sending digital copy and updates",
            "example": "priya.singh@email.com",
            "tip": "Use an email you check regularly"
        },
        "email": {
            "what": "Your email address",
            "why": "For sending digital copy and updates",
            "example": "your.name@email.com",
            "tip": "Use an email you check regularly"
        },
        
        # Additional fields
        "groom_age": {
            "what": "Age of the groom at the time of marriage",
            "why": "Required to verify legal age for marriage",
            "example": "28",
            "tip": "Must be 21 years or above for males"
        },
        "bride_age": {
            "what": "Age of the bride at the time of marriage",
            "why": "Required to verify legal age for marriage",
            "example": "25",
            "tip": "Must be 18 years or above for females"
        },
        "groom_occupation": {
            "what": "Current profession or occupation of the groom",
            "why": "Required for official records",
            "example": "Software Engineer or Business Owner",
            "tip": "Be specific about your profession"
        },
        "bride_occupation": {
            "what": "Current profession or occupation of the bride",
            "why": "Required for official records",
            "example": "Teacher or Doctor",
            "tip": "Be specific about your profession"
        },
        "witness_1_name": {
            "what": "Full name of the first witness to the marriage",
            "why": "Legal requirement for marriage registration",
            "example": "Amit Kumar Verma",
            "tip": "Must be an adult who was present at the ceremony"
        },
        "witness_2_name": {
            "what": "Full name of the second witness to the marriage",
            "why": "Legal requirement for marriage registration",
            "example": "Neha Gupta",
            "tip": "Must be an adult who was present at the ceremony"
        },
        "applicant_name": {
            "what": "Full name of the person applying for this certificate",
            "why": "To identify who is requesting this document",
            "example": "Rajesh Kumar Sharma",
            "tip": "Use your legal name as per official documents"
        },
        "gram_panchayat": {
            "what": "Name of the Gram Panchayat (village council)",
            "why": "Required to identify the local administrative body",
            "example": "Sanganer Gram Panchayat",
            "tip": "Enter the name of your local Gram Panchayat office"
        },
    }
    
    def __init__(self):
        """Initialize the data collector"""
        pass
    
    def generate_question(
        self, 
        field_name: str, 
        field_type: str = "text",
        field_label: Optional[str] = None
    ) -> str:
        """
        Generate an intelligent, context-rich question for a field
        
        Args:
            field_name: Name of the field
            field_type: Type of the field (date, phone, email, address, text)
            field_label: Optional custom label for the field
            
        Returns:
            Detailed question with context, examples, and tips
        """
        # Use label if provided, otherwise format field name
        if field_label:
            label = field_label
        else:
            label = self.format_field_label(field_name)
        
        # Get template for field type
        template = self.QUESTION_TEMPLATES.get(field_type, self.QUESTION_TEMPLATES["text"])
        
        # Format basic question
        question = template.format(label=label)
        
        # Add detailed field-specific information if available
        if field_name in self.FIELD_DESCRIPTIONS:
            desc = self.FIELD_DESCRIPTIONS[field_name]
            
            # Check if it's a detailed description (dict) or simple string
            if isinstance(desc, dict):
                # Build comprehensive question with all details
                details = []
                
                # What is this field?
                if "what" in desc:
                    details.append(f"📋 **What to enter**: {desc['what']}")
                
                # Why is it needed?
                if "why" in desc:
                    details.append(f"❓ **Why needed**: {desc['why']}")
                
                # Example
                if "example" in desc:
                    details.append(f"✏️ **Example**: {desc['example']}")
                
                # Helpful tip
                if "tip" in desc:
                    details.append(f"💡 **Tip**: {desc['tip']}")
                
                # Combine everything
                question = f"{question}\n\n" + "\n".join(details)
            else:
                # Simple string description
                question = f"{question}\n\n💡 **Note**: {desc}"
        
        return question
    
    def is_skip_request(self, user_input: str) -> bool:
        """
        Check if user input indicates a skip request
        Supports both keywords and empty input (double enter)
        
        Args:
            user_input: User's input text
            
        Returns:
            True if user wants to skip
        """
        # Empty input (double enter) = skip
        if not user_input or not user_input.strip():
            return True
        
        input_lower = user_input.lower().strip()
        
        # Check for skip keywords
        return any(keyword in input_lower for keyword in self.SKIP_KEYWORDS)
    
    def handle_skip(self, field_name: str, state: CollectionState) -> None:
        """
        Handle a skip request for a field
        
        Args:
            field_name: Name of the field being skipped
            state: Current collection state
        """
        if field_name not in state.skipped_fields:
            state.skipped_fields.append(field_name)
            logger.info(f"Field skipped: {field_name}")
    
    def get_next_field(self, state: CollectionState) -> Optional[str]:
        """
        Get the next field to collect
        
        Args:
            state: Current collection state
            
        Returns:
            Next field name, or None if all fields processed
        """
        if state.current_field_index < len(state.missing_fields):
            return state.missing_fields[state.current_field_index]
        return None
    
    def advance_to_next_field(self, state: CollectionState) -> None:
        """
        Move to the next field in the collection process
        
        Args:
            state: Current collection state
        """
        state.current_field_index += 1
    
    def is_collection_complete(self, state: CollectionState) -> bool:
        """
        Check if collection is complete
        
        Args:
            state: Current collection state
            
        Returns:
            True if all fields have been processed
        """
        return state.current_field_index >= len(state.missing_fields)
    
    def get_collection_summary(self, state: CollectionState) -> Dict[str, Any]:
        """
        Get summary of collection process
        
        Args:
            state: Current collection state
            
        Returns:
            Dictionary with collection statistics
        """
        total_fields = len(state.missing_fields)
        collected_count = len(state.collected_data)
        skipped_count = len(state.skipped_fields)
        
        return {
            "total_fields": total_fields,
            "collected_count": collected_count,
            "skipped_count": skipped_count,
            "completion_rate": (collected_count + skipped_count) / total_fields if total_fields > 0 else 1.0
        }
    
    def format_field_label(self, field_name: str) -> str:
        """
        Format field name into a readable label
        
        Args:
            field_name: Field name to format
            
        Returns:
            Formatted label
        """
        # Replace underscores with spaces
        label = field_name.replace('_', ' ')
        
        # Capitalize each word
        label = label.title()
        
        # Handle special cases and common abbreviations
        replacements = {
            'Dob': 'Date of Birth',
            'Email': 'Email Address',
            'Phone': 'Phone Number',
            'Mobile': 'Mobile Number',
            'Groom': "Groom's",
            'Bride': "Bride's",
            'Father': "Father's",
            'Mother': "Mother's",
            'Child': "Child's",
            'Witness 1': 'First Witness',
            'Witness 2': 'Second Witness',
            'Pin Code': 'PIN Code',
            'Pincode': 'PIN Code',
        }
        
        for old, new in replacements.items():
            if old in label:
                label = label.replace(old, new)
        
        return label
    
    def get_field_examples(self, field_name: str, field_type: str) -> Optional[str]:
        """
        Get example values for a field
        
        Args:
            field_name: Name of the field
            field_type: Type of the field
            
        Returns:
            Example string or None
        """
        examples = {
            "groom_name": "Example: Rajesh Kumar Sharma",
            "bride_name": "Example: Priya Singh",
            "father_name": "Example: Ramesh Kumar",
            "mother_name": "Example: Sunita Devi",
            "date_of_birth": "Example: 15-08-1990",
            "marriage_date": "Example: 10-11-2024",
            "phone": "Example: 9876543210",
            "email": "Example: rajesh.kumar@email.com",
            "address": "Example: 123 Main Street, Malviya Nagar, Jaipur, Rajasthan - 302017",
            "place_of_birth": "Example: Jaipur",
            "marriage_place": "Example: Jaipur, Rajasthan",
            "occupation": "Example: Software Engineer",
            "age": "Example: 28",
        }
        
        # Check for exact match
        if field_name in examples:
            return examples[field_name]
        
        # Check for partial matches
        for key, example in examples.items():
            if key in field_name:
                return example
        
        return None


# Global instance
data_collector = DataCollector()
