import time
from typing import List, Dict, Any, Optional, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.retriever import VectorRetriever
from app.rag.reranker import HybridReranker
from app.rag.generator import LLMGenerator
from app.config.settings import settings


class RAGService:
    def __init__(self):
        self.retriever = VectorRetriever()
        self.generator = LLMGenerator()

    async def query(
        self,
        db: AsyncSession,
        question: str,
        category: Optional[str] = None,
        department: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None,
        top_k: int = None
    ) -> Dict[str, Any]:

        start_time = time.time()

        # ---------------------------------------------------------
        # 1. Retrieve candidate chunks
        # ---------------------------------------------------------

        final_top_k = top_k or settings.TOP_K

        retrieved_chunks = await self.retriever.retrieve(
            db=db,
            query=question,
            top_k=final_top_k,
            category=category,
            department=department
        )

        # ---------------------------------------------------------
        # 2. Apply hybrid re-ranking
        # ---------------------------------------------------------

        if settings.HYBRID_SEARCH and retrieved_chunks:

            retrieved_chunks = HybridReranker.rerank(
                query=question,
                retrieved_chunks=retrieved_chunks,
                top_k=final_top_k
            )

        # ---------------------------------------------------------
        # 3. Generate grounded answer
        # ---------------------------------------------------------

        gen_result = await self.generator.generate_answer(
            query=question,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history
        )

        latency_ms = int(
            (time.time() - start_time) * 1000
        )

        return {
            "answer": gen_result.get("answer"),
            "sources": gen_result.get("sources", []),
            "retrieved_chunks": retrieved_chunks,
            "grounded": gen_result.get("grounded", False),
            "model": gen_result.get("model", "local"),
            "latency_ms": latency_ms
        }

    async def stream_query(
        self,
        db: AsyncSession,
        question: str,
        category: Optional[str] = None,
        department: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None,
        top_k: int = None
    ) -> AsyncGenerator[Dict[str, Any], None]:

        # ---------------------------------------------------------
        # 1. Retrieve candidate chunks
        # ---------------------------------------------------------

        final_top_k = top_k or settings.TOP_K

        retrieved_chunks = await self.retriever.retrieve(
            db=db,
            query=question,
            top_k=final_top_k,
            category=category,
            department=department
        )

        # ---------------------------------------------------------
        # 2. Apply hybrid re-ranking
        # ---------------------------------------------------------

        if settings.HYBRID_SEARCH and retrieved_chunks:

            retrieved_chunks = HybridReranker.rerank(
                query=question,
                retrieved_chunks=retrieved_chunks,
                top_k=final_top_k
            )

        # ---------------------------------------------------------
        # 3. Stream grounded answer
        # ---------------------------------------------------------

        async for event in self.generator.stream_answer(
            query=question,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history
        ):
            yield event