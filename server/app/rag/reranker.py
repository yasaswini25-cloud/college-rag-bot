import re
from typing import List, Dict, Any

class HybridReranker:
    """
    Reranks retrieved chunks combining semantic vector score with keyword match BM25/TF-IDF score.
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

        query_terms = set(re.findall(r"\w+", query.lower()))
        if not query_terms:
            return retrieved_chunks

        reranked = []
        for item in retrieved_chunks:
            content = item.get("content", "").lower()
            title = item.get("document_name", "").lower()
            
            # Count term matches
            matches = 0
            for term in query_terms:
                if len(term) <= 2:
                    continue
                # Term match in content
                if term in content:
                    matches += 1.0
                # Higher weight if matching document title
                if term in title:
                    matches += 1.5

            keyword_score = min(matches / max(len(query_terms), 1), 1.0)
            semantic_score = item.get("similarity_score", 0.0)

            # Combined hybrid score
            hybrid_score = (semantic_weight * semantic_score) + (keyword_weight * keyword_score)
            
            updated_item = dict(item)
            updated_item["hybrid_score"] = round(hybrid_score, 4)
            updated_item["keyword_score"] = round(keyword_score, 4)
            reranked.append(updated_item)

        # Sort by hybrid score
        reranked.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return reranked
