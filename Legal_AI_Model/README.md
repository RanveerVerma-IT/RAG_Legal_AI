## Legal AI Assistant (Prototype)

This prototype demonstrates a chat-like interface to generate Indian legal documents. Currently supports generating Birth Certificates and Marriage Certificate Applications for Rajasthan.

### Features
- Chat interface (Streamlit) similar to ChatGPT flow
- **Document Upload**: Upload PDF or DOCX documents to automatically extract information
- Detects intent for "Birth Certificate in Rajasthan" and "Marriage Certificate Application in Jaipur/Rajasthan"
- Extracts entities (name, DOB, email, phone, address) from user's initial message or uploaded documents
- Asks follow-up questions for missing required fields
- Generates downloadable DOCX and PDF

### Project Structure
```
main.py
requirements.txt
utils/
  parser.py
generators/
  birth_certificate.py
  marriage_certificate.py
documents/
  __init__.py
  document_reader.py      # PDF/DOCX reading and entity extraction
  upload_handler.py        # File upload handling
templates/
  rajasthan/
    birth_certificate.json
    marriage_certificate_application.json
uploads/                   # Uploaded documents (created automatically)
```

### Setup
1. Create and activate a virtual environment (recommended)
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Run
```bash
streamlit run main.py
```

Open the URL shown by Streamlit in your browser.

### Usage

**Option 1: Manual Entry**
- Start by typing commands like:
  - "Generate Birth Certificate in Rajasthan for <name>, DOB <dd-mm-yyyy>, address <...>"
  - "Generate Marriage Certificate Application in Jaipur for groom <name>, bride <name>..."
- Provide answers when prompted.
- Click the download buttons for DOCX/PDF once ready.

**Option 2: Upload Document**
- Use the sidebar to upload a PDF or DOCX document (e.g., existing birth certificate or marriage document)
- The system will automatically extract information from the document
- Provide any missing details when prompted
- Generate and download your document

### Notes
- This is a POC with simplified parsing and fixed template prompts.
- Extend by adding more templates under `templates/<state>/<document>.json` and corresponding generators.


# rag-poc
