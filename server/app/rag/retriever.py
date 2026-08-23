import re
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.rag.embeddings import EmbeddingGenerator, STOPWORDS
from app.config.settings import settings

class VectorRetriever:
    """
    Retrieves top-K relevant chunks using hybrid vector cosine similarity & keyword scoring.
    """
    def __init__(self, embedding_generator: EmbeddingGenerator = None):
        self.embedder = embedding_generator or EmbeddingGenerator()

    async def retrieve(
        self,
        db: AsyncSession,
        query: str,
        top_k: int = None,
        category: Optional[str] = None,
        department: Optional[str] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        top_k = top_k or settings.TOP_K
        threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

        # 1. Generate query embedding
        query_vector = await self.embedder.get_embedding(query)
        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)

        query_terms = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2 and w not in STOPWORDS]

        # 2. Fetch indexed chunks joined with document metadata
        stmt = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.status == "INDEXED")
        )

        if category and category.lower() != "all":
            stmt = stmt.where(Document.category.ilike(f"%{category}%"))
        
        if department and department.lower() != "all":
            stmt = stmt.where(Document.department.ilike(f"%{department}%"))

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # 3. Compute cosine similarities and keyword matches
        scored_chunks = []
        for chunk, doc in rows:
            emb = chunk.get_embedding()
            if not emb:
                continue
            
            c_vec = np.array(emb, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0 or q_norm == 0:
                continue

            similarity = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))

            # Calculate keyword match bonus
            content_lower = chunk.content.lower()
            title_lower = (doc.title or "").lower()
            kw_matches = sum(1 for term in query_terms if term in content_lower or term in title_lower)
            kw_score = kw_matches / max(len(query_terms), 1) if query_terms else 0.0

            # Combined match score
            combined_score = (0.65 * similarity) + (0.35 * kw_score)

            # Pass if semantic similarity or combined score meets threshold
            if similarity >= threshold or (kw_matches > 0 and combined_score >= 0.20):
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "document_name": doc.title or doc.filename,
                    "filename": doc.filename,
                    "category": doc.category,
                    "department": doc.department,
                    "version": doc.version,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity_score": round(max(similarity, combined_score), 4),
                    "raw_cosine": round(similarity, 4),
                    "kw_matches": kw_matches,
                    "metadata": chunk.to_dict().get("metadata", {})
                })

        # 4. Sort descending by score
        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)

        # 5. Return top_k
        return scored_chunks[:top_k]
