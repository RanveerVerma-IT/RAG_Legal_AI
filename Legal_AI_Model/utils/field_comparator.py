"""
Field Comparator Module
Compares extracted fields with required fields using intelligent matching
"""
import re
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FieldComparison:
    """Results of field comparison"""
    matched_fields: Dict[str, Any]  # field_name: value
    missing_fields: List[str]
    skippable_fields: List[str]
    field_mapping: Dict[str, str]  # extracted_name: required_name


class FieldComparator:
    """Compares extracted fields with required fields using fuzzy matching"""
    
    # Synonym mappings for semantic matching
    FIELD_SYNONYMS = {
        "groom": ["husband", "bridegroom", "spouse_male"],
        "bride": ["wife", "spouse_female"],
        "father": ["dad", "papa", "parent_male"],
        "mother": ["mom", "mama", "parent_female"],
        "child": ["baby", "newborn", "infant", "kid"],
        "phone": ["mobile", "contact", "telephone", "cell"],
        "email": ["mail", "e-mail", "email_address"],
        "address": ["residence", "location", "residential_address"],
        "dob": ["date_of_birth", "birth_date", "birthdate"],
    }
    
    # Maximum Levenshtein distance for fuzzy matching
    MAX_FUZZY_DISTANCE = 3
    
    def __init__(self):
        """Initialize the field comparator"""
        pass
    
    def compare_fields(
        self, 
        required: List[str], 
        extracted: Dict[str, Any]
    ) -> FieldComparison:
        """
        Compare required fields with extracted fields
        
        Args:
            required: List of required field names
            extracted: Dictionary of extracted field values
            
        Returns:
            FieldComparison object with matching results
        """
        logger.info(f"Comparing {len(required)} required fields with {len(extracted)} extracted fields")
        
        matched_fields: Dict[str, Any] = {}
        field_mapping: Dict[str, str] = {}
        missing_fields: List[str] = []
        
        # Normalize extracted field names
        normalized_extracted = {
            self.normalize_field_name(k): (k, v) 
            for k, v in extracted.items()
        }
        
        # Try to match each required field
        for req_field in required:
            normalized_req = self.normalize_field_name(req_field)
            
            # Try exact match first
            if normalized_req in normalized_extracted:
                original_name, value = normalized_extracted[normalized_req]
                matched_fields[req_field] = value
                field_mapping[original_name] = req_field
                logger.debug(f"Exact match: {req_field} = {original_name}")
                continue
            
            # Try fuzzy match
            matched_name = self.match_field_names(
                req_field, 
                list(extracted.keys())
            )
            
            if matched_name:
                matched_fields[req_field] = extracted[matched_name]
                field_mapping[matched_name] = req_field
                logger.debug(f"Fuzzy match: {req_field} = {matched_name}")
                continue
            
            # No match found
            missing_fields.append(req_field)
            logger.debug(f"No match found for: {req_field}")
        
        # All fields are skippable (user can choose to skip any field)
        skippable_fields = required.copy()
        
        comparison = FieldComparison(
            matched_fields=matched_fields,
            missing_fields=missing_fields,
            skippable_fields=skippable_fields,
            field_mapping=field_mapping
        )
        
        logger.info(
            f"Comparison complete: {len(matched_fields)} matched, "
            f"{len(missing_fields)} missing"
        )
        
        return comparison
    
    def normalize_field_name(self, field_name: str) -> str:
        """
        Normalize field name for matching
        
        Args:
            field_name: Field name to normalize
            
        Returns:
            Normalized field name
        """
        if not field_name:
            return ""
        
        # Convert to lowercase
        normalized = field_name.lower()
        
        # Remove special characters and replace with underscore
        normalized = re.sub(r'[^a-z0-9]+', '_', normalized)
        
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        
        # Remove multiple consecutive underscores
        normalized = re.sub(r'_+', '_', normalized)
        
        return normalized
    
    def match_field_names(
        self, 
        required_name: str, 
        extracted_names: List[str]
    ) -> Optional[str]:
        """
        Find best matching field name using fuzzy matching
        
        Args:
            required_name: Required field name
            extracted_names: List of extracted field names
            
        Returns:
            Best matching extracted field name, or None
        """
        if not extracted_names:
            return None
        
        required_normalized = self.normalize_field_name(required_name)
        best_match = None
        best_score = 0
        
        for extracted_name in extracted_names:
            extracted_normalized = self.normalize_field_name(extracted_name)
            
            # Calculate match score
            score = self._calculate_match_score(
                required_normalized, 
                extracted_normalized
            )
            
            if score > best_score:
                best_score = score
                best_match = extracted_name
        
        # Only return match if score is above threshold
        if best_score >= 50:  # Threshold for acceptable match
            return best_match
        
        return None
    
    def _calculate_match_score(self, name1: str, name2: str) -> int:
        """
        Calculate match score between two field names
        
        Args:
            name1: First field name (normalized)
            name2: Second field name (normalized)
            
        Returns:
            Match score (0-100)
        """
        # Exact match
        if name1 == name2:
            return 100
        
        # One contains the other
        if name1 in name2 or name2 in name1:
            return 80
        
        # Check synonyms
        if self._are_synonyms(name1, name2):
            return 90
        
        # Levenshtein distance
        distance = self._levenshtein_distance(name1, name2)
        if distance <= self.MAX_FUZZY_DISTANCE:
            # Convert distance to score (closer = higher score)
            score = 70 - (distance * 10)
            return max(score, 0)
        
        # Check if they share significant words
        words1 = set(name1.split('_'))
        words2 = set(name2.split('_'))
        common_words = words1.intersection(words2)
        
        if common_words:
            # Score based on proportion of common words
            proportion = len(common_words) / max(len(words1), len(words2))
            return int(proportion * 60)
        
        return 0
    
    def _are_synonyms(self, name1: str, name2: str) -> bool:
        """
        Check if two field names are synonyms
        
        Args:
            name1: First field name
            name2: Second field name
            
        Returns:
            True if they are synonyms
        """
        for base, synonyms in self.FIELD_SYNONYMS.items():
            all_forms = [base] + synonyms
            if name1 in all_forms and name2 in all_forms:
                return True
        
        return False
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Levenshtein distance
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


# Global instance
field_comparator = FieldComparator()
