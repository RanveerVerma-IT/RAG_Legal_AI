import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

import streamlit as st

from utils.entity_extractor import entity_extractor
from utils.validators import FieldValidatorFactory
from utils.template_manager import template_manager
from utils.intent_detector import intent_detector
from generators.document_factory import DocumentGeneratorFactory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


APP_TITLE = "Legal AI"
TEMPLATES_DIR = Path("templates")


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
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_conversation() -> None:
    keys_to_reset = [
        "messages", "awaiting_fields", "collected_data", "current_template",
        "current_state", "current_doc_type", "extracted_entities", "display_messages"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            st.session_state[key] = [] if key.endswith('s') else None
    st.session_state.collected_data = {}
    st.session_state.extracted_entities = {}


def add_system_message(content: str) -> None:
    st.session_state.messages.append({"role": "assistant", "content": content})
    st.session_state.display_messages.append({"role": "assistant", "content": content})


def add_user_message(content: str) -> None:
    st.session_state.messages.append({"role": "user", "content": content})
    st.session_state.display_messages.append({"role": "user", "content": content})


def detect_document_intent(user_input: str) -> tuple[Optional[str], str]:
    """Detect document type and state using intent detector"""
    return intent_detector.detect_intent(user_input)


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


def process_field_response(user_input: str) -> None:
    """Process user response for field with validation"""
    if not st.session_state.awaiting_fields:
        return
    
    current_field = st.session_state.awaiting_fields[0]
    field_value = user_input.strip()
    
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
                message = f"Invalid input: {error}\n\nPlease try again."
                add_system_message(message)
                return
            
            field_value = formatted_value
        
        # Store validated value
        st.session_state.collected_data[current_field] = field_value
        st.session_state.awaiting_fields = st.session_state.awaiting_fields[1:]
        
        if st.session_state.awaiting_fields:
            next_field = st.session_state.awaiting_fields[0]
            prompt = template_manager.get_field_question(state, doc_type, next_field)
            message = f"Recorded {current_field.replace('_', ' ')}.\n\n{prompt}"
            add_system_message(message)
        else:
            message = "All required information collected. Generating your document now."
            add_system_message(message)
            generate_document()
    else:
        prompt = template_manager.get_field_question(
            st.session_state.current_state,
            st.session_state.current_doc_type,
            current_field
        )
        message = f"Please provide {current_field.replace('_', ' ')}. {prompt}"
        add_system_message(message)


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
                font-size: 14px;
                cursor: pointer;
                transition: background-color 0.2s;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .chat-item:hover {
                background-color: #2a2a2a;
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
            </style>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("New chat", use_container_width=True, key="new_chat"):
            reset_conversation()
            st.rerun()
        
        # Quick Actions Section
        st.markdown('<div class="sidebar-section-title">Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("Marriage Certificate", use_container_width=True, key="quick_marriage"):
            add_user_message("Generate marriage certificate")
            detect_intent_and_bootstrap("Generate marriage certificate")
            st.rerun()
        
        if st.button("Birth Certificate", use_container_width=True, key="quick_birth"):
            add_user_message("Generate birth certificate")
            detect_intent_and_bootstrap("Generate birth certificate")
            st.rerun()
        
        # Chat History Section
        st.markdown('<div class="sidebar-section-title">Recent Chats</div>', unsafe_allow_html=True)
        
        if st.session_state.messages:
            # Group messages into conversations (simplified - showing last 5 user messages)
            user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
            recent_chats = user_messages[-5:] if len(user_messages) > 5 else user_messages
            
            for i, msg in enumerate(reversed(recent_chats)):
                # Truncate long messages for display
                display_text = msg["content"][:40] + "..." if len(msg["content"]) > 40 else msg["content"]
                st.markdown(f'<div class="chat-item">💬 {display_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: #6e6e73; font-size: 13px; padding: 12px 8px; text-align: center;">No chat history yet</div>', unsafe_allow_html=True)


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
    
    if st.session_state.current_template is None:
        detect_intent_and_bootstrap(user_input)
    else:
        process_field_response(user_input)


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

