import re
from typing import List, Dict, Any, Optional

from app.rag.embeddings import STOPWORDS


class HybridReranker:
    """
    Hybrid reranker for retrieved document chunks.

    Ranking is based on:
    1. Semantic similarity
    2. Keyword relevance
    3. Document title relevance

    The retriever provides a larger candidate pool.
    This class produces the final Top-K results.
    """

    @staticmethod
    def rerank(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        final_k: Optional[int] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:

        if not retrieved_chunks:
            return []

        # ---------------------------------------------------------
        # 1. Extract meaningful query terms
        # ---------------------------------------------------------

        query_terms = {
            term
            for term in re.findall(
                r"\b\w+\b",
                query.lower()
            )
            if len(term) > 2
            and term not in STOPWORDS
        }

        # If there are no meaningful query terms,
        # return the original candidate pool.
        if not query_terms:
            if final_k is not None:
                return retrieved_chunks[:final_k]

            return retrieved_chunks

        reranked = []

        # ---------------------------------------------------------
        # 2. Score every candidate
        # ---------------------------------------------------------

        for item in retrieved_chunks:

            content = (
                item.get("content") or ""
            ).lower()

            title = (
                item.get("document_name") or ""
            ).lower()

            # Tokenize document content
            content_terms = set(
                re.findall(
                    r"\b\w+\b",
                    content
                )
            )

            # Tokenize document title
            title_terms = set(
                re.findall(
                    r"\b\w+\b",
                    title
                )
            )

            # -----------------------------------------------------
            # Content keyword relevance
            # -----------------------------------------------------

            content_matches = (
                query_terms & content_terms
            )

            # -----------------------------------------------------
            # Document title relevance
            # -----------------------------------------------------

            title_matches = (
                query_terms & title_terms
            )

            # Give document title matches additional importance.
            keyword_score = (
                len(content_matches)
                + (1.5 * len(title_matches))
            ) / max(
                len(query_terms),
                1
            )

            keyword_score = min(
                keyword_score,
                1.0
            )

            # -----------------------------------------------------
            # Semantic similarity
            # -----------------------------------------------------

            semantic_score = float(
                item.get(
                    "raw_cosine",
                    item.get(
                        "similarity_score",
                        0.0
                    )
                )
            )

            # -----------------------------------------------------
            # Final hybrid score
            # -----------------------------------------------------

            hybrid_score = (
                semantic_weight * semantic_score
                + keyword_weight * keyword_score
            )

            # Copy original item so we don't modify it directly.
            updated_item = dict(item)

            updated_item["hybrid_score"] = round(
                hybrid_score,
                4
            )

            updated_item["keyword_score"] = round(
                keyword_score,
                4
            )

            updated_item["content_matches"] = len(
                content_matches
            )

            updated_item["title_matches"] = len(
                title_matches
            )

            reranked.append(updated_item)

        # ---------------------------------------------------------
        # 3. Sort by hybrid score
        # ---------------------------------------------------------

        reranked.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        # ---------------------------------------------------------
        # 4. Return final Top-K
        # ---------------------------------------------------------

        if final_k is not None:
            return reranked[:final_k]

        return reranked