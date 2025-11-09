"""
Configuration Module
Central configuration for the document processing system
"""
from pathlib import Path
import re

# Directories
DOCUMENTS_FOLDER = Path("documents")
TEMPLATES_FOLDER = Path("templates")
UPLOADS_FOLDER = Path("uploads")

# Placeholder patterns for document analysis
PLACEHOLDER_PATTERNS = [
    r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}",  # {{field_name}}
    r"\[([a-zA-Z_][a-zA-Z0-9_]*)\]",      # [field_name]
    r"__([a-zA-Z_][a-zA-Z0-9_]*)__",      # __field_name__
    r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}",      # {field_name}
]

# Field type inference keywords
FIELD_TYPE_KEYWORDS = {
    "date": ["date", "dob", "birth", "marriage", "wedding", "day", "month", "year"],
    "phone": ["phone", "mobile", "contact", "telephone", "cell"],
    "email": ["email", "mail", "e-mail"],
    "address": ["address", "residence", "location", "street", "city", "state", "pincode", "zip"],
    "text": ["name", "title", "description", "occupation", "education"],
}

# Fuzzy matching configuration
MAX_FUZZY_DISTANCE = 3
FUZZY_MATCH_THRESHOLD = 50  # Minimum score for acceptable match

# Skip keywords
SKIP_KEYWORDS = ["skip", "pass", "next", "leave blank", "leave empty", "n/a", "na"]

# Document type keywords
DOCUMENT_TYPE_KEYWORDS = {
    "marriage": ["marriage", "wedding", "nikah", "shaadi", "vivah", "matrimony"],
    "birth": ["birth", "janam", "newborn", "child"],
    "death": ["death", "demise", "mortality"],
    "income": ["income", "salary", "earning"],
    "domicile": ["domicile", "residence", "residential"],
    "caste": ["caste", "community", "category"],
}

# Location keywords
LOCATION_KEYWORDS = {
    "jaipur": ["jaipur"],
    "delhi": ["delhi", "new delhi"],
    "mumbai": ["mumbai", "bombay"],
    "bangalore": ["bangalore", "bengaluru"],
    "rajasthan": ["rajasthan"],
    "maharashtra": ["maharashtra"],
    "karnataka": ["karnataka"],
}

# Field synonyms for semantic matching
FIELD_SYNONYMS = {
    "groom": ["husband", "bridegroom", "spouse_male"],
    "bride": ["wife", "spouse_female"],
    "father": ["dad", "papa", "parent_male"],
    "mother": ["mom", "mama", "parent_female"],
    "child": ["baby", "newborn", "infant", "kid"],
    "phone": ["mobile", "contact", "telephone", "cell"],
    "email": ["mail", "e-mail", "email_address"],
    "address": ["residence", "location", "residential_address"],
    "dob": ["date_of_birth", "birth_date", "birthdate"],
}

# Question templates for data collection
QUESTION_TEMPLATES = {
    "date": "Please provide {label} (format: DD-MM-YYYY) or type 'skip' to leave blank",
    "phone": "Please provide {label} (format: +91XXXXXXXXXX) or type 'skip' to leave blank",
    "email": "Please provide {label} (format: email@example.com) or type 'skip' to leave blank",
    "address": "Please provide {label} (full address) or type 'skip' to leave blank",
    "text": "Please provide {label} or type 'skip' to leave blank",
}

# Cache settings
TEMPLATE_CACHE_TTL = 60  # seconds
TEMPLATE_ANALYSIS_CACHE_TTL = 300  # seconds

# File size limits (in bytes)
MAX_TEMPLATE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Feature flags
ENABLE_DOCX_PROCESSING = True  # Enable new DOCX-based processing
ENABLE_JSON_TEMPLATES = True  # Keep backward compatibility with JSON templates
ENABLE_FUZZY_MATCHING = True  # Enable fuzzy field name matching
ENABLE_SKIP_FUNCTIONALITY = True  # Enable field skipping

# UI Configuration
APP_TITLE = "Legal AI"
APP_ICON = "⚖️"
