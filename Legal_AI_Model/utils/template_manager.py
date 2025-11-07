"""
Template Manager
Handles template loading, caching, and management
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages document templates with caching"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def load_template(self, state: str, doc_type: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load template for given state and document type
        
        Args:
            state: State name (e.g., 'rajasthan')
            doc_type: Document type (e.g., 'birth_certificate')
            use_cache: Whether to use cached template
            
        Returns:
            Template dictionary
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template is invalid
        """
        cache_key = f"{state}_{doc_type}"
        
        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Loading template from cache: {cache_key}")
            return self._cache[cache_key]
        
        # Load from file
        state_dir = self.templates_dir / state.lower()
        template_path = state_dir / f"{doc_type.lower().replace(' ', '_')}.json"
        
        if not template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {template_path}\n"
                f"State: {state}, Document Type: {doc_type}"
            )
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = json.load(f)
            
            # Validate template structure
            self._validate_template(template)
            
            # Cache template
            self._cache[cache_key] = template
            logger.info(f"Loaded template: {cache_key}")
            
            return template
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template file: {template_path}\nError: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading template: {str(e)}")
    
    def _validate_template(self, template: Dict[str, Any]) -> None:
        """
        Validate template structure
        
        Raises:
            ValueError: If template is invalid
        """
        required_keys = ["name", "fields"]
        
        for key in required_keys:
            if key not in template:
                raise ValueError(f"Template missing required key: {key}")
        
        if not isinstance(template["fields"], list):
            raise ValueError("Template 'fields' must be a list")
        
        # Validate each field
        for field in template["fields"]:
            if not isinstance(field, dict):
                raise ValueError("Each field must be a dictionary")
            
            if "name" not in field:
                raise ValueError("Field missing 'name' key")
    
    def get_required_fields(self, state: str, doc_type: str) -> list:
        """Get list of required field names"""
        template = self.load_template(state, doc_type)
        return [
            field["name"]
            for field in template.get("fields", [])
            if field.get("required", False)
        ]
    
    def get_field_type(self, state: str, doc_type: str, field_name: str) -> Optional[str]:
        """Get field type for validation"""
        template = self.load_template(state, doc_type)
        
        for field in template.get("fields", []):
            if field["name"] == field_name:
                return field.get("type", "text")
        
        return None
    
    def get_field_question(self, state: str, doc_type: str, field_name: str) -> str:
        """Get question prompt for field"""
        template = self.load_template(state, doc_type)
        questions = template.get("questions", {})
        
        return questions.get(
            field_name,
            f"Please provide {field_name.replace('_', ' ')}"
        )
    
    def clear_cache(self) -> None:
        """Clear template cache"""
        self._cache.clear()
        logger.info("Template cache cleared")
    
    def get_available_states(self) -> list:
        """Get list of available states"""
        if not self.templates_dir.exists():
            return []
        
        return [
            d.name for d in self.templates_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    def get_available_documents(self, state: str) -> list:
        """Get list of available document types for a state"""
        state_dir = self.templates_dir / state.lower()
        
        if not state_dir.exists():
            return []
        
        return [
            f.stem for f in state_dir.iterdir()
            if f.suffix == '.json'
        ]


# Global instance
template_manager = TemplateManager()
