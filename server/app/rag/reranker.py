import re
from typing import List, Dict, Any

from app.rag.embeddings import STOPWORDS


class HybridReranker:
    """
    Strict hybrid reranker for the college RAG system.

    Ranking uses:
    1. Semantic similarity
    2. Keyword overlap
    3. Document title relevance
    4. Exact phrase relevance

    Important:
    Irrelevant chunks are filtered before they reach the LLM.
    This reduces hallucination and prevents unrelated documents/pages
    from being cited.
    """

    @staticmethod
    def _tokenize(text: str) -> set:
        """
        Convert text into meaningful lowercase tokens.
        """
        return {
            term
            for term in re.findall(r"\b\w+\b", text.lower())
            if len(term) > 2 and term not in STOPWORDS
        }

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize text for phrase matching.
        """
        return re.sub(
            r"\s+",
            " ",
            text.lower()
        ).strip()

    @staticmethod
    def rerank(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        semantic_weight: float = 0.60,
        keyword_weight: float = 0.30,
        phrase_weight: float = 0.10,
        final_k: int = 5
    ) -> List[Dict[str, Any]]:

        if not retrieved_chunks:
            return []

        query = query.strip()

        if not query:
            return []

        # ---------------------------------------------------------
        # 1. Extract query terms
        # ---------------------------------------------------------

        query_terms = HybridReranker._tokenize(query)

        if not query_terms:
            return []

        normalized_query = HybridReranker._normalize(query)

        reranked = []

        # ---------------------------------------------------------
        # 2. Score every retrieved candidate
        # ---------------------------------------------------------

        for item in retrieved_chunks:

            content = (
                item.get("content")
                or ""
            )

            document_name = (
                item.get("document_name")
                or item.get("filename")
                or ""
            )

            normalized_content = HybridReranker._normalize(
                content
            )

            normalized_title = HybridReranker._normalize(
                document_name
            )

            content_terms = HybridReranker._tokenize(
                content
            )

            title_terms = HybridReranker._tokenize(
                document_name
            )

            # -----------------------------------------------------
            # Keyword matching
            # -----------------------------------------------------

            content_matches = (
                query_terms & content_terms
            )

            title_matches = (
                query_terms & title_terms
            )

            content_coverage = (
                len(content_matches)
                / max(len(query_terms), 1)
            )

            title_coverage = (
                len(title_matches)
                / max(len(query_terms), 1)
            )

            keyword_score = (
                0.75 * content_coverage
                + 0.25 * title_coverage
            )

            keyword_score = min(
                keyword_score,
                1.0
            )

            # -----------------------------------------------------
            # Exact phrase matching
            # -----------------------------------------------------

            phrase_score = 0.0

            # Full question appears in chunk
            if normalized_query in normalized_content:
                phrase_score = 1.0

            else:
                # Check meaningful consecutive word phrases.
                query_words = [
                    word
                    for word in re.findall(
                        r"\b\w+\b",
                        normalized_query
                    )
                    if len(word) > 2
                    and word not in STOPWORDS
                ]

                if len(query_words) >= 2:

                    phrase_lengths = []

                    for size in range(
                        min(4, len(query_words)),
                        1,
                        -1
                    ):
                        for i in range(
                            len(query_words) - size + 1
                        ):
                            phrase = " ".join(
                                query_words[i:i + size]
                            )

                            if phrase in normalized_content:
                                phrase_lengths.append(size)

                    if phrase_lengths:
                        longest_phrase = max(
                            phrase_lengths
                        )

                        phrase_score = min(
                            longest_phrase / 4.0,
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

            # Cosine values can occasionally be outside the
            # expected range due to upstream calculations.
            semantic_score = max(
                0.0,
                min(
                    semantic_score,
                    1.0
                )
            )

            # -----------------------------------------------------
            # Final hybrid score
            # -----------------------------------------------------

            hybrid_score = (
                semantic_weight * semantic_score
                + keyword_weight * keyword_score
                + phrase_weight * phrase_score
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

            updated_item["phrase_score"] = round(
                phrase_score,
                4
            )

            updated_item["raw_cosine"] = round(
                semantic_score,
                4
            )

            updated_item["content_matches"] = len(
                content_matches
            )

            updated_item["title_matches"] = len(
                title_matches
            )

            # -----------------------------------------------------
            # Relevance classification
            # -----------------------------------------------------

            updated_item["is_lexically_relevant"] = (
                len(content_matches) > 0
                or len(title_matches) > 0
                or phrase_score > 0
            )

            reranked.append(updated_item)

        # ---------------------------------------------------------
        # 3. STRICT RELEVANCE FILTER
        # ---------------------------------------------------------
        #
        # If at least one candidate has lexical relevance,
        # remove candidates that have ZERO lexical relationship
        # with the question.
        #
        # Example:
        #
        # Query:
        # "What documents are required for admission verification?"
        #
        # Page 4:
        # documents + verification
        #
        # Page 5:
        # withdrawal + refund
        #
        # Page 5 should not reach the generator.
        # ---------------------------------------------------------

        lexically_relevant = [
            item
            for item in reranked
            if item["is_lexically_relevant"]
        ]

        if lexically_relevant:
            reranked = lexically_relevant

        else:
            # No lexical evidence anywhere.
            #
            # For a strict college knowledge assistant,
            # it is safer to return nothing than to pass
            # semantically similar but unrelated documents
            # to the LLM.
            return []

        # ---------------------------------------------------------
        # 4. Sort by hybrid relevance
        # ---------------------------------------------------------

        reranked.sort(
            key=lambda x: (
                x["hybrid_score"],
                x["keyword_score"],
                x["phrase_score"],
                x["raw_cosine"]
            ),
            reverse=True
        )

        # ---------------------------------------------------------
        # 5. Final Top-K
        # ---------------------------------------------------------

        return reranked[:final_k]