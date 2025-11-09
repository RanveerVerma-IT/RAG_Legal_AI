"""
Self-Learning System
Automatically improves from user queries and inputs
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningSystem:
    """Self-learning system that improves from user interactions"""
    
    def __init__(self, learning_data_file: str = "learning_data.json"):
        """Initialize the learning system"""
        self.learning_data_file = Path(learning_data_file)
        self.data = self._load_learning_data()
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from file"""
        if self.learning_data_file.exists():
            try:
                with open(self.learning_data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Convert regular dicts back to defaultdicts
                    return {
                        "query_patterns": defaultdict(int, loaded_data.get("query_patterns", {})),
                        "field_values": defaultdict(lambda: defaultdict(int), 
                                                    {k: defaultdict(int, v) for k, v in loaded_data.get("field_values", {}).items()}),
                        "common_errors": defaultdict(int, loaded_data.get("common_errors", {})),
                        "document_preferences": defaultdict(int, loaded_data.get("document_preferences", {})),
                        "field_skip_rates": defaultdict(int, loaded_data.get("field_skip_rates", {})),
                        "successful_completions": loaded_data.get("successful_completions", 0),
                        "total_sessions": loaded_data.get("total_sessions", 0),
                        "last_updated": loaded_data.get("last_updated", datetime.now().isoformat())
                    }
            except Exception as e:
                logger.error(f"Error loading learning data: {e}")
        
        # Initialize default structure
        return {
            "query_patterns": defaultdict(int),
            "field_values": defaultdict(lambda: defaultdict(int)),
            "common_errors": defaultdict(int),
            "document_preferences": defaultdict(int),
            "field_skip_rates": defaultdict(int),
            "successful_completions": 0,
            "total_sessions": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_learning_data(self) -> None:
        """Save learning data to file"""
        try:
            # Convert defaultdicts to regular dicts for JSON serialization
            save_data = {
                "query_patterns": dict(self.data["query_patterns"]),
                "field_values": {k: dict(v) for k, v in self.data["field_values"].items()},
                "common_errors": dict(self.data["common_errors"]),
                "document_preferences": dict(self.data["document_preferences"]),
                "field_skip_rates": dict(self.data["field_skip_rates"]),
                "successful_completions": self.data["successful_completions"],
                "total_sessions": self.data["total_sessions"],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.learning_data_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Learning data saved successfully")
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def learn_from_query(self, query: str, document_type: str) -> None:
        """Learn from user query patterns"""
        # Normalize query
        query_lower = query.lower().strip()
        
        # Track query patterns
        self.data["query_patterns"][query_lower] += 1
        
        # Track document preferences
        if document_type:
            self.data["document_preferences"][document_type] += 1
        
        self._save_learning_data()
    
    def learn_from_field_input(self, field_name: str, field_value: str, field_type: str) -> None:
        """Learn from user field inputs"""
        # Track common field values (for suggestions)
        if field_type in ["text", "name"]:
            # Store normalized value
            normalized_value = field_value.strip().title()
            self.data["field_values"][field_name][normalized_value] += 1
        
        self._save_learning_data()
    
    def learn_from_error(self, field_name: str, error_type: str) -> None:
        """Learn from validation errors"""
        error_key = f"{field_name}:{error_type}"
        self.data["common_errors"][error_key] += 1
        
        self._save_learning_data()
    
    def learn_from_skip(self, field_name: str) -> None:
        """Learn from field skips"""
        self.data["field_skip_rates"][field_name] += 1
        
        self._save_learning_data()
    
    def learn_from_completion(self, success: bool) -> None:
        """Learn from document completion"""
        self.data["total_sessions"] += 1
        if success:
            self.data["successful_completions"] += 1
        
        self._save_learning_data()
    
    def get_field_suggestions(self, field_name: str, limit: int = 3) -> List[str]:
        """Get suggestions for a field based on past inputs"""
        if field_name in self.data["field_values"]:
            # Sort by frequency
            sorted_values = sorted(
                self.data["field_values"][field_name].items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [value for value, count in sorted_values[:limit]]
        return []
    
    def get_popular_documents(self, limit: int = 5) -> List[tuple]:
        """Get most popular document types"""
        sorted_docs = sorted(
            self.data["document_preferences"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_docs[:limit]
    
    def get_problematic_fields(self, limit: int = 5) -> List[tuple]:
        """Get fields with most errors"""
        sorted_errors = sorted(
            self.data["common_errors"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_errors[:limit]
    
    def get_frequently_skipped_fields(self, limit: int = 5) -> List[tuple]:
        """Get most frequently skipped fields"""
        sorted_skips = sorted(
            self.data["field_skip_rates"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_skips[:limit]
    
    def get_success_rate(self) -> float:
        """Get overall success rate"""
        if self.data["total_sessions"] == 0:
            return 0.0
        return self.data["successful_completions"] / self.data["total_sessions"]
    
    def get_insights(self) -> Dict[str, Any]:
        """Get learning insights"""
        return {
            "total_sessions": self.data["total_sessions"],
            "successful_completions": self.data["successful_completions"],
            "success_rate": self.get_success_rate(),
            "popular_documents": self.get_popular_documents(),
            "problematic_fields": self.get_problematic_fields(),
            "frequently_skipped": self.get_frequently_skipped_fields(),
        }
    
    def should_make_field_optional(self, field_name: str, threshold: float = 0.7) -> bool:
        """Determine if a field should be made optional based on skip rate"""
        total_sessions = self.data["total_sessions"]
        if total_sessions < 10:  # Need minimum data
            return False
        
        skip_count = self.data["field_skip_rates"].get(field_name, 0)
        skip_rate = skip_count / total_sessions
        
        return skip_rate >= threshold
    
    def get_improved_question(self, field_name: str, original_question: str) -> str:
        """Get improved question based on learning"""
        # Check if field has high error rate
        error_count = sum(
            count for key, count in self.data["common_errors"].items()
            if key.startswith(f"{field_name}:")
        )
        
        if error_count > 5:
            # Add extra help for problematic fields
            return f"{original_question}\n\n⚠️ **Tip**: This field often has errors. Please double-check your input."
        
        # Check if field has suggestions
        suggestions = self.get_field_suggestions(field_name, limit=2)
        if suggestions:
            suggestions_text = ", ".join(suggestions)
            return f"{original_question}\n\n💡 **Common values**: {suggestions_text}"
        
        return original_question


# Global instance
learning_system = LearningSystem()
