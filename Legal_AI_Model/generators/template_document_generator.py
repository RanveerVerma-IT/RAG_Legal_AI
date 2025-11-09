"""
Template Document Generator Module
Fills DOCX templates with collected data and generates downloadable documents
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
import logging
import subprocess
import tempfile
import os

try:
    from docx import Document
    from docx.shared import RGBColor
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    from docx2pdf import convert
    DOCX2PDF_SUPPORT = True
except ImportError:
    DOCX2PDF_SUPPORT = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_SUPPORT = True
except ImportError:
    REPORTLAB_SUPPORT = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GeneratedDocument:
    """Represents a generated document"""
    document_bytes: bytes
    pdf_bytes: Optional[bytes]
    filename: str
    document_type: str
    generation_timestamp: datetime
    fields_filled: List[str]
    fields_skipped: List[str]


class TemplateDocumentGenerator:
    """Generates documents by filling DOCX templates with data"""
    
    # Placeholder patterns to find and replace
    PLACEHOLDER_PATTERNS = [
        r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}",  # {{field_name}}
        r"\[([a-zA-Z_][a-zA-Z0-9_]*)\]",      # [field_name]
        r"__([a-zA-Z_][a-zA-Z0-9_]*)__",      # __field_name__
        r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}",      # {field_name}
    ]
    
    def __init__(self):
        """Initialize the template document generator"""
        if not DOCX_SUPPORT:
            raise ImportError("python-docx is required for document generation")
        
        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern) for pattern in self.PLACEHOLDER_PATTERNS]
    
    def generate_document(
        self,
        template_path: Path,
        field_data: Dict[str, Any],
        skipped_fields: Optional[List[str]] = None
    ) -> GeneratedDocument:
        """
        Generate a document by filling template with data (both DOCX and PDF)
        
        Args:
            template_path: Path to template DOCX file
            field_data: Dictionary of field values
            skipped_fields: List of fields that were skipped
            
        Returns:
            GeneratedDocument object with both DOCX and PDF bytes
            
        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If document generation fails
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        skipped_fields = skipped_fields or []
        
        try:
            logger.info(f"Generating document from template: {template_path.name}")
            
            # Load template
            doc = Document(str(template_path))
            
            # Track filled fields
            fields_filled = []
            
            # Replace placeholders in paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    filled = self._replace_placeholders_in_paragraph(para, field_data)
                    fields_filled.extend(filled)
            
            # Replace placeholders in tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for para in cell.paragraphs:
                            if para.text.strip():
                                filled = self._replace_placeholders_in_paragraph(para, field_data)
                                fields_filled.extend(filled)
            
            # Replace placeholders in headers
            for section in doc.sections:
                header = section.header
                for para in header.paragraphs:
                    if para.text.strip():
                        filled = self._replace_placeholders_in_paragraph(para, field_data)
                        fields_filled.extend(filled)
            
            # Replace placeholders in footers
            for section in doc.sections:
                footer = section.footer
                for para in footer.paragraphs:
                    if para.text.strip():
                        filled = self._replace_placeholders_in_paragraph(para, field_data)
                        fields_filled.extend(filled)
            
            # Save DOCX to bytes
            doc_bytes = BytesIO()
            doc.save(doc_bytes)
            doc_bytes.seek(0)
            docx_content = doc_bytes.getvalue()
            
            # Generate PDF
            pdf_content = self._convert_to_pdf(doc, docx_content, template_path.stem, field_data)
            
            # Generate filename
            filename = self.generate_filename(
                template_path.stem,
                field_data
            )
            
            # Get document type from template name
            doc_type = self._extract_doc_type(template_path.stem)
            
            generated = GeneratedDocument(
                document_bytes=docx_content,
                pdf_bytes=pdf_content,
                filename=filename,
                document_type=doc_type,
                generation_timestamp=datetime.now(),
                fields_filled=list(set(fields_filled)),
                fields_skipped=skipped_fields
            )
            
            logger.info(
                f"Document generated successfully: {filename} "
                f"({len(fields_filled)} fields filled, {len(skipped_fields)} skipped)"
            )
            
            return generated
            
        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            raise ValueError(f"Document generation failed: {str(e)}")
    
    def _replace_placeholders_in_paragraph(
        self,
        paragraph,
        field_data: Dict[str, Any]
    ) -> List[str]:
        """
        Replace placeholders in a paragraph while preserving formatting
        
        Args:
            paragraph: python-docx Paragraph object
            field_data: Dictionary of field values
            
        Returns:
            List of field names that were filled
        """
        filled_fields = []
        
        # Get full paragraph text
        full_text = paragraph.text
        
        if not full_text:
            return filled_fields
        
        # Find all placeholders
        replacements = []
        
        for pattern in self.compiled_patterns:
            for match in pattern.finditer(full_text):
                field_name = match.group(1)
                placeholder_text = match.group(0)
                
                # Get value for this field
                value = field_data.get(field_name, "")
                
                # Format value
                formatted_value = self.format_value(value, field_name)
                
                replacements.append((placeholder_text, formatted_value, field_name))
        
        # Apply replacements
        if replacements:
            # Replace in runs to preserve formatting
            new_text = full_text
            for placeholder, value, field_name in replacements:
                new_text = new_text.replace(placeholder, value)
                if value:  # Only count as filled if value is not empty
                    filled_fields.append(field_name)
            
            # Clear existing runs and add new text
            # This is a simple approach; more complex formatting preservation
            # would require run-level manipulation
            if new_text != full_text:
                # Preserve first run's formatting
                if paragraph.runs:
                    first_run = paragraph.runs[0]
                    # Clear all runs
                    for run in paragraph.runs:
                        run.text = ""
                    # Set new text in first run
                    first_run.text = new_text
                else:
                    paragraph.text = new_text
        
        return filled_fields
    
    def format_value(self, value: Any, field_name: str) -> str:
        """
        Format a field value for display in document
        
        Args:
            value: Field value
            field_name: Name of the field
            
        Returns:
            Formatted string value
        """
        if value is None or value == "":
            return ""
        
        # Convert to string
        if isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value)
        
        return str(value)
    
    def generate_filename(
        self,
        template_name: str,
        field_data: Dict[str, Any]
    ) -> str:
        """
        Generate a descriptive filename for the document
        
        Args:
            template_name: Name of the template
            field_data: Dictionary of field values
            
        Returns:
            Generated filename
        """
        # Start with template name
        parts = [template_name]
        
        # Add primary identifier fields if available
        identifier_fields = [
            "applicant_name", "child_name", "groom_name", "bride_name",
            "name", "full_name"
        ]
        
        for field in identifier_fields:
            if field in field_data and field_data[field]:
                # Clean the name for filename
                name = str(field_data[field])
                name = re.sub(r'[^\w\s-]', '', name)
                name = re.sub(r'[\s]+', '_', name)
                parts.append(name)
                break
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parts.append(timestamp)
        
        # Join and add extension
        filename = "_".join(parts) + ".docx"
        
        return filename
    
    def _extract_doc_type(self, template_name: str) -> str:
        """
        Extract document type from template name
        
        Args:
            template_name: Template filename (without extension)
            
        Returns:
            Document type string
        """
        name_lower = template_name.lower()
        
        if "marriage" in name_lower or "wedding" in name_lower:
            return "marriage"
        elif "birth" in name_lower:
            return "birth"
        elif "death" in name_lower:
            return "death"
        elif "income" in name_lower:
            return "income"
        elif "domicile" in name_lower:
            return "domicile"
        else:
            return "document"
    
    def _convert_to_pdf(
        self,
        doc: Document,
        docx_bytes: bytes,
        template_name: str,
        field_data: Dict[str, Any]
    ) -> Optional[bytes]:
        """
        Convert DOCX to PDF - prioritizes direct conversion to maintain formatting
        
        Args:
            doc: python-docx Document object
            docx_bytes: DOCX file bytes
            template_name: Template name
            field_data: Field data for content extraction
            
        Returns:
            PDF bytes or None if conversion fails
        """
        try:
            # Method 1: Try docx2pdf (Windows only) - Best formatting preservation
            if DOCX2PDF_SUPPORT:
                logger.info("Converting to PDF using docx2pdf (preserves formatting)")
                pdf_bytes = self._convert_with_docx2pdf(docx_bytes)
                if pdf_bytes:
                    return pdf_bytes
            
            # Method 2: Try LibreOffice command line - Good formatting preservation
            logger.info("Attempting PDF conversion with LibreOffice")
            pdf_bytes = self._convert_with_libreoffice(docx_bytes)
            if pdf_bytes:
                return pdf_bytes
            
            # Method 3: Fallback to ReportLab - May lose some formatting
            if REPORTLAB_SUPPORT:
                logger.warning("Using ReportLab fallback - formatting may differ from DOCX")
                return self._create_pdf_with_reportlab(doc, template_name, field_data)
            
            return None
                
        except Exception as e:
            logger.warning(f"PDF conversion failed: {str(e)}. DOCX will still be available.")
            return None
    
    def _create_pdf_with_reportlab(
        self,
        doc: Document,
        template_name: str,
        field_data: Dict[str, Any]
    ) -> bytes:
        """
        Create PDF using ReportLab from document content
        
        Args:
            doc: python-docx Document object
            template_name: Template name
            field_data: Field data
            
        Returns:
            PDF bytes
        """
        buffer = BytesIO()
        pdf_doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(template_name.replace('_', ' ').title(), title_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Extract and add content from document
        for para in doc.paragraphs:
            if para.text.strip():
                # Determine style based on paragraph
                if para.style.name.startswith('Heading'):
                    style = styles['Heading2']
                else:
                    style = styles['Normal']
                
                # Clean text for PDF
                text = para.text.strip()
                story.append(Paragraph(text, style))
                story.append(Spacer(1, 0.1 * inch))
        
        # Add tables if any
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip())
                table_data.append(row_data)
            
            if table_data:
                pdf_table = Table(table_data)
                pdf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(pdf_table)
                story.append(Spacer(1, 0.2 * inch))
        
        # Build PDF
        pdf_doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _convert_with_docx2pdf(self, docx_bytes: bytes) -> Optional[bytes]:
        """
        Convert DOCX to PDF using docx2pdf library (Windows only)
        Preserves original DOCX formatting perfectly
        
        Args:
            docx_bytes: DOCX file bytes
            
        Returns:
            PDF bytes or None
        """
        docx_path = None
        pdf_path = None
        
        try:
            # Create temporary DOCX file
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_file:
                docx_file.write(docx_bytes)
                docx_path = docx_file.name
            
            pdf_path = docx_path.replace('.docx', '.pdf')
            
            logger.info(f"Converting DOCX to PDF: {docx_path} -> {pdf_path}")
            
            # Convert using Microsoft Word COM automation (Windows)
            convert(docx_path, pdf_path)
            
            # Check if PDF was created
            if not os.path.exists(pdf_path):
                logger.error("PDF file was not created")
                return None
            
            # Read PDF
            with open(pdf_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
            
            logger.info(f"PDF conversion successful: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"docx2pdf conversion failed: {e}")
            return None
        
        finally:
            # Cleanup temporary files
            try:
                if docx_path and os.path.exists(docx_path):
                    os.unlink(docx_path)
                if pdf_path and os.path.exists(pdf_path):
                    os.unlink(pdf_path)
            except Exception as cleanup_error:
                logger.warning(f"Cleanup error: {cleanup_error}")
    
    def _convert_with_libreoffice(self, docx_bytes: bytes) -> Optional[bytes]:
        """
        Convert DOCX to PDF using LibreOffice command line
        Works on Windows, Linux, and Mac if LibreOffice is installed
        
        Args:
            docx_bytes: DOCX file bytes
            
        Returns:
            PDF bytes or None
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save DOCX
                docx_path = os.path.join(temp_dir, 'document.docx')
                with open(docx_path, 'wb') as f:
                    f.write(docx_bytes)
                
                # Try different LibreOffice command names
                libreoffice_commands = [
                    'soffice',           # Linux/Mac
                    'libreoffice',       # Alternative
                    'C:\\Program Files\\LibreOffice\\program\\soffice.exe',  # Windows default
                    'C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe',  # Windows x86
                ]
                
                for cmd in libreoffice_commands:
                    try:
                        logger.info(f"Trying LibreOffice command: {cmd}")
                        result = subprocess.run(
                            [cmd, '--headless', '--convert-to', 'pdf', '--outdir', temp_dir, docx_path],
                            capture_output=True,
                            timeout=30,
                            shell=False
                        )
                        
                        if result.returncode == 0:
                            pdf_path = os.path.join(temp_dir, 'document.pdf')
                            if os.path.exists(pdf_path):
                                with open(pdf_path, 'rb') as f:
                                    pdf_bytes = f.read()
                                logger.info(f"LibreOffice conversion successful: {len(pdf_bytes)} bytes")
                                return pdf_bytes
                    
                    except FileNotFoundError:
                        continue
                    except Exception as e:
                        logger.debug(f"Command {cmd} failed: {e}")
                        continue
                
                logger.warning("LibreOffice not found or conversion failed")
                return None
                
        except Exception as e:
            logger.error(f"LibreOffice conversion failed: {e}")
            return None


# Global instance
template_document_generator = TemplateDocumentGenerator()
