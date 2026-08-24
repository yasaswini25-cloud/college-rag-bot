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

    Pipeline:
    1. Semantic similarity using embeddings
    2. Keyword matching
    3. Section/title relevance
    4. Candidate filtering
    5. Returns a candidate pool for reranking
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

        final_k = top_k or settings.TOP_K

        # Retrieve a larger pool initially.
        candidate_k = max(final_k * 3, 15)

        threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.SIMILARITY_THRESHOLD
        )

        # ---------------------------------------------------------
        # 1. Query embedding
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
        # 2. Query terms
        # ---------------------------------------------------------

        query_terms = {
            word
            for word in re.findall(
                r"\b\w+\b",
                query.lower()
            )
            if len(word) > 2
            and word not in STOPWORDS
        }

        if not query_terms:
            return []

        # ---------------------------------------------------------
        # 3. Fetch indexed chunks
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

        if category and category.lower() != "all":
            stmt = stmt.where(
                Document.category.ilike(
                    f"%{category}%"
                )
            )

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

        scored_chunks = []

        # ---------------------------------------------------------
        # 4. Score every chunk
        # ---------------------------------------------------------

        for chunk, doc in rows:

            embedding = chunk.get_embedding()

            if not embedding:
                continue

            c_vec = np.array(
                embedding,
                dtype=np.float32
            )

            c_norm = np.linalg.norm(c_vec)

            if c_norm == 0:
                continue

            # -----------------------------------------------------
            # Semantic similarity
            # -----------------------------------------------------

            cosine_similarity = float(
                np.dot(q_vec, c_vec)
                / (q_norm * c_norm)
            )

            # -----------------------------------------------------
            # Text
            # -----------------------------------------------------

            content = (
                chunk.content or ""
            ).lower()

            title = (
                doc.title
                or doc.filename
                or ""
            ).lower()

            # -----------------------------------------------------
            # Tokenization
            # -----------------------------------------------------

            content_terms = set(
                re.findall(
                    r"\b\w+\b",
                    content
                )
            )

            title_terms = set(
                re.findall(
                    r"\b\w+\b",
                    title
                )
            )

            content_matches = (
                query_terms & content_terms
            )

            title_matches = (
                query_terms & title_terms
            )

            # -----------------------------------------------------
            # Keyword score
            # -----------------------------------------------------

            keyword_score = (
                len(content_matches)
                + 1.5 * len(title_matches)
            ) / max(
                len(query_terms),
                1
            )

            keyword_score = min(
                keyword_score,
                1.0
            )

            # -----------------------------------------------------
            # Exact phrase relevance
            # -----------------------------------------------------

            normalized_query = re.sub(
                r"\s+",
                " ",
                query.lower()
            ).strip()

            normalized_content = re.sub(
                r"\s+",
                " ",
                content
            )

            phrase_match = (
                1.0
                if normalized_query in normalized_content
                else 0.0
            )

            # -----------------------------------------------------
            # Important-term matching
            #
            # Give additional weight to nouns/concepts that
            # frequently define the actual intent.
            # -----------------------------------------------------

            important_terms = {
                term
                for term in query_terms
                if term not in {
                    "what",
                    "which",
                    "when",
                    "where",
                    "how",
                    "does",
                    "do",
                    "are",
                    "is",
                    "the",
                    "for",
                    "from",
                    "with"
                }
            }

            important_matches = (
                important_terms & content_terms
            )

            important_score = (
                len(important_matches)
                / max(len(important_terms), 1)
            )

            # -----------------------------------------------------
            # Hybrid score
            # -----------------------------------------------------

            combined_score = (
                0.55 * cosine_similarity
                + 0.25 * keyword_score
                + 0.15 * important_score
                + 0.05 * phrase_match
            )

            # -----------------------------------------------------
            # Threshold
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
                        cosine_similarity,
                        4
                    ),

                    "keyword_score": round(
                        keyword_score,
                        4
                    ),

                    "important_score": round(
                        important_score,
                        4
                    ),

                    "phrase_match": phrase_match,

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
        # 5. Sort
        # ---------------------------------------------------------

        scored_chunks.sort(
            key=lambda x: x["similarity_score"],
            reverse=True
        )

        # ---------------------------------------------------------
        # 6. Candidate pool
        # ---------------------------------------------------------

        return scored_chunks[:candidate_k]