"""
Core Data Models
Defines all data structures used across the document processing system
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class DocumentRequest:
    """User's document generation request"""
    user_query: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessingContext:
    """Context maintained throughout the document processing pipeline"""
    request: DocumentRequest
    query_analysis: Optional[Any] = None  # QueryAnalysis
    template_path: Optional[Path] = None
    template_structure: Optional[Any] = None  # TemplateStructure
    field_comparison: Optional[Any] = None  # FieldComparison
    collected_data: Dict[str, Any] = field(default_factory=dict)
    collection_state: Optional[Any] = None  # CollectionState
    generated_document: Optional[Any] = None  # GeneratedDocument
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
