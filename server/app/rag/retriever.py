import re
import numpy as np

from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.rag.embeddings import EmbeddingGenerator, STOPWORDS
from app.config.settings import settings


class VectorRetriever:
    """
    Hybrid document retriever.

    Pipeline:
    1. Semantic retrieval using embedding cosine similarity.
    2. Lexical keyword matching.
    3. Hybrid scoring.
    4. Candidate retrieval.
    5. Neighbor-chunk expansion for contextual continuity.

    Neighbor expansion is especially useful for:
    - lists
    - tables
    - multi-sentence answers
    - sections split across chunk boundaries
    - admission requirements
    - procedures and eligibility criteria
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

        # Retrieve a larger candidate pool first.
        candidate_k = max(final_k * 3, 15)

        threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.SIMILARITY_THRESHOLD
        )

        # Number of neighboring chunks to add around strong matches.
        neighbor_window = 1

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
            # Keyword matching
            # -----------------------------------------------------

            content = chunk.content or ""

            title = (
                doc.title
                or doc.filename
                or ""
            )

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
                    ),

                    # This is a direct retrieval result.
                    "expanded": False
                }
            )

        # ---------------------------------------------------------
        # 6. Sort initial candidates
        # ---------------------------------------------------------

        scored_chunks.sort(
            key=lambda x: x["similarity_score"],
            reverse=True
        )

        # Keep a larger pool for expansion.
        initial_candidates = scored_chunks[:candidate_k]

        if not initial_candidates:
            return []

        # ---------------------------------------------------------
        # 7. Select strong anchor chunks
        # ---------------------------------------------------------
        #
        # We don't expand every candidate.
        #
        # Instead, expand the strongest results so unrelated
        # documents do not flood the context.
        # ---------------------------------------------------------

        anchor_count = min(
            max(final_k, 3),
            len(initial_candidates)
        )

        anchors = initial_candidates[:anchor_count]

        # ---------------------------------------------------------
        # 8. Retrieve neighboring chunks
        # ---------------------------------------------------------

        expanded_chunks = {}

        # Add all original candidates first.
        for item in initial_candidates:
            expanded_chunks[item["chunk_id"]] = item

        for anchor in anchors:

            document_id = anchor["document_id"]
            anchor_index = anchor["chunk_index"]

            start_index = max(
                0,
                anchor_index - neighbor_window
            )

            end_index = (
                anchor_index
                + neighbor_window
            )

            neighbor_stmt = (
                select(
                    DocumentChunk,
                    Document
                )
                .join(
                    Document,
                    DocumentChunk.document_id
                    == Document.id
                )
                .where(
                    and_(
                        DocumentChunk.document_id
                        == document_id,

                        DocumentChunk.chunk_index
                        >= start_index,

                        DocumentChunk.chunk_index
                        <= end_index,

                        Document.status
                        == "INDEXED"
                    )
                )
            )

            neighbor_result = await db.execute(
                neighbor_stmt
            )

            neighbor_rows = neighbor_result.all()

            for neighbor_chunk, neighbor_doc in neighbor_rows:

                # Already retrieved normally.
                if neighbor_chunk.id in expanded_chunks:
                    continue

                neighbor_content = (
                    neighbor_chunk.content
                    or ""
                )

                if not neighbor_content.strip():
                    continue

                # -------------------------------------------------
                # Important:
                # Neighbor chunks are NOT treated as equally
                # relevant semantic matches.
                #
                # They are contextual expansions.
                # -------------------------------------------------

                expanded_chunks[
                    neighbor_chunk.id
                ] = {
                    "chunk_id": neighbor_chunk.id,

                    "document_id": neighbor_doc.id,

                    "document_name": (
                        neighbor_doc.title
                        or neighbor_doc.filename
                    ),

                    "filename": neighbor_doc.filename,

                    "category": neighbor_doc.category,

                    "department": neighbor_doc.department,

                    "version": neighbor_doc.version,

                    "page_number": neighbor_chunk.page_number,

                    "chunk_index": neighbor_chunk.chunk_index,

                    "content": neighbor_content,

                    # Give neighboring chunks a lower score
                    # so they don't outrank directly relevant
                    # chunks.
                    "similarity_score": 0.0,

                    "raw_cosine": 0.0,

                    "keyword_score": 0.0,

                    "kw_matches": 0,

                    "metadata": (
                        neighbor_chunk.to_dict()
                        .get("metadata", {})
                    ),

                    "expanded": True,

                    "expanded_from_chunk": anchor_index
                }

        # ---------------------------------------------------------
        # 9. Convert dictionary back to list
        # ---------------------------------------------------------

        all_chunks = list(
            expanded_chunks.values()
        )

        # ---------------------------------------------------------
        # 10. Sort by document + chunk order
        #
        # This is important because the LLM should see neighboring
        # chunks in their natural document order.
        # ---------------------------------------------------------

        all_chunks.sort(
            key=lambda x: (
                str(x["document_id"]),
                x["chunk_index"]
            )
        )

        # ---------------------------------------------------------
        # 11. Return expanded context
        # ---------------------------------------------------------

        return all_chunks