"""
Legal Assistant POC - Main Application
Streamlit-based legal document generation and query system
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys
import logging
from typing import Dict, List, Optional

from fpdf import FPDF
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import requests
from googlesearch import search
from bs4 import BeautifulSoup

from config import Config
from utils import sanitize_filename, format_date, truncate_text, logger, to_latin1_safe

# Setup
Config.ensure_dirs()
logging.basicConfig(level=logging.INFO if Config.DEBUG_MODE else logging.WARNING)

class PDFGenerator:
    """Handle PDF document generation"""
    
    @staticmethod
    def create_pdf(document_content: str, doc_type: str, details: Dict = None):
        """
        Generate PDF from document content
        Args:
            document_content: Text content to convert
            doc_type: Document type/name
            details: Optional metadata dict
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Title section
            pdf.set_font("Arial", 'B', Config.PDF_TITLE_SIZE)
            pdf.cell(200, 10, txt=doc_type, ln=1, align='C')
            pdf.ln(10)
            
            # Content (sanitize for latin-1 compatibility)
            pdf.set_font("Arial", size=Config.PDF_FONT_SIZE)
            safe_content = to_latin1_safe(document_content)
            lines = safe_content.split('\n')
            
            for line in lines:
                if not line.strip():
                    pdf.ln(3)
                    continue
                
                # Detect headings (uppercase, short lines)
                if line.strip().isupper() and len(line.strip()) < 50:
                    pdf.set_font("Arial", 'B', Config.PDF_FONT_SIZE)
                    pdf.cell(200, 10, txt=line.strip(), ln=1)
                    pdf.set_font("Arial", size=Config.PDF_FONT_SIZE)
                else:
                    pdf.multi_cell(0, 8, txt=line.strip())
                pdf.ln(2)
            
            # Footer
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 9)
            footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')} - {Config.APP_NAME}"
            pdf.cell(0, 10, footer_text, 0, 1, 'C')
            
            logger.info(f"PDF generated: {doc_type}")
            return pdf
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    @staticmethod
    def get_pdf_bytes(pdf: FPDF) -> bytes:
        """Convert PDF to bytes"""
        return pdf.output(dest='S').encode('latin1')
    
    @staticmethod
    def get_download_button(pdf: FPDF, filename: str):
        """Create Streamlit download button for PDF"""
        filename = sanitize_filename(filename)
        if not filename.endswith('.pdf'):
            filename += '.pdf'
            
        pdf_bytes = PDFGenerator.get_pdf_bytes(pdf)
        st.download_button(
            label="Download as PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )

class DOCGenerator:
    """Handle DOCX document generation"""
    
    # Colors used in docs
    TITLE_COLOR = RGBColor(0, 0, 139)
    HEADING_COLOR = RGBColor(31, 58, 96)
    FOOTER_COLOR = RGBColor(128, 128, 128)
    
    @staticmethod
    def create_docx(document_content: str, doc_type: str, details: Dict = None):
        """Generate Word doc from text content"""
        try:
            doc = Document()
            
            # Set margins (1 inch all around)
            for section in doc.sections:
                margin = Inches(1)
                section.top_margin = margin
                section.bottom_margin = margin
                section.left_margin = margin
                section.right_margin = margin
            
            # Title
            title = doc.add_heading(doc_type, 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = title.runs[0]
            title_run.font.size = Pt(18)
            title_run.font.color.rgb = DOCGenerator.TITLE_COLOR
            title_run.bold = True
            doc.add_paragraph()
            
            # Process content
            lines = document_content.split('\n')
            current_para = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_para:
                        doc.add_paragraph()
                    current_para = None
                    continue
                
                # Check for heading
                is_heading = (line.isupper() and len(line) < 50 
                             and not line.startswith((' ', '\t')))
                
                if is_heading:
                    heading = doc.add_heading(line, level=2)
                    heading_run = heading.runs[0]
                    heading_run.font.size = Pt(14)
                    heading_run.font.color.rgb = DOCGenerator.HEADING_COLOR
                    heading_run.bold = True
                    current_para = None
                else:
                    # Regular paragraph
                    if current_para is None:
                        current_para = doc.add_paragraph(line)
                    else:
                        # New para for long lines or indented
                        if len(line) > 100 or line.startswith(('  ', '\t')):
                            current_para = doc.add_paragraph(line)
                        else:
                            current_para.add_run(' ' + line)
                    
                    # Format
                    if current_para:
                        current_para.style.font.size = Pt(12)
                        for run in current_para.runs:
                            run.font.name = 'Arial'
            
            # Footer
            doc.add_paragraph()
            footer = doc.add_paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')} - {Config.APP_NAME}"
            )
            footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
            footer_run = footer.runs[0]
            footer_run.font.size = Pt(9)
            footer_run.font.color.rgb = DOCGenerator.FOOTER_COLOR
            footer_run.italic = True
            
            logger.info(f"DOCX generated: {doc_type}")
            return doc
            
        except Exception as e:
            logger.error(f"DOCX generation failed: {e}")
            raise
    
    @staticmethod
    def get_docx_bytes(doc: Document) -> bytes:
        """Get DOCX as bytes"""
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def get_download_button(doc: Document, filename: str):
        """Create download button for DOCX"""
        filename = sanitize_filename(filename)
        if not filename.endswith('.docx'):
            filename += '.docx'
            
        docx_bytes = DOCGenerator.get_docx_bytes(doc)
        st.download_button(
            label="Download as DOCX",
            data=docx_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

class GoogleSearchIntegration:
    """Google search integration for legal queries"""
    
    # Legal domain preference (not used currently but kept for future)
    LEGAL_DOMAINS = [
        'indiankanoon.org',
        'legislative.gov.in',
        'main.sci.gov.in',
        'lawcommissionofindia.nic.in',
        'nludelhi.ac.in'
    ]
    
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    @staticmethod
    def search_legal_info(query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Google and fetch page details
        Returns list of dicts with title, url, description, rank
        """
        if not Config.ENABLE_GOOGLE_SEARCH:
            logger.warning("Google search disabled in config")
            return []
            
        try:
            search_results = []
            logger.info(f"Searching: {query}")
            
            # Build search query
            search_query = f"{query} Indian law legal"
            urls = list(search(search_query, num_results=num_results, lang='en'))
            
            if not urls:
                logger.warning("No search results returned")
                return []
            
            # Fetch details for each URL
            for i, url in enumerate(urls[:num_results]):
                try:
                    title, desc = GoogleSearchIntegration._fetch_page_info(url)
                    search_results.append({
                        'title': title or f"Result {i + 1}",
                        'url': url,
                        'description': desc or f"Legal information: {query}",
                        'rank': i + 1
                    })
                except Exception as e:
                    logger.debug(f"Failed to fetch info for {url}: {e}")
                    # Still add URL even if fetch fails
                    search_results.append({
                        'title': f"Search Result {i + 1}",
                        'url': url,
                        'description': f"Click to view: {query}",
                        'rank': i + 1
                    })
            
            logger.info(f"Found {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=Config.DEBUG_MODE)
            st.error(f"Search failed: {str(e)}")
            if Config.DEBUG_MODE:
                st.exception(e)
            return []
    
    @staticmethod
    def _fetch_page_info(url: str) -> tuple:
        """Fetch title and description from URL"""
        try:
            headers = {'User-Agent': GoogleSearchIntegration.USER_AGENT}
            response = requests.get(
                url, 
                headers=headers, 
                timeout=Config.GOOGLE_SEARCH_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ""
            
            # Try meta description first, then og:description
            meta_desc = (soup.find('meta', attrs={'name': 'description'}) or 
                        soup.find('meta', attrs={'property': 'og:description'}))
            description = ""
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            
            # Fallback to first paragraph
            if not description:
                p_tag = soup.find('p')
                if p_tag:
                    description = truncate_text(p_tag.get_text().strip(), 200)
            
            return title, description
            
        except requests.RequestException as e:
            logger.debug(f"Request failed for {url}: {e}")
            return "", ""
        except Exception as e:
            logger.debug(f"Parse failed for {url}: {e}")
            return "", ""
    
    @staticmethod
    def display_search_results(results: List[Dict], query: str):
        """Render search results in Streamlit UI"""
        if not results:
            st.warning("No results found. Try different search terms.")
            return
        
        st.subheader(f"Search Results: '{query}'")
        
        for i, result in enumerate(results):
            title = truncate_text(result.get('title', 'Untitled'), 60)
            with st.expander(f"{title}", expanded=(i == 0)):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    desc = result.get('description', 'No description available')
                    st.write(f"**Description:** {desc}")
                    url = result.get('url', '#')
                    st.write(f"**URL:** [{url}]({url})")
                
                with col2:
                    st.metric("Rank", f"#{result.get('rank', i+1)}")
                    # Note: Link opening via redirect doesn't always work in Streamlit
                    if st.button("Open", key=f"link_btn_{i}"):
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', 
                                   unsafe_allow_html=True)

class LegalAssistantPOC:
    """Main application class"""
    
    def __init__(self):
        self._init_session_state()
        self.setup_page_config()
    
    def _init_session_state(self):
        """Initialize all session state variables"""
        defaults = {
            'page': 'Dashboard',
            'user_type': 'General Public',
            'search_results': [],
            'last_query': '',
            'generated_document': None,
            'generated_document_type': None,
            'generated_document_details': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=Config.APP_NAME,
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self._inject_custom_css()
    
    def _inject_custom_css(self):
        """Inject custom CSS styles"""
        css = f"""
        <style>
        .main-header {{
            font-size: 2.5rem;
            color: {Config.SECONDARY_COLOR};
            margin-bottom: 1rem;
            font-weight: bold;
        }}
        .sub-header {{
            font-size: 1.5rem;
            color: {Config.PRIMARY_COLOR};
            margin-bottom: 1rem;
        }}
        .metric-card {{
            background-color: {Config.BG_COLOR};
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid {Config.PRIMARY_COLOR};
        }}
        /* Sidebar User Type radio styling */
        div[data-testid="stSidebar"] .stRadio > label {{
            font-weight: 700;
            color: {Config.SECONDARY_COLOR};
            font-size: 1rem;
        }}
        div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
            font-weight: 700;
            font-size: 1.05rem;
        }}
        div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
            row-gap: 0.35rem;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def run(self):
        """Main run method"""
        self.render_sidebar()
        self.render_main_content()
    
    def render_sidebar(self):
        with st.sidebar:
            # Logo placeholder - using emoji as fallback
            st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1>Legal AI</h1>
                <p style="color: #666; font-size: 0.9rem;">Proof of Concept</p>
            </div>
            """, unsafe_allow_html=True)
            
            # User Type Selection (bold, clearer options)
            st.markdown("**User Type**")
            st.session_state.user_type = st.radio(
                "",
                ["General Public", "Advocate"],
                key="user_type_selector"
            )
            
            st.divider()
            
            # Navigation
            st.subheader("Navigation")
            nav_options = ["Dashboard", "Legal Query", "Document Drafting", "Case Research"]
            for option in nav_options:
                if st.button(option, key=f"nav_{option}", use_container_width=True):
                    st.session_state.page = option
                    st.rerun()
            
            st.divider()
            
            # User Info
            st.subheader("User Info")
            st.info(f"**System** User\n**Type:** {st.session_state.user_type}")
            
            st.divider()
            st.caption(f"{Config.APP_NAME} v{Config.VERSION}")
            if Config.DEBUG_MODE:
                st.caption("🔧 Debug Mode ON")
    
    def render_main_content(self):
        # Page routing
        if st.session_state.page == "Dashboard":
            self.render_dashboard()
        elif st.session_state.page == "Legal Query":
            self.render_legal_query()
        elif st.session_state.page == "Document Drafting":
            self.render_document_drafting()
        elif st.session_state.page == "Case Research":
            self.render_case_research()

    def render_dashboard(self):
        st.markdown('<div class="main-header">Legal Assistant Dashboard</div>', unsafe_allow_html=True)
        
        # User-specific welcome message
        welcome_msg = f"Welcome, {st.session_state.user_type}!"
        st.subheader(welcome_msg)
        
        # Quick Stats in cards
        st.subheader("Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Queries", "24", "+3")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Documents Generated", "12", "+2")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Success Rate", "92%", "+2%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if st.session_state.user_type == "Advocate":
                st.metric("Active Cases", "5", "+1")
            else:
                st.metric("Saved Documents", "8", "+2")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Recent Activity")
            activity_data = self.get_recent_activity()
            st.dataframe(activity_data, use_container_width=True, hide_index=True)
            
            # Quick document templates
            st.subheader("Quick Document Templates")
            template_cols = st.columns(3)
            templates = ["Affidavit", "Rental Agreement", "Legal Notice"]
            for i, template in enumerate(templates):
                with template_cols[i]:
                    if st.button(f"📝 {template}", use_container_width=True):
                        st.session_state.page = "Document Drafting"
                        st.rerun()
        
        with col2:
            st.subheader("Quick Actions")
            actions = [
                ("New Legal Query", "Legal Query"),
                ("Draft Document", "Document Drafting"),
                ("Case Research", "Case Research"),
                ("View Analytics", "Dashboard")
            ]
            
            for action_text, target_page in actions:
                if st.button(action_text, use_container_width=True):
                    st.session_state.page = target_page
                    st.rerun()
            
            st.subheader("Notifications")
            notifications = [
                ("", "New Google Search feature added", "info"),
                ("", "2 pending document reviews", "warning"),
                ("", "System updated successfully", "success")
            ]
            
            for icon, text, type in notifications:
                if type == "info":
                    st.info(text)
                elif type == "warning":
                    st.warning(text)
                else:
                    st.success(text)

    def render_legal_query(self):
        st.markdown('<div class="main-header">Legal Query Assistant</div>', unsafe_allow_html=True)
        
        st.write("Get instant legal guidance using AI responses and Google search")
        
        # Input Methods
        input_method = st.radio("Choose input method:", ["Text", "Voice"], horizontal=True)

        user_query = ""
        submitted = False

        if input_method == "Text":
            with st.form("legal_query_form", clear_on_submit=False):
                user_query = st.text_area(
                    "Enter your legal query:",
                    placeholder="e.g., How to file a consumer complaint? Or draft a rental agreement...",
                    height=100,
                    key="legal_query_input"
                )
                submitted = st.form_submit_button("Ask")
        else:
            # Voice input simulation
            st.info("Voice Input Simulation")
            if st.button("Start Recording", key="voice_btn"):
                with st.spinner("Listening... (Simulated)"):
                    # Simulate processing time
                    import time
                    time.sleep(2)
                    user_query = "I need help with drafting a rental agreement for my apartment"
                    st.success("Recording completed!")
            if user_query:
                st.text_area("Transcribed Text:", user_query, height=80, key="voice_transcription")
                submitted = True

        # Search options
        col1, col2 = st.columns(2)
        with col1:
            search_option = st.radio(
                "Search Method:",
                ["AI Response Only", "Google Search Only", "Both AI and Google"],
                horizontal=True
            )
        with col2:
            num_results = st.slider("Number of search results:", 3, 10, 5)

        # Process query only when submitted
        if submitted and user_query.strip():
            st.divider()
            
            # Store the query
            st.session_state.last_query = user_query
            
            # AI Response Section
            if search_option in ["AI Response Only", "Both AI and Google"]:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("AI Legal Assistant Response")
                    
                    # Simulate thinking
                    with st.spinner("Analyzing your query..."):
                        response = self.generate_rag_response(user_query)
                    
                    st.markdown(response)
                    
                    # Action buttons
                    st.subheader("Next Steps")
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if st.button("📄 Generate Document Draft", use_container_width=True):
                            st.session_state.document_content = response
                            st.session_state.page = "Document Drafting"
                            st.rerun()
                    
                    with action_col2:
                        if st.button("🔍 Research Similar Cases", use_container_width=True):
                            st.session_state.research_query = user_query
                            st.session_state.page = "Case Research"
                            st.rerun()
                
                with col2:
                    st.subheader("Related Resources")
                    resources = self.get_related_resources(user_query)
                    for resource in resources:
                        st.write(f"• {resource}")
                    
                    st.divider()
                    st.subheader("Quick Tips")
                    tips = [
                        "Be specific about your jurisdiction",
                        "Include all relevant details",
                        "Review generated documents carefully"
                    ]
                    for tip in tips:
                        st.write(f"• {tip}")
            
            # Google Search Section
            if search_option in ["Google Search Only", "Both AI and Google"]:
                st.divider()
                
                # Perform Google search
                search_button_key = f"search_btn_{user_query}_{num_results}"
                if st.button("Search Google for Legal Information", type="primary", key=search_button_key):
                    with st.spinner("Searching Google for legal information..."):
                        search_results = GoogleSearchIntegration.search_legal_info(user_query, num_results)
                        st.session_state.search_results = search_results
                        st.session_state.last_query = user_query
                        st.rerun()
                
                # Display search results if available
                if st.session_state.search_results:
                    # Check if results match current query
                    if st.session_state.last_query == user_query:
                        GoogleSearchIntegration.display_search_results(st.session_state.search_results, user_query)
                    else:
                        # Clear old results if query changed
                        st.session_state.search_results = []
                
                # Quick search suggestions
                st.subheader("Quick Search Suggestions")
                suggestions = [
                    "Indian Penal Code section 420",
                    "Consumer Protection Act 2019",
                    "Rental agreement laws in India", 
                    "Divorce procedure in India",
                    "Property registration process"
                ]
                
                cols = st.columns(3)
                for i, suggestion in enumerate(suggestions):
                    with cols[i % 3]:
                        if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                            st.session_state.last_query = suggestion
                            st.rerun()

    def render_document_drafting(self):
        st.markdown('<div class="main-header">Document Drafting</div>', unsafe_allow_html=True)
        
        st.write("Generate legal documents quickly and accurately")
        
        # Document type selection
        doc_type = st.selectbox(
            "Select Document Type", 
            ["Affidavit", "Rental Agreement", "Legal Notice", "Will", "Power of Attorney"]
        )
        
        # Dynamic form based on document type
        st.subheader("Document Details")
        col1, col2 = st.columns(2)
        
        with col1:
            party_a = st.text_input("Party A Name", placeholder="Full legal name")
            party_b = st.text_input("Party B Name", placeholder="Full legal name")
            effective_date = st.date_input("Effective Date", value=datetime.now())
        
        with col2:
            jurisdiction = st.text_input("Jurisdiction", "Delhi")
            consideration = st.text_input("Consideration Amount", placeholder="₹ Amount")
            duration = st.text_input("Duration", "11 months")
        
        # Additional context
        additional_info = st.text_area("Additional Context (Optional)", 
                                     placeholder="Any specific clauses or special requirements...")
        
        # Generate button
        if st.button("Generate Document", type="primary", use_container_width=True):
            details = {
                'party_a': party_a,
                'party_b': party_b,
                'effective_date': effective_date.strftime("%Y-%m-%d"),
                'jurisdiction': jurisdiction,
                'consideration': consideration,
                'duration': duration,
                'additional_info': additional_info
            }
            
            with st.spinner(f"Generating {doc_type}..."):
                document_content = self.generate_document(doc_type, details)
                
                # Store in session state
                st.session_state.generated_document = document_content
                st.session_state.generated_document_type = doc_type
                st.session_state.generated_document_details = details
                st.rerun()
        
        # Display generated document if available
        if st.session_state.generated_document:
            st.divider()
            st.subheader("📋 Generated Document")
            
            # Show document details summary
            if st.session_state.generated_document_details:
                with st.expander("Document Details", expanded=False):
                    details = st.session_state.generated_document_details
                    st.write(f"**Document Type:** {st.session_state.generated_document_type}")
                    st.write(f"**Party A:** {details.get('party_a', 'N/A')}")
                    st.write(f"**Party B:** {details.get('party_b', 'N/A')}")
                    st.write(f"**Jurisdiction:** {details.get('jurisdiction', 'N/A')}")
                    st.write(f"**Effective Date:** {details.get('effective_date', 'N/A')}")
            
            # Document preview
            st.text_area("Document Content", st.session_state.generated_document, height=300, key="document_preview")
            
            # Generate documents in all formats
            document_details = st.session_state.generated_document_details or {
                'party_a': '',
                'party_b': '',
                'jurisdiction': ''
            }
            
            pdf = PDFGenerator.create_pdf(
                st.session_state.generated_document, 
                st.session_state.generated_document_type, 
                document_details
            )
            
            docx_doc = DOCGenerator.create_docx(
                st.session_state.generated_document,
                st.session_state.generated_document_type,
                document_details
            )
            
            # File name base
            file_base = st.session_state.generated_document_type.replace(' ', '_')
            
            st.subheader("Download Options")
            st.write("Choose your preferred format:")
            
            # Create three columns for download buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**PDF Format**")
                st.markdown("Best for printing and sharing")
                PDFGenerator.get_download_button(
                    pdf, 
                    f"{file_base}.pdf"
                )
                
            with col2:
                st.markdown("**DOCX Format**")
                st.markdown("Best for editing in Microsoft Word")
                DOCGenerator.get_download_button(
                    docx_doc,
                    f"{file_base}.docx"
                )
                
            with col3:
                st.markdown("**TXT Format**")
                st.markdown("Plain text for universal compatibility")
                st.download_button(
                    "Download as TXT",
                    st.session_state.generated_document,
                    file_name=f"{file_base}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="txt_download"
                )
            
            st.divider()
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate New Document", use_container_width=True):
                    st.session_state.generated_document = None
                    st.session_state.generated_document_type = None
                    st.session_state.generated_document_details = None
                    st.rerun()
            
            with col2:
                if st.button("Copy to Clipboard", use_container_width=True):
                    st.code(st.session_state.generated_document, language=None)
                    st.success("Document content copied! (Select and copy manually)")

    def render_case_research(self):
        st.markdown('<div class="main-header">Case Research</div>', unsafe_allow_html=True)
        
        st.write("Search for relevant case laws and legal precedents")
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Search Cases", placeholder="e.g., consumer complaint, rental agreement dispute...")
        with col2:
            jurisdiction = st.selectbox("Jurisdiction", ["All", "Supreme Court", "High Court", "District Court"])
        
        if search_query:
            with st.spinner("Searching case database..."):
                cases = self.search_cases(search_query, jurisdiction)
            
            st.subheader(f"Found {len(cases)} relevant cases")
            
            for i, case in enumerate(cases):
                with st.expander(f"{case['title']} - {case['court']} ({case['year']})", expanded=i==0):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Citation:** `{case['citation']}`")
                        st.write(f"**Summary:** {case['summary']}")
                        st.write(f"**Key Points:**")
                        for point in case['key_points']:
                            st.write(f"• {point}")
                    
                    with col2:
                        st.metric("Relevance Score", f"{case['relevance']}%")
                        if st.button("View Details", key=f"details_{i}"):
                            st.text_area("Full Case Text", case['full_text'], height=200, key=f"full_text_{i}")
            
            if not cases:
                st.info("No cases found. Try different search terms or broader jurisdiction.")

    # Helper methods
    def get_recent_activity(self):
        activity_data = {
            'Date': ['2025-01-15', '2025-01-14', '2025-01-14', '2025-01-13', '2025-01-12'],
            'Activity': [
                'Google Search - Consumer Rights',
                'Affidavit Drafted - Name Change',
                'Legal Query - Rental Agreement', 
                'Case Research - Property Disputes',
                'Legal Notice Drafted'
            ],
            'Status': ['Completed', 'Completed', 'Completed', 'Completed', 'Completed'],
            'User Type': ['General Public', 'Advocate', 'Advocate', 'General Public', 'General Public']
        }
        return pd.DataFrame(activity_data)

    def generate_rag_response(self, query):
        responses = {
            "rental agreement": """**Rental Agreement Guidance**

Based on the **Transfer of Property Act, 1882** and standard rental practices:

**Essential Clauses:**
1. **Parties Information**: Complete details of landlord and tenant
2. **Property Description**: Full address and specifications  
3. **Term**: Lease duration with renewal options
4. **Rent & Deposit**: Amount, payment date, security deposit terms
5. **Maintenance**: Responsibilities division
6. **Termination**: Notice period and conditions

**Additional Recommendations:**
- Include inventory list if furnished
- Specify utility payment responsibilities
- Add dispute resolution clause

I can generate a complete rental agreement template for you. Just provide the specific details.""",

            "consumer complaint": """**Consumer Complaint Procedure**

Under **Consumer Protection Act, 2019**:

**Step-by-Step Process:**
1. **Gather Evidence**: Bills, photos, communications, warranty cards
2. **Approach Appropriate Forum**:
   - District Commission (up to ₹1 crore)
   - State Commission (₹1 crore to ₹10 crores) 
   - National Commission (above ₹10 crores)
3. **File Complaint**: With required documents and court fees
4. **Mediation**: Optional settlement process
5. **Proceedings**: Present your case with evidence

**Time Limit**: Within 2 years from cause of action
**Compensation**: Can claim for deficiency, harassment, and legal costs

Would you like me to draft a consumer complaint notice for you?""",

            "default": f"""**Legal Assistance Available**

I understand you're asking about: *"{query}"*

**I can help you with:**

📝 **Document Drafting**
- Affidavits, Agreements, Notices, Contracts
- Legal pleadings and applications

⚖️ **Legal Guidance**  
- Procedure explanations
- Rights and responsibilities
- Compliance requirements

🔍 **Case Research**
- Relevant case laws
- Legal precedents
- Statutory references

**Try the Google Search feature** for more comprehensive legal information from reliable online sources!"""
        }
        
        query_lower = query.lower()
        for key in responses:
            if key in query_lower and key != "default":
                return responses[key]
        return responses["default"]

    def get_related_resources(self, query):
        resource_map = {
            "rental": ["Transfer of Property Act, 1882", "Rent Control Act", "Standard Rental Agreement Templates"],
            "consumer": ["Consumer Protection Act, 2019", "E-commerce Rules 2020", "Sample Complaint Letters"],
            "affidavit": ["Indian Evidence Act", "Oath Act", "Affidavit Format Guidelines"],
            "default": ["Indian Constitution", "Relevant Case Laws", "Legal Procedure Guides"]
        }
        
        query_lower = query.lower()
        for key in resource_map:
            if key in query_lower:
                return resource_map[key]
        return resource_map["default"]

    def generate_document(self, doc_type, details):
        templates = {
            "Affidavit": self._generate_affidavit(details),
            "Rental Agreement": self._generate_rental_agreement(details),
            "Legal Notice": self._generate_legal_notice(details),
            "Will": self._generate_will(details),
            "Power of Attorney": self._generate_power_of_attorney(details)
        }
        return templates.get(doc_type, "Document template not available.")

    def _generate_affidavit(self, details):
        return f"""
AFFIDAVIT

I, {details.get('party_a', '[Your Full Name]')}, son/daughter of [Father's Name], resident of [Your Complete Address], do hereby solemnly affirm and declare as under:

1. That I am the deponent herein and am fully conversant with the facts of the case.
2. That I am making this affidavit in support of my [Purpose - e.g., Name Change, Address Proof, etc.].
3. That the contents of this affidavit are true and correct to the best of my knowledge and belief.
4. That nothing material has been concealed therefrom.

DEPONENT

VERIFICATION

Verified at {details.get('jurisdiction', '[City Name]')} on this {datetime.now().day} day of {datetime.now().strftime('%B')}, {datetime.now().year}.

The contents of this affidavit are true to my knowledge.

____________________
(Signature of Deponent)

ATTESTATION

Before me,
Notary Public/Oath Commissioner
{details.get('jurisdiction', '[City Name]')}
"""

    def _generate_rental_agreement(self, details):
        return f"""
RENTAL AGREEMENT

This Rental Agreement is made on {details.get('effective_date', '[Date]')} BETWEEN:

{details.get('party_a', '[Landlord Name]')}, residing at [Landlord Address] (hereinafter referred to as the "LANDLORD")

AND

{details.get('party_b', '[Tenant Name]')}, residing at [Tenant Address] (hereinafter referred to as the "TENANT")

ARTICLE 1: PREMISES
The LANDLORD agrees to let and the TENANT agrees to take the residential premises located at [Complete Property Address].

ARTICLE 2: TERM
The term of this Agreement shall be {details.get('duration', '11 months')} commencing from {details.get('effective_date', '[Start Date]')}.

ARTICLE 3: RENT
The monthly rent shall be ₹{details.get('consideration', '[Monthly Rent]')} payable in advance on or before the [Day] of each month.

ARTICLE 4: SECURITY DEPOSIT
The TENANT has deposited ₹[Security Amount] as security which shall be refunded at the time of vacation subject to deductions for any damages.

ARTICLE 5: MAINTENANCE
The LANDLORD shall be responsible for structural repairs and the TENANT for routine maintenance.

ARTICLE 6: UTILITIES
The TENANT shall be responsible for payment of all utilities including electricity, water, and gas.

ARTICLE 7: TERMINATION
Either party may terminate this Agreement by giving [Number] days' written notice to the other party.

IN WITNESS WHEREOF, the parties have executed this Agreement on the date first above written.

LANDLORD: ____________________
Name: {details.get('party_a', '[Landlord Name]')}
Witness: ____________________

TENANT: ____________________
Name: {details.get('party_b', '[Tenant Name]')}
Witness: ____________________
"""

    def _generate_legal_notice(self, details):
        return f"""
LEGAL NOTICE

Under instructions from and on behalf of my client {details.get('party_a', '[Your Name]')}, I hereby serve you with the following notice:

1. That my client is [describe relationship or context].
2. That you have [describe the grievance or issue].
3. That my client has suffered losses and damages due to your actions.
4. That despite several verbal requests, you have failed to [describe failure].

You are hereby called upon to:
1. [Specific demand 1]
2. [Specific demand 2] 
3. [Specific demand 3]
4. Cease and desist from [specific action]

Please take note that if you fail to comply with the above demands within 15 days from receipt of this notice, my client shall be constrained to initiate appropriate legal proceedings against you at your risk as to cost and consequences.

Dated: {datetime.now().strftime('%d %B, %Y')}

Yours faithfully,

____________________
[Advocate Name]
Advocate
[Bar Council Number]
[Address]
"""

    def _generate_will(self, details):
        return f"""
LAST WILL AND TESTAMENT

I, {details.get('party_a', '[Testator Name]')}, residing at [Complete Address], being of sound mind and memory, do hereby make, publish, and declare this to be my Last Will and Testament.

ARTICLE I: REVOCATION OF PRIOR WILLS
I hereby revoke all former Wills and Codicils by me made.

ARTICLE II: APPOINTMENT OF EXECUTOR
I appoint {details.get('party_b', '[Executor Name]')} as the Executor of this Will.

ARTICLE III: BEQUESTS
I give, devise, and bequeath my property as follows:

1. To [Beneficiary 1 Name]: [Description of Property or Amount]
2. To [Beneficiary 2 Name]: [Description of Property or Amount]
3. To [Beneficiary 3 Name]: [Description of Property or Amount]

ARTICLE IV: RESIDUARY ESTATE
All the rest, residue, and remainder of my estate I give to [Residuary Beneficiary Name].

IN WITNESS WHEREOF, I have hereunto set my hand this {datetime.now().day} day of {datetime.now().strftime('%B')}, {datetime.now().year}.

____________________
(Testator)

WITNESSES:

1. ____________________
   Name: [Witness 1 Name]
   Address: [Witness 1 Address]

2. ____________________
   Name: [Witness 2 Name]
   Address: [Witness 2 Address]
"""

    def _generate_power_of_attorney(self, details):
        return f"""
GENERAL POWER OF ATTORNEY

Know All Men By These Presents that I, {details.get('party_a', '[Principal Name]')}, residing at [Principal Address] (hereinafter referred to as the "Principal") do hereby appoint {details.get('party_b', '[Agent Name]')}, residing at [Agent Address] (hereinafter referred to as the "Attorney") as my true and lawful Attorney.

The Attorney is authorized to act on my behalf for the following purposes:

1. To manage my bank accounts and financial transactions
2. To deal with my properties and assets
3. To represent me before government authorities
4. To execute documents on my behalf
5. [Add specific powers as required]

This Power of Attorney shall be effective from {details.get('effective_date', '[Start Date]')} and shall remain in force until [End Date or revocation].

IN WITNESS WHEREOF, the Principal has executed this Power of Attorney on this {datetime.now().day} day of {datetime.now().strftime('%B')}, {datetime.now().year}.

____________________
(Principal)

WITNESSES:

1. ____________________
   Name: [Witness 1 Name]
   Address: [Witness 1 Address]

2. ____________________
   Name: [Witness 2 Name]
   Address: [Witness 2 Address]
"""

    def search_cases(self, query, jurisdiction):
        all_cases = [
            {
                "title": "Consumer Rights in E-commerce",
                "court": "Supreme Court of India", 
                "citation": "AIR 2020 SC 125",
                "year": "2020",
                "summary": "Landmark judgment establishing liability of e-commerce platforms under consumer protection laws.",
                "relevance": 92,
                "key_points": [
                    "E-commerce platforms are considered 'service providers'",
                    "Liable for deficiency in services",
                    "Online reviews cannot be sole basis for liability"
                ],
                "full_text": "Full text of the judgment would appear here with detailed legal reasoning and conclusions..."
            },
            {
                "title": "Rental Agreement and Tenant Rights",
                "court": "Delhi High Court",
                "citation": "2021 SCC Online Del 345", 
                "year": "2021",
                "summary": "Case clarifying tenant rights regarding security deposits and maintenance responsibilities.",
                "relevance": 85,
                "key_points": [
                    "Security deposit must be refunded within 30 days of vacation",
                    "Normal wear and tear cannot be deducted from deposit",
                    "Landlord responsible for major structural repairs"
                ],
                "full_text": "Detailed judgment text covering rental agreement disputes and legal obligations..."
            }
        ]
        
        # Filter by jurisdiction if specified
        if jurisdiction != "All":
            return [case for case in all_cases if jurisdiction in case['court']]
        
        return all_cases

if __name__ == "__main__":
    try:
        if Config.DEBUG_MODE:
            logger.info(f"Starting {Config.APP_NAME} v{Config.VERSION}")
            logger.info(f"Platform: {sys.platform}")
        
        app = LegalAssistantPOC()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        st.error("Application error. Please check logs.")
        if Config.DEBUG_MODE:
            st.exception(e)



    