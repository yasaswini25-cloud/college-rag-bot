import os
import uuid
import aiofiles
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, desc
from app.config.settings import settings
from app.models.document import Document
from app.models.chunk import DocumentChunk

class DocumentService:
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> tuple[str, str, int]:
        """
        Validates and saves uploaded file to UPLOAD_DIR.
        Returns: (file_path, filename, file_size_bytes)
        """
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Validate extension
        filename = file.filename or "uploaded_document"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        dest_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        file_size = 0
        async with aiofiles.open(dest_path, "wb") as out_file:
            content = await file.read()
            file_size = len(content)
            
            # Size check (25MB limit)
            if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                os.remove(dest_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
                )
            
            await out_file.write(content)

        return dest_path, filename, file_size

    @staticmethod
    async def create_document(
        db: AsyncSession,
        title: str,
        filename: str,
        file_path: str,
        category: str,
        department: str,
        version: str,
        file_size_bytes: int,
        uploaded_by: Optional[str] = None
    ) -> Document:
        doc = Document(
            id=str(uuid.uuid4()),
            title=title.strip() if title else filename,
            filename=filename,
            category=category or "General",
            department=department or "All",
            version=version or "1.0",
            file_url=file_path,
            file_size_bytes=file_size_bytes,
            status="PENDING",
            uploaded_by=uploaded_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def get_documents(
        db: AsyncSession,
        category: Optional[str] = None,
        department: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        stmt = select(Document).order_by(desc(Document.created_at))

        if category and category.lower() != "all":
            stmt = stmt.where(Document.category.ilike(f"%{category}%"))
        if department and department.lower() != "all":
            stmt = stmt.where(Document.department.ilike(f"%{department}%"))
        if status_filter and status_filter.lower() != "all":
            stmt = stmt.where(Document.status == status_filter.upper())
        if search:
            stmt = stmt.where(
                or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.filename.ilike(f"%{search}%"),
                    Document.category.ilike(f"%{search}%"),
                    Document.department.ilike(f"%{search}%")
                )
            )

        result = await db.execute(stmt)
        docs = result.scalars().all()
        return [d.to_dict() for d in docs]

    @staticmethod
    async def get_document_by_id(db: AsyncSession, doc_id: str) -> Optional[Document]:
        stmt = select(Document).where(Document.id == doc_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def update_document(
        db: AsyncSession,
        doc_id: str,
        title: Optional[str] = None,
        category: Optional[str] = None,
        department: Optional[str] = None,
        version: Optional[str] = None
    ) -> Document:
        doc = await DocumentService.get_document_by_id(db, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        if title is not None:
            doc.title = title.strip()
        if category is not None:
            doc.category = category
        if department is not None:
            doc.department = department
        if version is not None:
            doc.version = version
        doc.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: str) -> bool:
        doc = await DocumentService.get_document_by_id(db, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        # Delete physical file if exists
        if doc.file_url and os.path.exists(doc.file_url):
            try:
                os.remove(doc.file_url)
            except Exception:
                pass

        # Delete associated chunks
        await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc_id))
        
        # Delete document record
        await db.delete(doc)
        await db.commit()
        return True
