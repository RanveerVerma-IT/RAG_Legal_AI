"""
Utility functions for Legal Assistant POC
"""
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
import re

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Clean filename - remove invalid chars"""
    # Remove invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()


def format_date(date_obj=None) -> str:
    """Format date for display"""
    if date_obj is None:
        date_obj = datetime.now()
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except:
            return date_obj
    return date_obj.strftime('%d %B, %Y')


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'


def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Safely get value from dict"""
    try:
        return dictionary.get(key, default)
    except:
        return default


def create_dir_if_not_exists(path: str):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def to_latin1_safe(text: str) -> str:
    """Convert text to Latin-1 safe string for FPDF.

    Replaces common Unicode characters with ASCII equivalents and
    removes any characters not representable in latin-1 to prevent
    encoding errors during PDF generation.
    """
    if not text:
        return ""
    replacements = {
        '₹': 'INR ',
        '’': "'",
        '‘': "'",
        '“': '"',
        '”': '"',
        '–': '-',
        '—': '-',
        '•': '*',
        '…': '...'
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    try:
        # Fast path: if encodable, return as-is
        text.encode('latin1')
        return text
    except Exception:
        # Fallback: drop unencodable characters
        return text.encode('latin1', 'ignore').decode('latin1')
