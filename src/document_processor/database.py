"""
MongoDB Database Configuration and Models
Handles student document storage and retrieval
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, init_beanie
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class DocumentEntry(BaseModel):
    """Individual document entry within a student record"""
    docType: str = Field(..., description="Type of document (AadharCard, MarkSheet10, etc.)")
    cloudinaryUrl: Optional[str] = Field(None, description="Cloudinary URL of the document image")
    documentPath: Optional[str] = Field(None, description="Local file path for testing")
    fields: Dict[str, Any] = Field(..., description="Extracted document fields")
    processedAt: datetime = Field(default_factory=datetime.utcnow, description="When the document was processed")
    confidence: float = Field(..., description="Processing confidence score")
    validationIssues: List[str] = Field(default_factory=list, description="Validation issues found")

class StudentDocument(Document):
    """Student document collection in MongoDB"""
    studentId: str = Field(..., description="Unique student identifier", unique=True)
    documents: List[DocumentEntry] = Field(default_factory=list, description="List of processed documents")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Settings:
        name = "students"
        indexes = [
            "studentId",
            "createdAt",
            "documents.docType",
        ]
    
    async def add_document(self, doc_entry: DocumentEntry) -> "StudentDocument":
        """Add a new document to the student record"""
        # Check if document type already exists and update or append
        existing_doc_index = None
        for i, doc in enumerate(self.documents):
            if doc.docType == doc_entry.docType:
                existing_doc_index = i
                break
        
        if existing_doc_index is not None:
            # Update existing document
            self.documents[existing_doc_index] = doc_entry
            logger.info(f"Updated existing {doc_entry.docType} for student {self.studentId}")
        else:
            # Add new document
            self.documents.append(doc_entry)
            logger.info(f"Added new {doc_entry.docType} for student {self.studentId}")
        
        self.updatedAt = datetime.utcnow()
        await self.save()
        return self
    
    @classmethod
    async def find_or_create_student(cls, student_id: str) -> "StudentDocument":
        """Find existing student or create new one"""
        student = await cls.find_one(cls.studentId == student_id)
        if not student:
            student = cls(studentId=student_id)
            await student.insert()
            logger.info(f"Created new student record: {student_id}")
        return student
    
    async def get_documents_by_type(self, doc_type: str) -> List[DocumentEntry]:
        """Get all documents of a specific type for this student"""
        return [doc for doc in self.documents if doc.docType == doc_type]
    
    async def get_latest_document(self, doc_type: str = None) -> Optional[DocumentEntry]:
        """Get the most recently processed document, optionally filtered by type"""
        filtered_docs = self.documents
        if doc_type:
            filtered_docs = [doc for doc in self.documents if doc.docType == doc_type]
        
        if not filtered_docs:
            return None
        
        return max(filtered_docs, key=lambda doc: doc.processedAt)

class DatabaseManager:
    """Database connection and initialization manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    async def connect_db(self, connection_string: str = None):
        """Initialize database connection"""
        if not connection_string:
            connection_string = os.getenv("MONGODB_URL", "mongodb://localhost:27017/document_processor")
        
        try:
            self.client = AsyncIOMotorClient(connection_string)
            # Extract database name from connection string
            db_name = connection_string.split('/')[-1] or "document_processor"
            self.database = self.client[db_name]
            
            # Initialize Beanie with document models
            await init_beanie(database=self.database, document_models=[StudentDocument])
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {db_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect_db(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            if not self.client:
                return False
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False

# Global database manager instance
db_manager = DatabaseManager()

async def get_database():
    """Get database manager instance"""
    return db_manager