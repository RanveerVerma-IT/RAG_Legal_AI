"""
Document Generator Factory
Provides dynamic document generation based on document type
"""
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import logging

from generators.birth_certificate import generate_birth_certificate_docx, generate_birth_certificate_pdf
from generators.marriage_certificate import generate_marriage_certificate_docx, generate_marriage_certificate_pdf


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Base class for document generators"""
    
    def __init__(self, doc_type: str, state: str):
        self.doc_type = doc_type
        self.state = state
    
    def generate(self, data: Dict[str, Any]) -> Tuple[bytes, bytes, str]:
        """
        Generate document in both DOCX and PDF formats
        
        Returns:
            (docx_content, pdf_content, file_prefix)
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate data before generation
        
        Returns:
            (is_valid, error_message)
        """
        return True, None


class BirthCertificateGenerator(DocumentGenerator):
    """Generator for birth certificates"""
    
    REQUIRED_FIELDS = [
        "child_name",
        "father_name",
        "mother_name",
        "date_of_birth",
        "place_of_birth",
        "gender",
        "address",
    ]
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate birth certificate data"""
        missing_fields = [field for field in self.REQUIRED_FIELDS if not data.get(field)]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    def generate(self, data: Dict[str, Any]) -> Tuple[bytes, bytes, str]:
        """Generate birth certificate"""
        try:
            logger.info(f"Generating birth certificate for {self.state}")
            
            # Validate data
            is_valid, error = self.validate_data(data)
            if not is_valid:
                raise ValueError(error)
            
            # Generate documents
            docx_content = generate_birth_certificate_docx(data)
            pdf_content = generate_birth_certificate_pdf(data)
            file_prefix = f"{self.state}_birth_certificate"
            
            logger.info("Birth certificate generated successfully")
            return docx_content, pdf_content, file_prefix
            
        except Exception as e:
            logger.error(f"Error generating birth certificate: {str(e)}")
            raise


class MarriageCertificateGenerator(DocumentGenerator):
    """Generator for marriage certificates"""
    
    REQUIRED_FIELDS = [
        "groom_name",
        "bride_name",
        "marriage_date",
        "marriage_place",
    ]
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate marriage certificate data"""
        missing_fields = [field for field in self.REQUIRED_FIELDS if not data.get(field)]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    def generate(self, data: Dict[str, Any]) -> Tuple[bytes, bytes, str]:
        """Generate marriage certificate"""
        try:
            logger.info(f"Generating marriage certificate for {self.state}")
            
            # Validate data
            is_valid, error = self.validate_data(data)
            if not is_valid:
                raise ValueError(error)
            
            # Generate documents
            docx_content = generate_marriage_certificate_docx(data)
            pdf_content = generate_marriage_certificate_pdf(data)
            file_prefix = f"{self.state}_marriage_certificate_application"
            
            logger.info("Marriage certificate generated successfully")
            return docx_content, pdf_content, file_prefix
            
        except Exception as e:
            logger.error(f"Error generating marriage certificate: {str(e)}")
            raise


class DocumentGeneratorFactory:
    """Factory to create appropriate document generator"""
    
    GENERATORS = {
        "birth_certificate": BirthCertificateGenerator,
        "marriage_certificate_application": MarriageCertificateGenerator,
    }
    
    DOCUMENT_NAMES = {
        "birth_certificate": "Birth Certificate",
        "marriage_certificate_application": "Marriage Certificate Application",
    }
    
    @classmethod
    def create_generator(cls, doc_type: str, state: str) -> DocumentGenerator:
        """
        Create appropriate document generator
        
        Args:
            doc_type: Type of document to generate
            state: State for which to generate document
            
        Returns:
            DocumentGenerator instance
            
        Raises:
            ValueError: If document type is not supported
        """
        generator_class = cls.GENERATORS.get(doc_type)
        
        if not generator_class:
            raise ValueError(f"Unsupported document type: {doc_type}")
        
        return generator_class(doc_type, state)
    
    @classmethod
    def get_document_name(cls, doc_type: str) -> str:
        """Get human-readable document name"""
        return cls.DOCUMENT_NAMES.get(doc_type, doc_type.replace('_', ' ').title())
    
    @classmethod
    def get_supported_documents(cls) -> list:
        """Get list of supported document types"""
        return list(cls.GENERATORS.keys())
