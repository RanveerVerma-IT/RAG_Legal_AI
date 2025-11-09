"""
Document Processor Module
Orchestrates the entire document processing pipeline
"""
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

from core.models import DocumentRequest, ProcessingContext
from core.exceptions import (
    DocumentProcessingError,
    TemplateNotFoundError,
    TemplateParseError,
    QueryAnalysisError,
    GenerationError
)

from utils.query_analyzer import query_analyzer
from documents.template_matcher import template_matcher
from documents.document_analyzer import document_analyzer
from utils.field_comparator import field_comparator
from utils.data_collector import data_collector, CollectionState
from generators.template_document_generator import template_document_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Orchestrates the document processing pipeline"""
    
    def __init__(self):
        """Initialize the document processor"""
        self.query_analyzer = query_analyzer
        self.template_matcher = template_matcher
        self.document_analyzer = document_analyzer
        self.field_comparator = field_comparator
        self.data_collector = data_collector
        self.document_generator = template_document_generator
    
    def process_initial_query(
        self,
        user_query: str,
        session_id: str
    ) -> ProcessingContext:
        """
        Process initial user query to start document generation
        
        Args:
            user_query: User's input query
            session_id: Session identifier
            
        Returns:
            ProcessingContext with initial analysis
            
        Raises:
            QueryAnalysisError: If query analysis fails
            TemplateNotFoundError: If no matching template found
            TemplateParseError: If template analysis fails
        """
        logger.info(f"Processing initial query for session {session_id}")
        
        # Create request
        request = DocumentRequest(
            user_query=user_query,
            session_id=session_id
        )
        
        # Create context
        context = ProcessingContext(request=request)
        
        try:
            # Step 1: Analyze query
            logger.info("Step 1: Analyzing query")
            query_analysis = self.query_analyzer.analyze_query(user_query)
            context.query_analysis = query_analysis
            
            if not query_analysis.document_type:
                raise QueryAnalysisError("Could not determine document type from query")
            
            # Step 2: Find matching template
            logger.info("Step 2: Finding matching template")
            template_path = self.template_matcher.find_template(
                query_analysis.document_type,
                query_analysis.location
            )
            
            if not template_path:
                available_types = self.template_matcher.get_available_document_types()
                raise TemplateNotFoundError(
                    f"No template found for '{query_analysis.document_type}'. "
                    f"Available types: {', '.join(available_types)}"
                )
            
            context.template_path = template_path
            
            # Step 3: Analyze template structure
            logger.info("Step 3: Analyzing template structure")
            template_structure = self.document_analyzer.analyze_template(template_path)
            context.template_structure = template_structure
            
            # Step 4: Compare extracted fields with required fields
            logger.info("Step 4: Comparing fields")
            field_comparison = self.field_comparator.compare_fields(
                template_structure.required_fields,
                query_analysis.extracted_fields
            )
            context.field_comparison = field_comparison
            
            # Store matched fields in collected data
            context.collected_data.update(field_comparison.matched_fields)
            
            # Step 5: Initialize collection state for missing fields
            if field_comparison.missing_fields:
                logger.info(f"Step 5: Initializing collection for {len(field_comparison.missing_fields)} missing fields")
                collection_state = CollectionState(
                    missing_fields=field_comparison.missing_fields,
                    current_field_index=0,
                    collected_data=context.collected_data.copy()
                )
                context.collection_state = collection_state
            else:
                logger.info("Step 5: All required fields already collected")
                context.collection_state = None
            
            logger.info("Initial query processing complete")
            return context
            
        except (QueryAnalysisError, TemplateNotFoundError, TemplateParseError) as e:
            logger.error(f"Error processing query: {str(e)}")
            context.errors.append(str(e))
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing query: {str(e)}")
            context.errors.append(f"Unexpected error: {str(e)}")
            raise DocumentProcessingError(f"Failed to process query: {str(e)}")
    
    def process_field_response(
        self,
        context: ProcessingContext,
        user_response: str,
        field_type: str = "text"
    ) -> Tuple[bool, Optional[str]]:
        """
        Process user response for a field
        
        Args:
            context: Current processing context
            user_response: User's response
            field_type: Type of the current field
            
        Returns:
            Tuple of (is_complete, next_question)
            - is_complete: True if all fields collected
            - next_question: Question for next field, or None if complete
        """
        if not context.collection_state:
            return (True, None)
        
        state = context.collection_state
        current_field = self.data_collector.get_next_field(state)
        
        if not current_field:
            return (True, None)
        
        # Check if user wants to skip
        if self.data_collector.is_skip_request(user_response):
            logger.info(f"User skipped field: {current_field}")
            self.data_collector.handle_skip(current_field, state)
            self.data_collector.advance_to_next_field(state)
        else:
            # Store the value
            state.collected_data[current_field] = user_response
            context.collected_data[current_field] = user_response
            logger.info(f"Collected value for field: {current_field}")
            self.data_collector.advance_to_next_field(state)
        
        # Check if collection is complete
        if self.data_collector.is_collection_complete(state):
            logger.info("Field collection complete")
            return (True, None)
        
        # Get next field and generate question
        next_field = self.data_collector.get_next_field(state)
        if next_field and context.template_structure:
            # Find placeholder for this field to get type and label
            placeholder = next(
                (p for p in context.template_structure.placeholders if p.field_name == next_field),
                None
            )
            
            if placeholder:
                question = self.data_collector.generate_question(
                    next_field,
                    placeholder.field_type,
                    placeholder.label
                )
            else:
                question = self.data_collector.generate_question(next_field, field_type)
            
            return (False, question)
        
        return (True, None)
    
    def generate_document(self, context: ProcessingContext) -> bytes:
        """
        Generate final document from collected data
        
        Args:
            context: Processing context with collected data
            
        Returns:
            Document bytes
            
        Raises:
            GenerationError: If document generation fails
        """
        if not context.template_path:
            raise GenerationError("No template path in context")
        
        if not context.collected_data:
            logger.warning("No data collected, generating document with empty fields")
        
        try:
            logger.info("Generating document")
            
            # Get skipped fields
            skipped_fields = []
            if context.collection_state:
                skipped_fields = context.collection_state.skipped_fields
            
            # Generate document
            generated = self.document_generator.generate_document(
                context.template_path,
                context.collected_data,
                skipped_fields
            )
            
            context.generated_document = generated
            
            logger.info(f"Document generated: {generated.filename}")
            return generated.document_bytes
            
        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            raise GenerationError(f"Failed to generate document: {str(e)}")
    
    def get_missing_fields_summary(self, context: ProcessingContext) -> Dict[str, Any]:
        """
        Get summary of missing fields
        
        Args:
            context: Processing context
            
        Returns:
            Dictionary with missing fields information
        """
        if not context.field_comparison:
            return {"missing_count": 0, "missing_fields": []}
        
        return {
            "missing_count": len(context.field_comparison.missing_fields),
            "missing_fields": context.field_comparison.missing_fields,
            "matched_count": len(context.field_comparison.matched_fields),
            "matched_fields": list(context.field_comparison.matched_fields.keys())
        }
    
    def get_first_question(self, context: ProcessingContext) -> Optional[str]:
        """
        Get the first question to ask user
        
        Args:
            context: Processing context
            
        Returns:
            First question string, or None if no fields to collect
        """
        if not context.collection_state:
            return None
        
        first_field = self.data_collector.get_next_field(context.collection_state)
        
        if not first_field:
            return None
        
        # Find placeholder for this field
        if context.template_structure:
            placeholder = next(
                (p for p in context.template_structure.placeholders if p.field_name == first_field),
                None
            )
            
            if placeholder:
                return self.data_collector.generate_question(
                    first_field,
                    placeholder.field_type,
                    placeholder.label
                )
        
        return self.data_collector.generate_question(first_field)


# Global instance
document_processor = DocumentProcessor()
