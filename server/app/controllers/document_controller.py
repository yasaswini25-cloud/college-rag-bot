from typing import Optional
from fastapi import UploadFile, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.document_service import DocumentService
from app.services.processing_service import ProcessingService
from app.models.user import User

class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    version: Optional[str] = None

class DocumentController:
    @staticmethod
    async def upload_document(
        db: AsyncSession,
        background_tasks: BackgroundTasks,
        user: User,
        file: UploadFile,
        title: Optional[str] = None,
        category: Optional[str] = "General",
        department: Optional[str] = "All",
        version: Optional[str] = "1.0"
    ):
        file_path, filename, file_size = await DocumentService.save_uploaded_file(file)
        
        doc = await DocumentService.create_document(
            db=db,
            title=title or filename,
            filename=filename,
            file_path=file_path,
            category=category or "General",
            department=department or "All",
            version=version or "1.0",
            file_size_bytes=file_size,
            uploaded_by=user.id
        )

        # Trigger async ingestion pipeline in background
        background_tasks.add_task(ProcessingService.process_document, doc.id)

        return {
            "message": "Document uploaded successfully. Processing in progress.",
            "document": doc.to_dict()
        }

    @staticmethod
    async def list_documents(
        db: AsyncSession,
        category: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ):
        return await DocumentService.get_documents(
            db=db,
            category=category,
            department=department,
            status_filter=status,
            search=search
        )

    @staticmethod
    async def get_document(db: AsyncSession, doc_id: str):
        doc = await DocumentService.get_document_by_id(db, doc_id)
        return doc.to_dict() if doc else None

    @staticmethod
    async def update_document(db: AsyncSession, doc_id: str, req: UpdateDocumentRequest):
        doc = await DocumentService.update_document(
            db=db,
            doc_id=doc_id,
            title=req.title,
            category=req.category,
            department=req.department,
            version=req.version
        )
        return doc.to_dict()

    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: str):
        success = await DocumentService.delete_document(db=db, doc_id=doc_id)
        return {"status": "ok", "deleted": success}
