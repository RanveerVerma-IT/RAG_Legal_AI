"""
Document Analyzer Module
Analyzes DOCX templates to identify placeholders and required fields
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import logging

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Placeholder:
    """Represents a placeholder field in a document template"""
    field_name: str
    placeholder_text: str
    field_type: str
    label: Optional[str]
    required: bool
    location: str  # paragraph, table, header, footer


@dataclass
class TemplateStructure:
    """Represents the analyzed structure of a document template"""
    template_path: Path
    placeholders: List[Placeholder]
    required_fields: List[str]
    optional_fields: List[str]
    document_metadata: Dict[str, Any]


class DocumentAnalyzer:
    """Analyzes DOCX templates to extract placeholders and field information"""
    
    # Placeholder patterns to detect
    PLACEHOLDER_PATTERNS = [
        r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}",  # {{field_name}}
        r"\[([a-zA-Z_][a-zA-Z0-9_]*)\]",      # [field_name]
        r"__([a-zA-Z_][a-zA-Z0-9_]*)__",      # __field_name__
        r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}",      # {field_name}
    ]
    
    # Field type inference keywords
    FIELD_TYPE_KEYWORDS = {
        "date": ["date", "dob", "birth", "marriage", "wedding", "day", "month", "year"],
        "phone": ["phone", "mobile", "contact", "telephone", "cell"],
        "email": ["email", "mail", "e-mail"],
        "address": ["address", "residence", "location", "street", "city", "state", "pincode", "zip"],
        "text": ["name", "title", "description", "occupation", "education"],
    }
    
    def __init__(self):
        """Initialize the document analyzer"""
        if not DOCX_SUPPORT:
            raise ImportError("python-docx is required for document analysis")
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern) for pattern in self.PLACEHOLDER_PATTERNS]
    
    def analyze_template(self, template_path: Path) -> TemplateStructure:
        """
        Analyze a DOCX template to extract all placeholders and structure
        
        Args:
            template_path: Path to the DOCX template file
            
        Returns:
            TemplateStructure object containing all extracted information
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template cannot be parsed
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        try:
            doc = Document(str(template_path))
            logger.info(f"Analyzing template: {template_path.name}")
            
            # Extract placeholders from all locations
            placeholders = self.extract_placeholders(doc)
            
            # Categorize fields
            required_fields = [p.field_name for p in placeholders if p.required]
            optional_fields = [p.field_name for p in placeholders if not p.required]
            
            # Extract metadata
            metadata = self._extract_metadata(doc, template_path)
            
            structure = TemplateStructure(
                template_path=template_path,
                placeholders=placeholders,
                required_fields=required_fields,
                optional_fields=optional_fields,
                document_metadata=metadata
            )
            
            logger.info(f"Found {len(placeholders)} placeholders ({len(required_fields)} required, {len(optional_fields)} optional)")
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing template {template_path}: {str(e)}")
            raise ValueError(f"Failed to analyze template: {str(e)}")
    
    def extract_placeholders(self, doc: Document) -> List[Placeholder]:
        """
        Extract all placeholders from a DOCX document
        
        Args:
            doc: python-docx Document object
            
        Returns:
            List of unique Placeholder objects
        """
        placeholders_dict: Dict[str, Placeholder] = {}
        
        # Extract from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                found = self._find_placeholders_in_text(para.text, "paragraph")
                for placeholder in found:
                    if placeholder.field_name not in placeholders_dict:
                        placeholders_dict[placeholder.field_name] = placeholder
        
        # Extract from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        found = self._find_placeholders_in_text(cell.text, "table")
                        for placeholder in found:
                            if placeholder.field_name not in placeholders_dict:
                                placeholders_dict[placeholder.field_name] = placeholder
        
        # Extract from headers
        for section in doc.sections:
            header = section.header
            for para in header.paragraphs:
                if para.text.strip():
                    found = self._find_placeholders_in_text(para.text, "header")
                    for placeholder in found:
                        if placeholder.field_name not in placeholders_dict:
                            placeholders_dict[placeholder.field_name] = placeholder
        
        # Extract from footers
        for section in doc.sections:
            footer = section.footer
            for para in footer.paragraphs:
                if para.text.strip():
                    found = self._find_placeholders_in_text(para.text, "footer")
                    for placeholder in found:
                        if placeholder.field_name not in placeholders_dict:
                            placeholders_dict[placeholder.field_name] = placeholder
        
        return list(placeholders_dict.values())
    
    def _find_placeholders_in_text(self, text: str, location: str) -> List[Placeholder]:
        """
        Find all placeholders in a text string
        
        Args:
            text: Text to search for placeholders
            location: Location type (paragraph, table, header, footer)
            
        Returns:
            List of Placeholder objects found in the text
        """
        placeholders = []
        found_fields: Set[str] = set()
        
        for pattern in self.compiled_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                field_name = match.group(1)
                
                # Skip if already found
                if field_name in found_fields:
                    continue
                
                found_fields.add(field_name)
                placeholder_text = match.group(0)
                
                # Get context around the placeholder
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                # Infer field type
                field_type = self.infer_field_type(field_name, context)
                
                # Extract label (text before placeholder)
                label = self._extract_label(text, match.start())
                
                # Determine if required (assume all are required by default)
                required = not self._is_optional_field(field_name, context)
                
                placeholder = Placeholder(
                    field_name=field_name,
                    placeholder_text=placeholder_text,
                    field_type=field_type,
                    label=label,
                    required=required,
                    location=location
                )
                
                placeholders.append(placeholder)
        
        return placeholders
    
    def infer_field_type(self, field_name: str, context: str) -> str:
        """
        Infer the field type based on field name and context
        
        Args:
            field_name: Name of the field
            context: Surrounding text context
            
        Returns:
            Field type string (date, phone, email, address, text)
        """
        field_name_lower = field_name.lower()
        context_lower = context.lower()
        
        # Check field name and context against keywords
        for field_type, keywords in self.FIELD_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in field_name_lower or keyword in context_lower:
                    return field_type
        
        # Default to text
        return "text"
    
    def _extract_label(self, text: str, placeholder_pos: int) -> Optional[str]:
        """
        Extract label text that appears before a placeholder
        
        Args:
            text: Full text containing the placeholder
            placeholder_pos: Position of the placeholder in text
            
        Returns:
            Label text or None
        """
        # Look for text before placeholder (up to 100 chars back)
        start = max(0, placeholder_pos - 100)
        before_text = text[start:placeholder_pos].strip()
        
        # Extract last sentence or phrase
        if ':' in before_text:
            label = before_text.split(':')[-1].strip()
        elif '\n' in before_text:
            label = before_text.split('\n')[-1].strip()
        else:
            # Take last few words
            words = before_text.split()
            label = ' '.join(words[-5:]) if len(words) > 5 else before_text
        
        return label if label and len(label) < 100 else None
    
    def _is_optional_field(self, field_name: str, context: str) -> bool:
        """
        Determine if a field is optional based on name and context
        
        Args:
            field_name: Name of the field
            context: Surrounding text context
            
        Returns:
            True if field is optional, False if required
        """
        optional_keywords = ['optional', 'if applicable', 'if any', 'leave blank']
        context_lower = context.lower()
        
        return any(keyword in context_lower for keyword in optional_keywords)
    
    def _extract_metadata(self, doc: Document, template_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from document
        
        Args:
            doc: python-docx Document object
            template_path: Path to template file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'filename': template_path.name,
            'file_size': template_path.stat().st_size,
            'paragraph_count': len(doc.paragraphs),
            'table_count': len(doc.tables),
        }
        
        # Try to extract core properties
        try:
            core_props = doc.core_properties
            if core_props.title:
                metadata['title'] = core_props.title
            if core_props.author:
                metadata['author'] = core_props.author
            if core_props.created:
                metadata['created'] = core_props.created
            if core_props.modified:
                metadata['modified'] = core_props.modified
        except Exception as e:
            logger.debug(f"Could not extract core properties: {e}")
        
        return metadata


# Global instance
document_analyzer = DocumentAnalyzer()
