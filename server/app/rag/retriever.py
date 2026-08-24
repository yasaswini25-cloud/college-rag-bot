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
    Hybrid document retriever.

    Performs:
    1. Semantic retrieval using embedding cosine similarity.
    2. Lexical keyword matching.
    3. Hybrid scoring.
    4. Returns a larger candidate pool for downstream reranking.
    """

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator = None
    ):
        self.embedder = (
            embedding_generator
            or EmbeddingGenerator()
        )

    async def retrieve(
        self,
        db: AsyncSession,
        query: str,
        top_k: int = None,
        category: Optional[str] = None,
        department: Optional[str] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:

        # ---------------------------------------------------------
        # 1. Retrieval configuration
        # ---------------------------------------------------------

        final_k = top_k or settings.TOP_K

        # Retrieve more candidates initially.
        # The reranker will later reduce this to the final Top-K.
        candidate_k = max(final_k * 3, 15)

        threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.SIMILARITY_THRESHOLD
        )

        # ---------------------------------------------------------
        # 2. Generate query embedding
        # ---------------------------------------------------------

        query_vector = await self.embedder.get_embedding(query)

        q_vec = np.array(
            query_vector,
            dtype=np.float32
        )

        q_norm = np.linalg.norm(q_vec)

        if q_norm == 0:
            return []

        # ---------------------------------------------------------
        # 3. Extract meaningful query terms
        # ---------------------------------------------------------

        query_terms = [
            word
            for word in re.findall(
                r"\b\w+\b",
                query.lower()
            )
            if len(word) > 2
            and word not in STOPWORDS
        ]

        query_term_set = set(query_terms)

        # ---------------------------------------------------------
        # 4. Fetch indexed document chunks
        # ---------------------------------------------------------

        stmt = (
            select(DocumentChunk, Document)
            .join(
                Document,
                DocumentChunk.document_id == Document.id
            )
            .where(
                Document.status == "INDEXED"
            )
        )

        # Optional category filtering
        if category and category.lower() != "all":
            stmt = stmt.where(
                Document.category.ilike(
                    f"%{category}%"
                )
            )

        # Optional department filtering
        if department and department.lower() != "all":
            stmt = stmt.where(
                Document.department.ilike(
                    f"%{department}%"
                )
            )

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # ---------------------------------------------------------
        # 5. Score every chunk
        # ---------------------------------------------------------

        scored_chunks = []

        for chunk, doc in rows:

            emb = chunk.get_embedding()

            if not emb:
                continue

            c_vec = np.array(
                emb,
                dtype=np.float32
            )

            c_norm = np.linalg.norm(c_vec)

            if c_norm == 0:
                continue

            # -----------------------------------------------------
            # Semantic similarity
            # -----------------------------------------------------

            similarity = float(
                np.dot(q_vec, c_vec)
                / (q_norm * c_norm)
            )

            # -----------------------------------------------------
            # Token-based keyword matching
            # -----------------------------------------------------

            content = chunk.content or ""
            title = doc.title or doc.filename or ""

            content_terms = set(
                re.findall(
                    r"\b\w+\b",
                    content.lower()
                )
            )

            title_terms = set(
                re.findall(
                    r"\b\w+\b",
                    title.lower()
                )
            )

            content_matches = (
                query_term_set & content_terms
            )

            title_matches = (
                query_term_set & title_terms
            )

            # Content matches have normal weight.
            # Title matches receive additional importance.
            keyword_score = (
                len(content_matches)
                + (1.5 * len(title_matches))
            ) / max(
                len(query_term_set),
                1
            )

            keyword_score = min(
                keyword_score,
                1.0
            )

            # -----------------------------------------------------
            # Hybrid score
            # -----------------------------------------------------

            combined_score = (
                0.65 * similarity
                + 0.35 * keyword_score
            )

            # -----------------------------------------------------
            # Retrieval threshold
            # -----------------------------------------------------

            if combined_score < threshold:
                continue

            scored_chunks.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": doc.id,

                    "document_name": (
                        doc.title
                        or doc.filename
                    ),

                    "filename": doc.filename,

                    "category": doc.category,
                    "department": doc.department,
                    "version": doc.version,

                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,

                    "content": chunk.content,

                    "similarity_score": round(
                        combined_score,
                        4
                    ),

                    "raw_cosine": round(
                        similarity,
                        4
                    ),

                    "keyword_score": round(
                        keyword_score,
                        4
                    ),

                    "kw_matches": len(
                        content_matches
                    ),

                    "metadata": (
                        chunk.to_dict()
                        .get("metadata", {})
                    )
                }
            )

        # ---------------------------------------------------------
        # 6. Sort by initial retrieval score
        # ---------------------------------------------------------

        scored_chunks.sort(
            key=lambda x: x["similarity_score"],
            reverse=True
        )

        # ---------------------------------------------------------
        # 7. Return candidate pool
        #
        # IMPORTANT:
        # Do NOT immediately return final Top-K.
        # Give the reranker a larger candidate pool.
        # ---------------------------------------------------------

        return scored_chunks[:candidate_k]