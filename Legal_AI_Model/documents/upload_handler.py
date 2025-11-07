"""
Upload Handler Module
Handles file uploads in Streamlit and manages uploaded files
"""
import os
from pathlib import Path
from typing import Optional, Tuple
import streamlit as st

from documents.document_reader import read_document, extract_entities_from_document


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def handle_file_upload() -> Optional[Tuple[bytes, str, str]]:
    """
    Handle file upload via Streamlit file uploader.
    
    Returns:
        Tuple of (file_bytes, file_name, file_type) if file is uploaded, None otherwise
    """
    uploaded_file = st.file_uploader(
        "Upload a document (PDF or DOCX)",
        type=['pdf', 'docx'],
        help="Upload a birth certificate or other reference document to extract information",
        key="document_uploader"
    )
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        file_type = uploaded_file.type
        
        # Save uploaded file to uploads directory
        save_path = UPLOAD_DIR / file_name
        with open(save_path, 'wb') as f:
            f.write(file_bytes)
        
        return file_bytes, file_name, file_type
    
    return None


def process_uploaded_document(file_bytes: bytes, file_type: str) -> dict:
    """
    Process uploaded document and extract information.
    
    Args:
        file_bytes: File content as bytes
        file_type: File MIME type
        
    Returns:
        Dictionary with extracted text and entities
    """
    try:
        # Read document text
        text = read_document(file_bytes, file_type)
        
        # Extract entities
        entities = extract_entities_from_document(text)
        
        return {
            "success": True,
            "text": text,
            "entities": entities,
            "message": "Document processed successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "entities": {},
            "message": f"Error processing document: {str(e)}"
        }


def get_uploaded_files_list() -> list:
    """
    Get list of previously uploaded files.
    
    Returns:
        List of file names in uploads directory
    """
    if UPLOAD_DIR.exists():
        return [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return []


def delete_uploaded_file(filename: str) -> bool:
    """
    Delete an uploaded file.
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        True if successful, False otherwise
    """
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        try:
            file_path.unlink()
            return True
        except Exception:
            return False
    return False

