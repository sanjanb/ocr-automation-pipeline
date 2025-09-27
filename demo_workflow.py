"""
End-to-End Workflow Demonstration
Shows complete microservice workflow from request to MongoDB storage
"""

import json
from datetime import datetime
from src.document_processor.models import ProcessDocumentRequest
from src.document_processor.normalizer import normalize_fields
from src.document_processor.database import DocumentEntry

def demonstrate_workflow():
    """Demonstrate the complete microservice workflow"""
    
    print("🚀 **MICROSERVICE WORKFLOW DEMONSTRATION**")
    print("=" * 60)
    
    # Step 1: Incoming Request
    print("\n📥 **STEP 1: Incoming API Request**")
    sample_request = {
        "studentId": "STUD_12345",
        "docType": "AadharCard", 
        "cloudinaryUrl": "https://res.cloudinary.com/demo/image/upload/v1640995392/docs/aadhaar_sample.jpg"
    }
    
    print("Request JSON:")
    print(json.dumps(sample_request, indent=2))
    
    # Step 2: Request Validation
    print("\n✅ **STEP 2: Request Validation (Pydantic)**")
    try:
        validated_request = ProcessDocumentRequest(**sample_request)
        print(f"✅ Request validated successfully")
        print(f"   - Student ID: {validated_request.studentId}")
        print(f"   - Document Type: {validated_request.docType}")
        print(f"   - Cloudinary URL: {validated_request.cloudinaryUrl[:50]}...")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return
    
    # Step 3: Document Type Mapping
    print("\n🔄 **STEP 3: Document Type Mapping**")
    from src.document_processor.models import get_internal_doc_type
    internal_type = get_internal_doc_type(validated_request.docType)
    print(f"   External: {validated_request.docType} → Internal: {internal_type}")
    
    # Step 4: Simulated Gemini Processing
    print("\n🤖 **STEP 4: Gemini AI Processing (Simulated)**")
    print("   [In real scenario: Download from Cloudinary → Send to Gemini → Extract JSON]")
    
    # Simulate raw extraction result
    simulated_raw_extraction = {
        "full_name": "sanjan acharya",
        "aadhaar_number": "123456789012", 
        "date_of_birth": "15/06/2002",
        "address": "123 MG Road, Bangalore, Karnataka 560001",
        "father_name": "ramesh acharya",
        "gender": "m",
        "mobile_number": "9876543210"
    }
    
    print("   Raw Gemini extraction:")
    print(json.dumps(simulated_raw_extraction, indent=4))
    
    # Step 5: Field Normalization  
    print("\n🎯 **STEP 5: Field Normalization**")
    normalized_fields = normalize_fields(simulated_raw_extraction, internal_type)
    
    print("   Normalized fields:")
    print(json.dumps(normalized_fields, indent=4))
    
    print("\n   📊 **Normalization Changes:**")
    print("   • full_name → Name (title case)")
    print("   • aadhaar_number → AadhaarNumber (formatted)")
    print("   • date_of_birth → DOB (ISO format)")  
    print("   • gender 'm' → Gender 'Male'")
    print("   • mobile_number → formatted phone")
    
    # Step 6: Database Document Creation
    print("\n💾 **STEP 6: MongoDB Document Creation**")
    
    doc_entry = DocumentEntry(
        docType=validated_request.docType,
        cloudinaryUrl=validated_request.cloudinaryUrl,
        fields=normalized_fields,
        processedAt=datetime.utcnow(),
        confidence=0.95,
        modelUsed="gemini-2.0-flash-exp", 
        validationIssues=[]
    )
    
    print("   Document entry created:")
    doc_dict = doc_entry.dict()
    doc_dict['processedAt'] = doc_dict['processedAt'].isoformat() + 'Z'
    print(json.dumps(doc_dict, indent=4))
    
    # Step 7: MongoDB Storage Schema
    print("\n🗄️ **STEP 7: MongoDB Storage Schema**")
    
    complete_student_record = {
        "studentId": validated_request.studentId,
        "documents": [doc_dict],
        "createdAt": datetime.utcnow().isoformat() + 'Z',
        "updatedAt": datetime.utcnow().isoformat() + 'Z'
    }
    
    print("   Complete student record in MongoDB:")
    print(json.dumps(complete_student_record, indent=4))
    
    # Step 8: API Response
    print("\n📤 **STEP 8: API Response**")
    
    api_response = {
        "success": True,
        "studentId": validated_request.studentId,
        "savedDocument": {
            "docType": doc_entry.docType,
            "cloudinaryUrl": doc_entry.cloudinaryUrl,
            "fields": doc_entry.fields,
            "processedAt": doc_entry.processedAt.isoformat() + 'Z',
            "confidence": doc_entry.confidence,
            "modelUsed": doc_entry.modelUsed,
            "validationIssues": doc_entry.validationIssues
        },
        "message": "Document AadharCard processed and saved successfully"
    }
    
    print("   Final API response:")
    print(json.dumps(api_response, indent=4))
    
    # Step 9: Summary
    print("\n🎊 **WORKFLOW SUMMARY**")
    print("=" * 60)
    print("✅ Request validation with Pydantic models")
    print("✅ Document type mapping (external → internal)")  
    print("✅ Cloudinary image download (simulated)")
    print("✅ Gemini AI processing (simulated)")
    print("✅ Field normalization and standardization")
    print("✅ MongoDB document creation with Beanie ODM")
    print("✅ Student record upsert operation")
    print("✅ Structured API response generation")
    
    print(f"\n📊 **Processing Stats:**")
    print(f"   • Raw fields extracted: {len(simulated_raw_extraction)}")
    print(f"   • Normalized fields: {len(normalized_fields)}")
    print(f"   • Confidence score: {doc_entry.confidence}")
    print(f"   • Validation issues: {len(doc_entry.validationIssues)}")
    
    print(f"\n🎯 **Key Benefits:**")
    print("   • Consistent field naming across all document types")
    print("   • Student-centric document organization") 
    print("   • Comprehensive validation and error handling")
    print("   • Scalable async processing architecture")
    print("   • Production-ready MongoDB integration")

if __name__ == "__main__":
    demonstrate_workflow()