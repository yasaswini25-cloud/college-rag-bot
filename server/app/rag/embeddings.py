import math
import hashlib
import re
import numpy as np
from typing import List
from app.config.settings import settings

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", 
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", 
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", 
    "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself", "yourselves"
}

class EmbeddingGenerator:
    """
    Generates dense vector embeddings using Gemini, OpenAI, or local deterministic fallback.
    """
    def __init__(self, provider: str = None):
        self.provider = (provider or settings.EMBEDDING_PROVIDER).lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.dimension = 768  # Standard vector dimension

    async def get_embedding(self, text: str) -> List[float]:
        embeddings = await self.get_embeddings_batch([text])
        return embeddings[0] if embeddings else [0.0] * self.dimension

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # Try Gemini API if key is present
        if self.gemini_key and (self.provider == "gemini" or self.provider == "auto"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                
                results = []
                for text in texts:
                    res = genai.embed_content(
                        model="models/text-embedding-004",
                        content=text,
                        task_type="retrieval_document"
                    )
                    emb = res.get("embedding", [])
                    results.append(emb)
                return results
            except Exception as e:
                print(f"[EmbeddingGenerator] Gemini API error: {e}. Falling back to local vectorizer.")

        # Try OpenAI API if key is present
        if self.openai_key and (self.provider == "openai" or self.provider == "auto"):
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.openai_key)
                response = await client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                print(f"[EmbeddingGenerator] OpenAI API error: {e}. Falling back to local vectorizer.")

        # High-performance Deterministic Positive Vectorizer
        return [self._local_dense_vector(t) for t in texts]

    def _local_dense_vector(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension

        vec = np.zeros(self.dimension, dtype=np.float32)
        words = re.findall(r"\w+", text.lower())

        for i, word in enumerate(words):
            if not word or len(word) <= 1 or word in STOPWORDS:
                continue

            # Term frequency hashing
            h1 = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx1 = h1 % self.dimension
            vec[idx1] += 2.0

            # 3-gram character subword hashing
            if len(word) >= 3:
                for j in range(len(word) - 2):
                    sub = word[j:j+3]
                    h2 = int(hashlib.sha256(sub.encode("utf-8")).hexdigest(), 16)
                    idx2 = h2 % self.dimension
                    vec[idx2] += 0.5

        # L2 Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()
