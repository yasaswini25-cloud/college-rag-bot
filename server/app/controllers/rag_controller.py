from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rag_service import RAGService
from app.services.embedding_service import EmbeddingService

class RAGQueryRequest(BaseModel):
    query: str
    category: Optional[str] = None
    department: Optional[str] = None
    topK: Optional[int] = 5

class RAGController:
    def __init__(self):
        self.rag_service = RAGService()

    async def direct_query(self, db: AsyncSession, req: RAGQueryRequest):
        return await self.rag_service.query(
            db=db,
            question=req.query,
            category=req.category,
            department=req.department,
            top_k=req.topK
        )

    async def reindex_all(self, db: AsyncSession):
        return await EmbeddingService.reindex_all(db=db)

    async def get_status(self):
        from app.config.settings import settings
        return {
            "llm_provider": settings.LLM_PROVIDER,
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "top_k": settings.TOP_K,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD,
            "hybrid_search": settings.HYBRID_SEARCH
        }
