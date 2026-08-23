from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.controllers.rag_controller import RAGController, RAGQueryRequest
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/rag", tags=["RAG Pipeline"])
controller = RAGController()

@router.post("/query")
async def direct_rag_query(req: RAGQueryRequest, db: AsyncSession = Depends(get_db)):
    return await controller.direct_query(db, req)

@router.post("/reindex")
async def reindex_documents(
    user: User = Depends(AuthService.require_admin),
    db: AsyncSession = Depends(get_db)
):
    return await controller.reindex_all(db)

@router.get("/status")
async def get_rag_status():
    return await controller.get_status()
