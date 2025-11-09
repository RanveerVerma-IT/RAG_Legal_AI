"""
Quick test script to verify PDF generation works
"""
from generators.template_document_generator import template_document_generator
from pathlib import Path

def test_pdf_generation():
    """Test PDF generation with sample template"""
    
    # Test data
    template_path = Path("documents/Sample_Jaipur_Marriage_Form.docx")
    
    if not template_path.exists():
        print("❌ Sample template not found!")
        return
    
    field_data = {
        "groom_name": "John Doe",
        "groom_father_name": "Robert Doe",
        "groom_date_of_birth": "15-05-1990",
        "groom_address": "123 Main St, Jaipur",
        "groom_phone": "+919876543210",
        "bride_name": "Jane Smith",
        "bride_father_name": "Michael Smith",
        "bride_date_of_birth": "20-08-1992",
        "bride_address": "456 Oak Ave, Jaipur",
        "bride_phone": "+919876543211",
        "marriage_date": "10-11-2024",
        "marriage_place": "Jaipur, Rajasthan"
    }
    
    try:
        print("🔄 Generating document...")
        generated = template_document_generator.generate_document(
            template_path,
            field_data,
            []
        )
        
        print(f"✅ DOCX generated: {len(generated.document_bytes)} bytes")
        
        if generated.pdf_bytes:
            print(f"✅ PDF generated: {len(generated.pdf_bytes)} bytes")
            
            # Save test files
            with open("test_output.docx", "wb") as f:
                f.write(generated.document_bytes)
            print("📄 Saved: test_output.docx")
            
            with open("test_output.pdf", "wb") as f:
                f.write(generated.pdf_bytes)
            print("📄 Saved: test_output.pdf")
            
            print("\n✅ Both DOCX and PDF generation successful!")
        else:
            print("⚠️  PDF generation failed, but DOCX is available")
            
            # Save DOCX only
            with open("test_output.docx", "wb") as f:
                f.write(generated.document_bytes)
            print("📄 Saved: test_output.docx")
        
        print(f"\nFields filled: {len(generated.fields_filled)}")
        print(f"Fields skipped: {len(generated.fields_skipped)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pdf_generation()
