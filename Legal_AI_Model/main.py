import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime

import streamlit as st

from utils.entity_extractor import entity_extractor
from utils.validators import FieldValidatorFactory
from utils.template_manager import template_manager
from utils.intent_detector import intent_detector
from generators.document_factory import DocumentGeneratorFactory

# New backend imports
from core.document_processor import document_processor
from core.exceptions import (
    TemplateNotFoundError,
    TemplateParseError,
    QueryAnalysisError,
    GenerationError
)
from core.learning_system import learning_system
from config import ENABLE_DOCX_PROCESSING

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


APP_TITLE = "Legal AI"
TEMPLATES_DIR = Path("templates")


def _get_friendly_document_name(template_name: str) -> str:
    """Convert template filename to friendly document name"""
    # Remove common suffixes
    name = template_name.replace('_Form', '').replace('_Application', '').replace('_Certificate', '')
    
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    
    # Add proper document type suffix
    if 'marriage' in name.lower():
        return "Marriage Registration Certificate"
    elif 'birth' in name.lower():
        return "Birth Certificate"
    elif 'death' in name.lower():
        return "Death Certificate"
    elif 'income' in name.lower():
        return "Income Certificate"
    elif 'domicile' in name.lower():
        return "Domicile Certificate"
    else:
        return name.title()


def load_template(state: str, doc_type: str) -> Dict[str, Any]:
    """Load template using template manager"""
    try:
        return template_manager.load_template(state, doc_type)
    except Exception as e:
        logger.error(f"Error loading template: {str(e)}")
        raise


def initialize_session_state() -> None:
    defaults = {
        "messages": [],
        "awaiting_fields": [],
        "collected_data": {},
        "current_template": None,
        "current_state": None,
        "current_doc_type": None,
        "extracted_entities": {},
        "display_messages": [],
        # New backend state
        "processing_context": None,
        "use_new_backend": ENABLE_DOCX_PROCESSING,
        "session_id": str(uuid.uuid4()),
        # Chat history management
        "chat_history": [],  # List of all chat sessions
        "current_chat_id": None,
        "chat_title": "New Chat",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Load chat history from file if exists
    if "chat_history" in st.session_state and not st.session_state.chat_history:
        load_chat_history()


def save_current_chat() -> None:
    """Save current chat to history before starting new one"""
    if st.session_state.display_messages and len(st.session_state.display_messages) > 0:
        # Generate chat title from first user message
        first_user_msg = next(
            (msg["content"] for msg in st.session_state.display_messages if msg["role"] == "user"),
            "New Chat"
        )
        chat_title = first_user_msg[:50] + "..." if len(first_user_msg) > 50 else first_user_msg
        
        # Create chat session object
        chat_session = {
            "id": st.session_state.current_chat_id or str(uuid.uuid4()),
            "title": chat_title,
            "messages": st.session_state.display_messages.copy(),
            "timestamp": datetime.now().isoformat(),
            "session_data": {
                "collected_data": st.session_state.collected_data.copy(),
                "current_doc_type": st.session_state.current_doc_type,
                "current_state": st.session_state.current_state,
            }
        }
        
        # Check if chat already exists (update) or new (append)
        existing_index = next(
            (i for i, chat in enumerate(st.session_state.chat_history) 
             if chat["id"] == chat_session["id"]),
            None
        )
        
        if existing_index is not None:
            st.session_state.chat_history[existing_index] = chat_session
        else:
            st.session_state.chat_history.insert(0, chat_session)
        
        # Keep only last 50 chats
        st.session_state.chat_history = st.session_state.chat_history[:50]
        
        # Save to file
        save_chat_history()


def load_chat_session(chat_id: str) -> None:
    """Load a specific chat session"""
    chat = next((c for c in st.session_state.chat_history if c["id"] == chat_id), None)
    
    if chat:
        st.session_state.current_chat_id = chat_id
        st.session_state.display_messages = chat["messages"].copy()
        st.session_state.messages = chat["messages"].copy()
        st.session_state.chat_title = chat["title"]
        
        # Restore session data
        if "session_data" in chat:
            st.session_state.collected_data = chat["session_data"].get("collected_data", {})
            st.session_state.current_doc_type = chat["session_data"].get("current_doc_type")
            st.session_state.current_state = chat["session_data"].get("current_state")


def reset_conversation() -> None:
    """Start a new chat and save current one to history"""
    # Save current chat to history
    save_current_chat()
    
    # Reset all conversation state
    keys_to_reset = [
        "messages", "awaiting_fields", "collected_data", "current_template",
        "current_state", "current_doc_type", "extracted_entities", "display_messages",
        "processing_context"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            st.session_state[key] = [] if key.endswith('s') else None
    st.session_state.collected_data = {}
    st.session_state.extracted_entities = {}
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chat_title = "New Chat"
    
    # Clear generated documents
    if hasattr(st.session_state, "generated_docx"):
        delattr(st.session_state, "generated_docx")
    if hasattr(st.session_state, "generated_pdf"):
        delattr(st.session_state, "generated_pdf")
    if hasattr(st.session_state, "generated_file_prefix"):
        delattr(st.session_state, "generated_file_prefix")


def save_chat_history() -> None:
    """Save chat history to file"""
    try:
        history_file = Path("chat_history.json")
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(st.session_state.chat_history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")


def load_chat_history() -> None:
    """Load chat history from file"""
    try:
        history_file = Path("chat_history.json")
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                st.session_state.chat_history = json.load(f)
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        st.session_state.chat_history = []


def add_system_message(content: str) -> None:
    st.session_state.messages.append({"role": "assistant", "content": content})
    st.session_state.display_messages.append({"role": "assistant", "content": content})


def add_user_message(content: str) -> None:
    st.session_state.messages.append({"role": "user", "content": content})
    st.session_state.display_messages.append({"role": "user", "content": content})


def detect_document_intent(user_input: str) -> tuple[Optional[str], str]:
    """Detect document type and state using intent detector"""
    return intent_detector.detect_intent(user_input)


def initialize_document_generation_new_backend(user_input: str) -> None:
    """Initialize document generation using new DOCX-based backend"""
    try:
        # Process initial query
        context = document_processor.process_initial_query(
            user_input,
            st.session_state.session_id
        )
        
        st.session_state.processing_context = context
        
        # Learn from query (non-blocking)
        try:
            doc_type = context.query_analysis.document_type if context.query_analysis else None
            if doc_type:
                learning_system.learn_from_query(user_input, doc_type)
        except Exception as learn_error:
            logger.warning(f"Learning system error (non-critical): {learn_error}")
        
        # Get summary of what was found
        summary = document_processor.get_missing_fields_summary(context)
        
        # Build response message with better formatting
        if context.template_path:
            doc_type_name = _get_friendly_document_name(context.template_path.stem)
        else:
            doc_type_name = "document"
        
        # Start with a friendly greeting
        message_parts = [f"Great! I'll help you create your **{doc_type_name}**."]
        
        # Show what we already have (if any)
        if summary["matched_count"] > 0:
            message_parts.append(f"\n✅ I've captured {summary['matched_count']} detail(s) from your request.")
        
        # Ask for missing information without showing count
        if summary["missing_count"] > 0:
            # Get first question
            first_question = document_processor.get_first_question(context)
            if first_question:
                message_parts.append(f"\n{first_question}")
        else:
            message_parts.append("\n\n✨ All information collected! Generating your document...")
            # Generate document immediately
            generate_document_new_backend()
        
        add_system_message("\n".join(message_parts))
        
    except TemplateNotFoundError as e:
        logger.error(f"Template not found: {str(e)}")
        add_system_message(str(e))
    except (QueryAnalysisError, TemplateParseError) as e:
        logger.error(f"Error initializing: {str(e)}")
        add_system_message(f"Error: {str(e)}")
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        add_system_message(f"An unexpected error occurred. Please try again or contact support.")


def initialize_document_generation(doc_type: str, state: str, user_input: str) -> None:
    """Initialize document generation with enhanced entity extraction"""
    st.session_state.current_state = state
    st.session_state.current_doc_type = doc_type
    
    try:
        template = load_template(state, doc_type)
        st.session_state.current_template = template
        
        required_fields = template_manager.get_required_fields(state, doc_type)
        
        # Extract entities using enhanced extractor
        parsed_entities = entity_extractor.extract_entities(user_input)
        collected_data = st.session_state.collected_data.copy()
        
        if st.session_state.extracted_entities:
            collected_data.update(st.session_state.extracted_entities)
        
        # Validate and format extracted entities
        for field in required_fields:
            if field in parsed_entities and parsed_entities[field]:
                field_type = template_manager.get_field_type(state, doc_type, field)
                if field_type:
                    is_valid, error, formatted_value = FieldValidatorFactory.validate_and_format(
                        field_type, parsed_entities[field]
                    )
                    if is_valid:
                        collected_data[field] = formatted_value
                    else:
                        logger.warning(f"Validation failed for {field}: {error}")
                else:
                    collected_data[field] = parsed_entities[field]
        
        missing_fields = [
            field for field in required_fields 
            if field not in collected_data or not collected_data.get(field)
        ]
        
        st.session_state.collected_data = collected_data
        st.session_state.awaiting_fields = missing_fields
        
        if missing_fields:
            first_field = missing_fields[0]
            prompt = template_manager.get_field_question(state, doc_type, first_field)
            doc_name = DocumentGeneratorFactory.get_document_name(doc_type)
            message = f"I will help you generate a {doc_name} for {state.title()}.\n\n{prompt}"
            add_system_message(message)
        else:
            message = "All required information collected. Generating your document now."
            add_system_message(message)
            generate_document()
            
    except FileNotFoundError as e:
        logger.error(f"Template not found: {str(e)}")
        add_system_message(f"Error: Template not found for {doc_type} in {state}")
    except Exception as e:
        logger.error(f"Error initializing document generation: {str(e)}")
        add_system_message(f"An error occurred: {str(e)}")


def process_field_response_new_backend(user_input: str) -> None:
    """Process user response using new backend with skip functionality"""
    context = st.session_state.processing_context
    
    if not context or not context.collection_state:
        return
    
    try:
        # Get current field before processing
        from utils.data_collector import data_collector
        current_field = data_collector.get_next_field(context.collection_state)
        
        # Check if skip
        is_skip = data_collector.is_skip_request(user_input)
        
        # Process the response
        is_complete, next_question = document_processor.process_field_response(
            context,
            user_input,
            "text"  # Default type, will be determined from template
        )
        
        # Learn from interaction (non-blocking)
        try:
            if current_field:
                if is_skip:
                    learning_system.learn_from_skip(current_field)
                else:
                    # Get field type
                    placeholder = next(
                        (p for p in context.template_structure.placeholders if p.field_name == current_field),
                        None
                    )
                    field_type = placeholder.field_type if placeholder else "text"
                    learning_system.learn_from_field_input(current_field, user_input, field_type)
        except Exception as learn_error:
            logger.warning(f"Learning system error (non-critical): {learn_error}")
        
        if is_complete:
            # All fields collected, generate document
            add_system_message("\n✨ All information collected! Generating your document...")
            generate_document_new_backend()
            # Learn from successful completion (non-blocking)
            try:
                learning_system.learn_from_completion(True)
            except Exception as learn_error:
                logger.warning(f"Learning system error (non-critical): {learn_error}")
        else:
            # Ask next question (with learning improvements)
            if next_question:
                # Get improved question if available (non-blocking)
                try:
                    next_field = data_collector.get_next_field(context.collection_state)
                    if next_field:
                        next_question = learning_system.get_improved_question(next_field, next_question)
                except Exception as learn_error:
                    logger.warning(f"Learning system error (non-critical): {learn_error}")
                add_system_message(next_question)
    
    except Exception as e:
        logger.error(f"Error processing field response: {str(e)}")
        add_system_message(f"Error processing your response: {str(e)}")
        # Learn from error (non-blocking)
        try:
            if current_field:
                learning_system.learn_from_error(current_field, "processing_error")
        except Exception as learn_error:
            logger.warning(f"Learning system error (non-critical): {learn_error}")


def process_field_response(user_input: str) -> None:
    """Process user response for field with validation and skip support"""
    if not st.session_state.awaiting_fields:
        return
    
    current_field = st.session_state.awaiting_fields[0]
    field_value = user_input.strip()
    
    # Check if user wants to skip (empty input or skip keyword)
    from utils.data_collector import data_collector
    if data_collector.is_skip_request(user_input):
        # Skip this field
        st.session_state.awaiting_fields = st.session_state.awaiting_fields[1:]
        
        if st.session_state.awaiting_fields:
            next_field = st.session_state.awaiting_fields[0]
            prompt = template_manager.get_field_question(
                st.session_state.current_state,
                st.session_state.current_doc_type,
                next_field
            )
            message = f"⏭️ Skipped {current_field.replace('_', ' ')}.\n\n{prompt}"
            add_system_message(message)
        else:
            message = "✨ All fields processed. Generating your document..."
            add_system_message(message)
            generate_document()
        return
    
    if field_value:
        # Get field type and validate
        state = st.session_state.current_state
        doc_type = st.session_state.current_doc_type
        field_type = template_manager.get_field_type(state, doc_type, current_field)
        
        if field_type:
            is_valid, error, formatted_value = FieldValidatorFactory.validate_and_format(
                field_type, field_value
            )
            
            if not is_valid:
                # Validation failed, ask again
                message = f"{error}\n\nPlease try again or press Enter to skip."
                add_system_message(message)
                return
            
            field_value = formatted_value
        
        # Store validated value
        st.session_state.collected_data[current_field] = field_value
        st.session_state.awaiting_fields = st.session_state.awaiting_fields[1:]
        
        if st.session_state.awaiting_fields:
            next_field = st.session_state.awaiting_fields[0]
            prompt = template_manager.get_field_question(state, doc_type, next_field)
            message = f"✅ Recorded.\n\n{prompt}"
            add_system_message(message)
        else:
            message = "✨ All information collected! Generating your document..."
            add_system_message(message)
            generate_document()


def validate_generation_requirements() -> Optional[str]:
    if not st.session_state.current_template:
        return "No template selected"
    
    required_fields = [
        field["name"] for field in st.session_state.current_template.get("fields", [])
        if field.get("required", False)
    ]
    
    missing_fields = [
        field for field in required_fields
        if field not in st.session_state.collected_data or not st.session_state.collected_data.get(field)
    ]
    
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    
    return None


def generate_document_new_backend() -> None:
    """Generate document using new DOCX-based backend (both DOCX and PDF)"""
    context = st.session_state.processing_context
    
    if not context:
        add_system_message("Error: No processing context available")
        return
    
    try:
        # Generate document
        doc_bytes = document_processor.generate_document(context)
        
        # Store for download
        st.session_state.generated_docx = doc_bytes
        
        # Generate filename and store PDF if available
        if context.generated_document:
            filename = context.generated_document.filename
            st.session_state.generated_file_prefix = filename.replace('.docx', '')
            
            # Store PDF if generated
            if context.generated_document.pdf_bytes:
                st.session_state.generated_pdf = context.generated_document.pdf_bytes
                logger.info("PDF version also generated")
            else:
                logger.warning("PDF generation failed, only DOCX available")
            
            # Show summary
            filled_count = len(context.generated_document.fields_filled)
            skipped_count = len(context.generated_document.fields_skipped)
            
            message = f"Your document is ready! ({filled_count} fields filled"
            if skipped_count > 0:
                message += f", {skipped_count} skipped"
            message += "). Download using the buttons below."
            
            add_system_message(message)
            logger.info(f"Document generated: {filename}")
        else:
            add_system_message("Your document is ready. Download using the buttons below.")
    
    except GenerationError as e:
        logger.error(f"Generation error: {str(e)}")
        add_system_message(f"Error generating document: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating document: {str(e)}")
        add_system_message(f"An unexpected error occurred: {str(e)}")


def generate_document() -> None:
    """Generate document using factory pattern"""
    validation_error = validate_generation_requirements()
    if validation_error:
        add_system_message(validation_error)
        return
    
    data = st.session_state.collected_data
    doc_type = st.session_state.current_doc_type
    state = st.session_state.current_state
    
    try:
        # Create generator using factory
        generator = DocumentGeneratorFactory.create_generator(doc_type, state)
        
        # Generate documents
        docx_content, pdf_content, file_prefix = generator.generate(data)
        
        # Store generated documents
        st.session_state.generated_docx = docx_content
        st.session_state.generated_pdf = pdf_content
        st.session_state.generated_file_prefix = file_prefix
        
        # Get document name
        document_name = DocumentGeneratorFactory.get_document_name(doc_type)
        
        add_system_message(f"Your {document_name} is ready. Download using the buttons below.")
        logger.info(f"Document generated successfully: {document_name}")
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        add_system_message(f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Document generation failed: {str(e)}")
        add_system_message(f"Document generation failed: {str(e)}")


def apply_custom_styles() -> None:
    st.markdown("""
        <style>
        .main .block-container {
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main content area - lighter background */
        .main {
            background-color: #1a1a1a !important;
        }
        
        .main .block-container {
            background-color: #1a1a1a !important;
        }
        
        /* ChatGPT-style sidebar - darker background */
        section[data-testid="stSidebar"] {
            background-color: #0d0d0d !important;
            border-right: 1px solid #2a2a2a !important;
        }
        
        section[data-testid="stSidebar"] > div {
            background-color: #0d0d0d !important;
            padding-top: 2rem !important;
        }
        
        section[data-testid="stSidebar"]::after {
            content: '';
            position: absolute;
            right: 0;
            top: 0;
            bottom: 0;
            width: 1px;
            background: linear-gradient(180deg, 
                transparent 0%, 
                #3a3a3a 20%, 
                #3a3a3a 80%, 
                transparent 100%);
        }
        
        /* Sidebar buttons */
        .stButton > button {
            background-color: transparent !important;
            border: 1px solid #3a3a3a !important;
            border-radius: 8px !important;
            color: #e0e0e0 !important;
            font-weight: 500 !important;
            padding: 10px 16px !important;
            transition: all 0.2s !important;
        }
        
        .stButton > button:hover {
            background-color: #1a1a1a !important;
            border-color: #4a4a4a !important;
        }
        
        /* Apple-style gradient border chat input */
        .stChatInputContainer {
            padding: 0 !important;
            max-width: 900px !important;
            margin: 0 auto !important;
        }
        
        .stChatInput {
            position: relative !important;
            padding: 3px !important;
            background: linear-gradient(90deg, 
                #ff3b30 0%, 
                #ff9500 15%, 
                #ffcc00 30%, 
                #34c759 45%, 
                #00c7be 60%, 
                #007aff 75%, 
                #5856d6 90%, 
                #af52de 100%) !important;
            border-radius: 50px !important;
            overflow: hidden !important;
        }
        
        .stChatInput > div {
            background-color: #1c1c1e !important;
            border-radius: 47px !important;
            border: none !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }
        
        .stChatInput > div > div {
            background-color: transparent !important;
            border: none !important;
            padding: 16px 24px !important;
            flex: 1 !important;
        }
        
        .stChatInput input {
            background-color: transparent !important;
            border: none !important;
            color: #ffffff !important;
            font-size: 16px !important;
            padding: 0 !important;
            width: 100% !important;
        }
        
        .stChatInput input::placeholder {
            color: #8e8e93 !important;
            font-size: 16px !important;
        }
        
        .stChatInput input:focus {
            outline: none !important;
            box-shadow: none !important;
        }
        
        .stChatInput button {
            background-color: transparent !important;
            border: none !important;
            color: #007aff !important;
            padding: 8px 16px !important;
            margin: 0 !important;
            flex-shrink: 0 !important;
        }
        
        .stChatInput button:hover {
            background-color: rgba(0, 122, 255, 0.1) !important;
            border-radius: 50% !important;
        }
        
        .stChatInput form {
            width: 100% !important;
        }
        
        .stDownloadButton > button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        # New Chat Button
        st.markdown("""
            <style>
            .sidebar-button {
                background-color: transparent;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px 16px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                width: 100%;
                text-align: left;
                margin-bottom: 16px;
                transition: background-color 0.2s;
            }
            .sidebar-button:hover {
                background-color: #2a2a2a;
            }
            .sidebar-section-title {
                color: #8e8e93;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 24px 0 12px 0;
                padding: 0 8px;
            }
            .chat-item {
                background-color: transparent;
                border-radius: 8px;
                padding: 10px 12px;
                margin: 4px 0;
                color: #e0e0e0;
                font-size: 13px;
                cursor: pointer;
                transition: background-color 0.2s;
                border: 1px solid transparent;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                text-align: left;
            }
            .chat-item:hover {
                background-color: #2a2a2a;
                border-color: #3a3a3a;
            }
            .chat-item-active {
                background-color: #2a2a2a;
                border-color: #4a4a4a;
            }
            .quick-action-btn {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 13px;
                margin: 4px 0;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .quick-action-btn:hover {
                background-color: #2a2a2a;
                border-color: #4a4a4a;
            }
            .chat-timestamp {
                color: #6e6e73;
                font-size: 11px;
                margin-top: 2px;
            }
            /* Keep chat history buttons in single line */
            .stButton > button {
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                text-align: left !important;
                height: 38px !important;
                padding: 8px 12px !important;
                display: flex !important;
                justify-content: flex-start !important;
                align-items: center !important;
            }
            .stButton > button p {
                text-align: left !important;
                margin: 0 !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("➕ New chat", use_container_width=True, key="new_chat"):
            reset_conversation()
            st.rerun()
        
        # Quick Actions Section
        st.markdown('<div class="sidebar-section-title">Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("Marriage Certificate", use_container_width=True, key="quick_marriage"):
            reset_conversation()  # Start fresh chat
            add_user_message("Generate marriage certificate")
            detect_intent_and_bootstrap("Generate marriage certificate")
            st.rerun()
        
        if st.button("Birth Certificate", use_container_width=True, key="quick_birth"):
            reset_conversation()  # Start fresh chat
            add_user_message("Generate birth certificate")
            detect_intent_and_bootstrap("Generate birth certificate")
            st.rerun()
        
        # Chat History Section
        st.markdown('<div class="sidebar-section-title">Chat History</div>', unsafe_allow_html=True)
        
        if st.session_state.chat_history:
            # Show recent chats (last 20)
            for chat in st.session_state.chat_history[:20]:
                chat_id = chat["id"]
                title = chat["title"]
                timestamp = chat.get("timestamp", "")
                
                # Format timestamp
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%b %d, %I:%M %p")
                except:
                    time_str = ""
                
                # Check if this is the current chat
                is_active = chat_id == st.session_state.current_chat_id
                active_class = "chat-item-active" if is_active else ""
                
                # Create unique key for button
                button_key = f"chat_{chat_id}"
                
                # Display chat item
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(
                        f"{title}",
                        key=button_key,
                        use_container_width=True,
                        disabled=is_active
                    ):
                        load_chat_session(chat_id)
                        st.rerun()
                
                with col2:
                    # Delete button
                    if st.button("❌", key=f"del_{chat_id}", help="Delete chat"):
                        st.session_state.chat_history = [
                            c for c in st.session_state.chat_history if c["id"] != chat_id
                        ]
                        save_chat_history()
                        if is_active:
                            reset_conversation()
                        st.rerun()
                
                if time_str:
                    st.markdown(
                        f'<div class="chat-timestamp" style="padding-left: 12px;">{time_str}</div>',
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                '<div style="color: #6e6e73; font-size: 13px; padding: 12px 8px; text-align: center;">'
                'No chat history yet<br/>Start a conversation!</div>',
                unsafe_allow_html=True
            )


def render_main_chat() -> None:
    for message in st.session_state.display_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    if not st.session_state.display_messages:
        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; color: #888; font-size: 14px;'>
            Start by requesting a document like "Generate marriage certificate" or "Create birth certificate"
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)


def render_download_section() -> None:
    if hasattr(st.session_state, "generated_docx") or hasattr(st.session_state, "generated_pdf"):
        st.subheader("Download Document")
        col1, col2 = st.columns(2)
        file_prefix = getattr(st.session_state, "generated_file_prefix", "document")
        
        if hasattr(st.session_state, "generated_docx"):
            with col1:
                st.download_button(
                    label="Download DOCX",
                    data=st.session_state.generated_docx,
                    file_name=f"{file_prefix}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
        
        if hasattr(st.session_state, "generated_pdf"):
            with col2:
                st.download_button(
                    label="Download PDF",
                    data=st.session_state.generated_pdf,
                    file_name=f"{file_prefix}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )


def detect_intent_and_bootstrap(user_input: str) -> None:
    # Use new backend if enabled
    if st.session_state.use_new_backend:
        try:
            initialize_document_generation_new_backend(user_input)
        except Exception as e:
            logger.error(f"New backend failed, falling back to old: {str(e)}")
            # Fallback to old backend
            doc_type, state = detect_document_intent(user_input)
            if doc_type:
                initialize_document_generation(doc_type, state, user_input)
            else:
                add_system_message(
                    "I can help you generate legal documents. Available documents:\n\n"
                    "• Marriage Certificate Application\n"
                    "• Birth Certificate\n\n"
                    "Try: 'Generate marriage certificate' or 'Create birth certificate'"
                )
    else:
        # Use old backend
        doc_type, state = detect_document_intent(user_input)
        
        if doc_type:
            initialize_document_generation(doc_type, state, user_input)
        else:
            add_system_message(
                "I can help you generate legal documents. Available documents:\n\n"
                "• Marriage Certificate Application\n"
                "• Birth Certificate\n\n"
                "Try: 'Generate marriage certificate' or 'Create birth certificate'"
            )


def handle_user_input(user_input: str) -> None:
    add_user_message(user_input)
    
    # Set current chat ID if not set
    if not st.session_state.current_chat_id:
        st.session_state.current_chat_id = str(uuid.uuid4())
    
    # Use new backend if enabled and context exists
    if st.session_state.use_new_backend and st.session_state.processing_context:
        process_field_response_new_backend(user_input)
    elif st.session_state.current_template is None:
        detect_intent_and_bootstrap(user_input)
    else:
        process_field_response(user_input)
    
    # Save chat after each interaction
    save_current_chat()


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="⚖️",
        layout="wide"
    )
    
    initialize_session_state()
    apply_custom_styles()
    
    st.title(APP_TITLE)
    st.caption("Generate Indian legal documents through conversational interface")
    
    render_sidebar()
    render_main_chat()
    render_download_section()
    
    user_input = st.chat_input("Enter your message...")
    
    if user_input:
        handle_user_input(user_input)
        st.rerun()


if __name__ == "__main__":
    main() 






