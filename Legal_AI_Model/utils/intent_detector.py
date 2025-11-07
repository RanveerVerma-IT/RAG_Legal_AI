"""
Intent Detector
Detects user intent for document generation
"""
import re
from typing import Tuple, Optional
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentDetector:
    """Detects document type and state from user input"""
    
    # Document type keywords
    DOCUMENT_KEYWORDS = {
        "marriage_certificate_application": {
            'marriage certificate', 'marriage application', 'marriage form',
            'marriage registration', 'marriage cert', 'wedding certificate',
            'wedding application', 'marriage license', 'nikah certificate',
            'shaadi certificate', 'vivah certificate'
        },
        "birth_certificate": {
            'birth certificate', 'birth cert', 'birth registration',
            'birth form', 'child certificate', 'newborn certificate',
            'janam certificate', 'birth proof'
        }
    }
    
    # State keywords with cities
    STATE_KEYWORDS = {
        'rajasthan': {
            'rajasthan', 'jaipur', 'jodhpur', 'udaipur', 'kota', 'ajmer',
            'bikaner', 'alwar', 'bharatpur', 'sikar'
        },
        'delhi': {
            'delhi', 'new delhi', 'ncr', 'national capital'
        },
        'maharashtra': {
            'maharashtra', 'mumbai', 'pune', 'nagpur', 'thane', 'nashik'
        },
        'karnataka': {
            'karnataka', 'bangalore', 'bengaluru', 'mysore', 'mangalore', 'hubli'
        },
        'uttar pradesh': {
            'uttar pradesh', 'up', 'lucknow', 'kanpur', 'agra', 'varanasi',
            'noida', 'ghaziabad', 'meerut'
        },
        'tamil nadu': {
            'tamil nadu', 'chennai', 'coimbatore', 'madurai', 'salem', 'tiruchirappalli'
        }
    }
    
    def __init__(self, default_state: str = "rajasthan"):
        self.default_state = default_state
    
    def detect_intent(self, user_input: str) -> Tuple[Optional[str], str]:
        """
        Detect document type and state from user input
        
        Args:
            user_input: User's input text
            
        Returns:
            (doc_type, state) tuple
        """
        input_lower = user_input.lower()
        
        # Detect document type
        doc_type = self._detect_document_type(input_lower)
        
        # Detect state
        state = self._detect_state(input_lower)
        
        logger.info(f"Detected intent - Document: {doc_type}, State: {state}")
        
        return doc_type, state
    
    def _detect_document_type(self, text: str) -> Optional[str]:
        """Detect document type from text"""
        # Check each document type
        for doc_type, keywords in self.DOCUMENT_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return doc_type
        
        return None
    
    def _detect_state(self, text: str) -> str:
        """Detect state from text"""
        # Check each state
        for state, keywords in self.STATE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return state
        
        # Return default if not found
        return self.default_state
    
    def get_supported_documents(self) -> list:
        """Get list of supported document types"""
        return list(self.DOCUMENT_KEYWORDS.keys())
    
    def get_supported_states(self) -> list:
        """Get list of supported states"""
        return list(self.STATE_KEYWORDS.keys())
    
    def get_document_keywords(self, doc_type: str) -> set:
        """Get keywords for a document type"""
        return self.DOCUMENT_KEYWORDS.get(doc_type, set())
    
    def add_document_keyword(self, doc_type: str, keyword: str) -> None:
        """Add a new keyword for document type"""
        if doc_type in self.DOCUMENT_KEYWORDS:
            self.DOCUMENT_KEYWORDS[doc_type].add(keyword.lower())
            logger.info(f"Added keyword '{keyword}' for document type '{doc_type}'")
    
    def add_state_keyword(self, state: str, keyword: str) -> None:
        """Add a new keyword for state"""
        if state in self.STATE_KEYWORDS:
            self.STATE_KEYWORDS[state].add(keyword.lower())
            logger.info(f"Added keyword '{keyword}' for state '{state}'")


# Global instance
intent_detector = IntentDetector()
