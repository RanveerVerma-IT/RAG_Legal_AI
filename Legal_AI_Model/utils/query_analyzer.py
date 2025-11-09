"""
Query Analyzer Module
Analyzes user queries to extract document intent and field values
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

from utils.intent_detector import intent_detector
from utils.entity_extractor import entity_extractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryAnalysis:
    """Results of query analysis"""
    document_type: Optional[str]
    location: Optional[str]
    extracted_fields: Dict[str, Any]
    confidence_score: float
    raw_query: str


class QueryAnalyzer:
    """Analyzes user queries to extract document type, location, and field values"""
    
    def __init__(self):
        """Initialize the query analyzer"""
        self.intent_detector = intent_detector
        self.entity_extractor = entity_extractor
    
    def analyze_query(self, user_input: str) -> QueryAnalysis:
        """
        Analyze user query to extract all relevant information
        
        Args:
            user_input: User's input text
            
        Returns:
            QueryAnalysis object with extracted information
        """
        logger.info(f"Analyzing query: {user_input[:100]}...")
        
        # Detect document type and location using intent detector
        doc_type, location = self.intent_detector.detect_intent(user_input)
        
        # Extract field values using entity extractor
        extracted_fields = self.entity_extractor.extract_entities(user_input)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(doc_type, location, extracted_fields)
        
        analysis = QueryAnalysis(
            document_type=doc_type,
            location=location,
            extracted_fields=extracted_fields,
            confidence_score=confidence,
            raw_query=user_input
        )
        
        logger.info(
            f"Query analysis complete: doc_type={doc_type}, location={location}, "
            f"fields={len(extracted_fields)}, confidence={confidence:.2f}"
        )
        
        return analysis
    
    def _calculate_confidence(
        self, 
        doc_type: Optional[str], 
        location: Optional[str], 
        fields: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for the analysis
        
        Args:
            doc_type: Detected document type
            location: Detected location
            fields: Extracted fields
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # Document type detected
        if doc_type:
            score += 0.4
        
        # Location detected
        if location:
            score += 0.2
        
        # Fields extracted
        if fields:
            # Add score based on number of fields (up to 0.4)
            field_score = min(len(fields) * 0.1, 0.4)
            score += field_score
        
        return min(score, 1.0)
    
    def extract_document_type(self, user_input: str) -> Optional[str]:
        """
        Extract just the document type from query
        
        Args:
            user_input: User's input text
            
        Returns:
            Document type or None
        """
        doc_type, _ = self.intent_detector.detect_intent(user_input)
        return doc_type
    
    def extract_location(self, user_input: str) -> Optional[str]:
        """
        Extract just the location from query
        
        Args:
            user_input: User's input text
            
        Returns:
            Location or None
        """
        _, location = self.intent_detector.detect_intent(user_input)
        return location
    
    def extract_fields(self, user_input: str) -> Dict[str, Any]:
        """
        Extract just the field values from query
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary of extracted fields
        """
        return self.entity_extractor.extract_entities(user_input)


# Global instance
query_analyzer = QueryAnalyzer()
