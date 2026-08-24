import re

from typing import List, Dict, Any

from app.rag.embeddings import STOPWORDS


class HybridReranker:
    """
    Reranks retrieved chunks using:
    1. Semantic similarity
    2. Token-based keyword relevance
    3. Document title relevance

    The retriever provides a larger candidate pool.
    This class produces the final ranking.
    """

    @staticmethod
    def rerank(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
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

        if not query_terms:
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

            # Tokenize content and title.
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

            # -----------------------------------------------------
            # Content relevance
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

            # Give title matches higher importance.
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
            # Semantic score
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
            # Final reranking score
            # -----------------------------------------------------

            hybrid_score = (
                semantic_weight * semantic_score
                + keyword_weight * keyword_score
            )

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
        # 3. Sort by final reranking score
        # ---------------------------------------------------------

        reranked.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        # ---------------------------------------------------------
        # 4. Return final Top-K
        # ---------------------------------------------------------

        return reranked