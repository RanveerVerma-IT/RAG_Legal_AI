# config.py
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

class Config:
    APP_NAME = "Legal Assistant POC"
    VERSION = "2.1.0"
    
    # Paths
    DATA_DIR = BASE_DIR / "data"
    VECTOR_DB_PATH = DATA_DIR / "vector_db"
    DOCUMENTS_PATH = DATA_DIR / "documents"
    
    # RAG settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD = 0.7
    MAX_RESULTS = 5
    
    # Search settings
    GOOGLE_SEARCH_TIMEOUT = 5
    MAX_SEARCH_RESULTS = 10
    
    # Document generation
    PDF_FONT_SIZE = 12
    PDF_TITLE_SIZE = 16
    # Note: DOCX_FONT_SIZE imported from docx.shared in main.py
    
    # UI Theme
    PRIMARY_COLOR = '#3E7BFA'
    SECONDARY_COLOR = '#1f3a60'
    BG_COLOR = '#f8f9fa'
    
    # Feature flags
    ENABLE_GOOGLE_SEARCH = True
    ENABLE_VOICE_INPUT = False  # TODO: Implement properly
    DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def ensure_dirs(cls):
        """Create required directories"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.VECTOR_DB_PATH.mkdir(exist_ok=True)
        cls.DOCUMENTS_PATH.mkdir(exist_ok=True)
