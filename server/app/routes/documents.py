from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.controllers.document_controller import DocumentController, UpdateDocumentRequest
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form("General"),
    department: Optional[str] = Form("All"),
    version: Optional[str] = Form("1.0"),
    user: User = Depends(AuthService.require_admin),
    db: AsyncSession = Depends(get_db)
):
    return await DocumentController.upload_document(
        db=db,
        background_tasks=background_tasks,
        user=user,
        file=file,
        title=title,
        category=category,
        department=department,
        version=version
    )

@router.get("")
async def list_documents(
    category: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await DocumentController.list_documents(
        db=db,
        category=category,
        department=department,
        status=status,
        search=search
    )

@router.get("/{doc_id}")
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    return await DocumentController.get_document(db=db, doc_id=doc_id)

@router.put("/{doc_id}")
async def update_document(
    doc_id: str,
    req: UpdateDocumentRequest,
    user: User = Depends(AuthService.require_admin),
    db: AsyncSession = Depends(get_db)
):
    return await DocumentController.update_document(db=db, doc_id=doc_id, req=req)

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    user: User = Depends(AuthService.require_admin),
    db: AsyncSession = Depends(get_db)
):
    return await DocumentController.delete_document(db=db, doc_id=doc_id)
