# Implementation Plan

- [x] 1. Create Document Analyzer component for DOCX template analysis


  - Create `documents/document_analyzer.py` module
  - Implement placeholder extraction from DOCX files (paragraphs, tables, headers, footers)
  - Implement field type inference based on field names and context
  - Add support for multiple placeholder patterns ({{field}}, [field], __field__)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_



- [ ] 2. Create Template Matcher component for dynamic template discovery
  - Create `documents/template_matcher.py` module
  - Implement file search in documents folder with pattern matching
  - Add location-based template prioritization (e.g., "Jaipur_Marriage" over generic "Marriage")
  - Implement template metadata extraction from filenames


  - Add method to list all available templates
  - _Requirements: 1.3, 1.4, 1.5, 9.1, 9.2, 9.5_

- [ ] 3. Enhance Query Analyzer to integrate with new components
  - Create `utils/query_analyzer.py` module that wraps existing IntentDetector and EntityExtractor


  - Add fuzzy matching for document type detection
  - Enhance location extraction to support city names
  - Create QueryAnalysis dataclass to structure results
  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [x] 4. Create Field Comparator for intelligent field matching


  - Create `utils/field_comparator.py` module
  - Implement field name normalization (snake_case, camelCase, spaces)
  - Add fuzzy field name matching with configurable threshold
  - Implement semantic matching for synonyms (groom/husband, bride/wife)
  - Create FieldComparison dataclass to structure results
  - _Requirements: 4.1, 4.2, 4.3_



- [ ] 5. Enhance Data Collector with skip functionality
  - Update `utils/data_collector.py` module (or create if doesn't exist)
  - Add skip detection from user input (keywords: "skip", "pass", "next")
  - Implement skip state tracking
  - Update question generation to mention skip option
  - Handle skipped fields in collection flow
  - _Requirements: 5.1, 5.2, 6.1, 6.2, 6.3, 6.4_



- [ ] 6. Create Document Generator for template filling
  - Create `generators/template_document_generator.py` module
  - Implement DOCX placeholder replacement in paragraphs
  - Implement DOCX placeholder replacement in tables
  - Implement DOCX placeholder replacement in headers and footers


  - Add formatting preservation during replacement
  - Handle skipped fields (leave blank or use default value)
  - Implement descriptive filename generation
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 6.5, 8.3_

- [ ] 7. Create orchestration layer to coordinate all components
  - Create `core/document_processor.py` module

  - Implement ProcessingContext dataclass to maintain state
  - Create main processing pipeline that coordinates all components
  - Add error handling for each processing stage
  - Implement logging at each stage
  - _Requirements: 4.4, 4.5, 10.3, 10.5_

- [ ] 8. Integrate new backend with existing Streamlit UI
  - Update `main.py` to use new document processor
  - Modify `initialize_document_generation()` to use Template Matcher and Document Analyzer
  - Update `process_field_response()` to handle skip functionality


  - Modify `generate_document()` to use new Document Generator
  - Add UI indicators for skip option during field collection

  - Ensure backward compatibility with existing JSON-based templates
  - _Requirements: 5.3, 5.4, 5.5, 6.1, 8.1, 8.4, 8.5_

- [ ] 9. Add comprehensive error handling
  - Create custom exception classes in `core/exceptions.py`
  - Add try-catch blocks in all components
  - Implement user-friendly error messages

  - Add error logging with context
  - Implement retry logic for recoverable errors
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 10. Add configuration and utilities
  - Create `config.py` with placeholder patterns, field type keywords, etc.
  - Add fuzzy matching utility (optional: install rapidfuzz)


  - Create data models file `core/models.py` with all dataclasses
  - Add validation utilities for different field types
  - _Requirements: 2.3, 2.4, 5.3, 5.4_

- [ ] 11. Write unit tests for core components
  - Write tests for Document Analyzer (placeholder extraction, field type inference)
  - Write tests for Template Matcher (file search, fuzzy matching)
  - Write tests for Field Comparator (normalization, fuzzy matching)
  - Write tests for Document Generator (placeholder replacement, formatting)
  - Write tests for Query Analyzer integration
  - _Requirements: All requirements (validation)_

- [ ] 12. Write integration tests for end-to-end flow
  - Test complete flow with sample DOCX template
  - Test with various user queries
  - Test skip functionality
  - Test error scenarios (missing template, invalid input)
  - Verify generated documents are correct
  - _Requirements: All requirements (validation)_

- [ ] 13. Add documentation
  - Document new components with docstrings
  - Create README for new backend architecture
  - Add inline comments for complex logic
  - Document placeholder patterns and conventions
  - Create migration guide from JSON to DOCX templates
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
