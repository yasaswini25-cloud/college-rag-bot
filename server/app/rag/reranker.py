import re

from typing import List, Dict, Any

from app.rag.embeddings import STOPWORDS


class HybridReranker:
    """
    Final relevance reranker.

    Combines:
    - semantic similarity
    - keyword overlap
    - important-term overlap
    - document title relevance
    - exact phrase relevance
    """

    @staticmethod
    def rerank(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        semantic_weight: float = 0.60,
        keyword_weight: float = 0.25,
        important_weight: float = 0.15
    ) -> List[Dict[str, Any]]:

        if not retrieved_chunks:
            return []

        # ---------------------------------------------------------
        # Query terms
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

        reranked = []

        for item in retrieved_chunks:

            content = (
                item.get("content") or ""
            ).lower()

            title = (
                item.get("document_name") or ""
            ).lower()

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
            # Keyword relevance
            # -----------------------------------------------------

            content_matches = (
                query_terms & content_terms
            )

            title_matches = (
                query_terms & title_terms
            )

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
            # Important-term relevance
            # -----------------------------------------------------

            important_matches = (
                important_terms & content_terms
            )

            important_score = (
                len(important_matches)
                / max(
                    len(important_terms),
                    1
                )
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
            # Final score
            # -----------------------------------------------------

            hybrid_score = (
                semantic_weight * semantic_score
                + keyword_weight * keyword_score
                + important_weight * important_score
            )

            # -----------------------------------------------------
            # Penalize weak lexical relevance
            #
            # Prevents chunks such as fee/refund information
            # from ranking highly for document-verification queries.
            # -----------------------------------------------------

            if (
                important_terms
                and len(important_matches) == 0
            ):
                hybrid_score *= 0.65

            updated_item = dict(item)

            updated_item["hybrid_score"] = round(
                hybrid_score,
                4
            )

            updated_item["keyword_score"] = round(
                keyword_score,
                4
            )

            updated_item["important_score"] = round(
                important_score,
                4
            )

            updated_item["content_matches"] = len(
                content_matches
            )

            updated_item["title_matches"] = len(
                title_matches
            )

            updated_item["important_matches"] = len(
                important_matches
            )

            reranked.append(updated_item)

        # ---------------------------------------------------------
        # Sort
        # ---------------------------------------------------------

        reranked.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        # ---------------------------------------------------------
        # IMPORTANT:
        # Return only final Top-K
        # ---------------------------------------------------------

        final_k = 5

        return reranked[:final_k]