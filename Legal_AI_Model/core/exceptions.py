"""
Custom Exceptions for Document Processing
"""


class DocumentProcessingError(Exception):
    """Base exception for document processing"""
    pass


class TemplateNotFoundError(DocumentProcessingError):
    """Template matching failed"""
    pass


class TemplateParseError(DocumentProcessingError):
    """Template analysis failed"""
    pass


class ValidationError(DocumentProcessingError):
    """Field validation failed"""
    pass


class GenerationError(DocumentProcessingError):
    """Document generation failed"""
    pass


class QueryAnalysisError(DocumentProcessingError):
    """Query analysis failed"""
    pass
