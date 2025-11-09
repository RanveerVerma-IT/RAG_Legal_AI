"""
Template Matcher Module
Finds and matches document templates in the documents folder
"""
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TemplateInfo:
    """Information about a document template"""
    file_path: Path
    document_type: str
    location: Optional[str]
    file_size: int
    last_modified: datetime


@dataclass
class TemplateMetadata:
    """Metadata extracted from template filename"""
    document_type: str
    location: Optional[str]
    filename: str


class TemplateMatcher:
    """Matches user queries to document templates in the documents folder"""
    
    # Document type keywords mapping
    DOCUMENT_TYPE_KEYWORDS = {
        "marriage": ["marriage", "wedding", "nikah", "shaadi", "vivah", "matrimony"],
        "birth": ["birth", "janam", "newborn", "child"],
        "death": ["death", "demise", "mortality"],
        "income": ["income", "salary", "earning"],
        "domicile": ["domicile", "residence", "residential"],
        "caste": ["caste", "community", "category"],
    }
    
    # Location/state keywords
    LOCATION_KEYWORDS = {
        "jaipur": ["jaipur"],
        "delhi": ["delhi", "new delhi"],
        "mumbai": ["mumbai", "bombay"],
        "bangalore": ["bangalore", "bengaluru"],
        "rajasthan": ["rajasthan"],
        "maharashtra": ["maharashtra"],
        "karnataka": ["karnataka"],
    }
    
    def __init__(self, documents_folder: str = "documents"):
        """
        Initialize the template matcher
        
        Args:
            documents_folder: Path to folder containing document templates
        """
        self.documents_folder = Path(documents_folder)
        self._template_cache: Dict[str, TemplateInfo] = {}
        self._cache_timestamp: Optional[datetime] = None
    
    def find_template(self, doc_type: str, location: Optional[str] = None) -> Optional[Path]:
        """
        Find a matching template for the given document type and location
        
        Args:
            doc_type: Document type (e.g., "marriage", "birth")
            location: Location/state (e.g., "jaipur", "delhi")
            
        Returns:
            Path to matching template file, or None if not found
        """
        logger.info(f"Searching for template: doc_type='{doc_type}', location='{location}'")
        
        # Get all available templates
        templates = self.list_available_templates()
        
        if not templates:
            logger.warning("No templates found in documents folder")
            return None
        
        # Normalize inputs
        doc_type_normalized = self._normalize_text(doc_type)
        location_normalized = self._normalize_text(location) if location else None
        
        # Find best match
        best_match = None
        best_score = 0
        
        for template in templates:
            score = self._calculate_match_score(
                template, doc_type_normalized, location_normalized
            )
            
            if score > best_score:
                best_score = score
                best_match = template
        
        if best_match and best_score > 0:
            logger.info(f"Found matching template: {best_match.file_path.name} (score: {best_score})")
            return best_match.file_path
        
        logger.warning(f"No matching template found for doc_type='{doc_type}', location='{location}'")
        return None
    
    def list_available_templates(self, force_refresh: bool = False) -> List[TemplateInfo]:
        """
        List all available document templates
        
        Args:
            force_refresh: Force refresh of template cache
            
        Returns:
            List of TemplateInfo objects
        """
        # Check if cache is valid (refresh every 60 seconds)
        if not force_refresh and self._cache_timestamp:
            age = (datetime.now() - self._cache_timestamp).total_seconds()
            if age < 60 and self._template_cache:
                return list(self._template_cache.values())
        
        # Scan documents folder
        templates = []
        
        if not self.documents_folder.exists():
            logger.warning(f"Documents folder not found: {self.documents_folder}")
            return templates
        
        # Find all DOCX files
        for file_path in self.documents_folder.glob("*.docx"):
            # Skip temporary files
            if file_path.name.startswith('~$'):
                continue
            
            try:
                metadata = self.get_template_metadata(file_path)
                stat = file_path.stat()
                
                template_info = TemplateInfo(
                    file_path=file_path,
                    document_type=metadata.document_type,
                    location=metadata.location,
                    file_size=stat.st_size,
                    last_modified=datetime.fromtimestamp(stat.st_mtime)
                )
                
                templates.append(template_info)
                self._template_cache[str(file_path)] = template_info
                
            except Exception as e:
                logger.error(f"Error processing template {file_path.name}: {e}")
        
        self._cache_timestamp = datetime.now()
        logger.info(f"Found {len(templates)} templates in documents folder")
        
        return templates
    
    def get_template_metadata(self, template_path: Path) -> TemplateMetadata:
        """
        Extract metadata from template filename
        
        Args:
            template_path: Path to template file
            
        Returns:
            TemplateMetadata object
        """
        filename = template_path.stem  # Without extension
        filename_lower = filename.lower()
        
        # Extract location from filename
        location = None
        for loc, keywords in self.LOCATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    location = loc
                    break
            if location:
                break
        
        # Extract document type from filename
        doc_type = "unknown"
        for dtype, keywords in self.DOCUMENT_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    doc_type = dtype
                    break
            if doc_type != "unknown":
                break
        
        return TemplateMetadata(
            document_type=doc_type,
            location=location,
            filename=filename
        )
    
    def _calculate_match_score(
        self, 
        template: TemplateInfo, 
        doc_type: str, 
        location: Optional[str]
    ) -> int:
        """
        Calculate match score for a template
        
        Args:
            template: TemplateInfo object
            doc_type: Normalized document type
            location: Normalized location (optional)
            
        Returns:
            Match score (higher is better)
        """
        score = 0
        
        # Check document type match
        if doc_type:
            # Exact match
            if template.document_type == doc_type:
                score += 100
            # Keyword match
            elif doc_type in template.document_type or template.document_type in doc_type:
                score += 50
            # Check filename
            elif doc_type in self._normalize_text(template.file_path.stem):
                score += 30
        
        # Check location match
        if location and template.location:
            # Exact match
            if template.location == location:
                score += 50
            # Partial match
            elif location in template.location or template.location in location:
                score += 25
            # Check filename
            elif location in self._normalize_text(template.file_path.stem):
                score += 15
        elif location and not template.location:
            # Penalize if location specified but template has no location
            score -= 10
        elif not location and template.location:
            # Slight preference for generic templates when no location specified
            score += 5
        
        return max(0, score)
    
    def _normalize_text(self, text: Optional[str]) -> str:
        """
        Normalize text for matching
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Remove special characters
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def get_available_document_types(self) -> List[str]:
        """
        Get list of available document types
        
        Returns:
            List of document type strings
        """
        templates = self.list_available_templates()
        doc_types = set(t.document_type for t in templates if t.document_type != "unknown")
        return sorted(list(doc_types))
    
    def get_available_locations(self) -> List[str]:
        """
        Get list of available locations
        
        Returns:
            List of location strings
        """
        templates = self.list_available_templates()
        locations = set(t.location for t in templates if t.location)
        return sorted(list(locations))
    
    def clear_cache(self) -> None:
        """Clear the template cache"""
        self._template_cache.clear()
        self._cache_timestamp = None
        logger.info("Template cache cleared")


# Global instance
template_matcher = TemplateMatcher()
