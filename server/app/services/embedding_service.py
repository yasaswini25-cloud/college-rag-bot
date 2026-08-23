from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chunk import DocumentChunk
from app.rag.embeddings import EmbeddingGenerator

class EmbeddingService:
    @staticmethod
    async def reindex_all(db: AsyncSession) -> Dict[str, Any]:
        """
        Re-generates vector embeddings for all existing chunks in the system.
        """
        stmt = select(DocumentChunk)
        result = await db.execute(stmt)
        chunks = result.scalars().all()

        if not chunks:
            return {"status": "ok", "reindexed_count": 0}

        embedder = EmbeddingGenerator()
        texts = [c.content for c in chunks]
        embeddings = await embedder.get_embeddings_batch(texts)

        for i, c in enumerate(chunks):
            if i < len(embeddings):
                c.set_embedding(embeddings[i])

        await db.commit()
        return {"status": "ok", "reindexed_count": len(chunks)}
