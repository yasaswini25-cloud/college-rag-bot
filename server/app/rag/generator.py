import os
import re
from typing import List, Dict, Any, AsyncGenerator
from app.config.settings import settings
from app.rag.prompt import PromptBuilder

class LLMGenerator:
    """
    Generates answers from retrieved context using Gemini, OpenAI, or local synthesis fallback.
    Supports streaming and non-streaming responses.
    """
    def __init__(self, provider: str = None):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    async def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Non-streaming generation returning complete answer, sources, and metadata.
        """
        # If no chunks were retrieved, handle fallback immediately
        if not retrieved_chunks:
            return {
                "answer": PromptBuilder.FALLBACK_UNKNOWN_MESSAGE,
                "sources": [],
                "model": "rule-based-guardrail",
                "grounded": False
            }

        prompt = PromptBuilder.build_rag_prompt(query, retrieved_chunks, conversation_history)
        sources = self._format_sources(retrieved_chunks)

        # 1. Try Gemini
        if self.gemini_key and (self.provider == "gemini" or self.provider == "auto"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=PromptBuilder.SYSTEM_PROMPT
                )
                response = model.generate_content(prompt)
                answer_text = response.text.strip() if response.text else PromptBuilder.FALLBACK_UNKNOWN_MESSAGE
                return {
                    "answer": answer_text,
                    "sources": sources,
                    "model": "gemini-1.5-flash",
                    "grounded": True
                }
            except Exception as e:
                print(f"[LLMGenerator] Gemini error: {e}. Falling back...")

        # 2. Try OpenAI
        if self.openai_key and (self.provider == "openai" or self.provider == "auto"):
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.openai_key)
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": PromptBuilder.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                answer_text = response.choices[0].message.content.strip()
                return {
                    "answer": answer_text,
                    "sources": sources,
                    "model": "gpt-4o-mini",
                    "grounded": True
                }
            except Exception as e:
                print(f"[LLMGenerator] OpenAI error: {e}. Falling back...")

        # 3. Local Extractive Synthesis Fallback
        local_answer = self._local_grounded_synthesis(query, retrieved_chunks)
        return {
            "answer": local_answer,
            "sources": sources,
            "model": "local-rag-synthesizer",
            "grounded": True
        }

    async def stream_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams response tokens asynchronously.
        """
        if not retrieved_chunks:
            yield {"type": "token", "content": PromptBuilder.FALLBACK_UNKNOWN_MESSAGE}
            yield {"type": "sources", "sources": []}
            yield {"type": "done"}
            return

        sources = self._format_sources(retrieved_chunks)
        prompt = PromptBuilder.build_rag_prompt(query, retrieved_chunks, conversation_history)

        # 1. Try Gemini Streaming
        if self.gemini_key and (self.provider == "gemini" or self.provider == "auto"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=PromptBuilder.SYSTEM_PROMPT
                )
                response = model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield {"type": "token", "content": chunk.text}
                yield {"type": "sources", "sources": sources}
                yield {"type": "done"}
                return
            except Exception as e:
                print(f"[LLMGenerator] Gemini streaming error: {e}. Falling back to local stream...")

        # 2. Local Streaming Simulation
        full_res = await self.generate_answer(query, retrieved_chunks, conversation_history)
        answer = full_res.get("answer", "")
        
        # Stream word by word for natural UI rendering
        words = answer.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            yield {"type": "token", "content": token}
        
        yield {"type": "sources", "sources": sources}
        yield {"type": "done"}

    def _local_grounded_synthesis(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Synthesizes a structured response from retrieved chunks when external LLM API key is not configured.
        """
        if not chunks:
            return PromptBuilder.FALLBACK_UNKNOWN_MESSAGE

        # Filter most relevant sentences matching query terms
        query_words = set(re.findall(r"\w+", query.lower()))
        best_sentences = []

        for chunk in chunks[:3]:
            content = chunk.get("content", "")
            doc_name = chunk.get("document_name", "College Document")
            page_num = chunk.get("page_number", 1)

            # Split into sentences or lines
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            for line in lines:
                line_lower = line.lower()
                matches = sum(1 for w in query_words if len(w) > 2 and w in line_lower)
                if matches > 0:
                    best_sentences.append((matches, line, doc_name, page_num))

        if not best_sentences:
            # Output the top chunk cleanly
            top = chunks[0]
            return f"According to **{top.get('document_name')}** (Page {top.get('page_number')}):\n\n{top.get('content')}"

        # Sort by relevance matches
        best_sentences.sort(key=lambda x: x[0], reverse=True)
        top_lines = [item[1] for item in best_sentences[:6]]
        
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for line in top_lines:
            if line not in seen:
                seen.add(line)
                deduped.append(line)

        formatted_body = "\n\n".join([f"• {l}" if not l.startswith("Section") and not l.startswith("Chapter") and not l.startswith("-") and not l.startswith("•") else l for l in deduped])
        top_doc = chunks[0]
        
        return f"Based on the official **{top_doc.get('document_name')}** (Page {top_doc.get('page_number')}):\n\n{formatted_body}"

    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        seen = set()
        for c in chunks:
            key = (c.get("document_id"), c.get("page_number"))
            if key in seen:
                continue
            seen.add(key)
            sources.append({
                "documentId": c.get("document_id"),
                "documentName": c.get("document_name") or c.get("filename"),
                "filename": c.get("filename"),
                "page": c.get("page_number", 1),
                "similarityScore": c.get("similarity_score", 0.0),
                "category": c.get("category", "General"),
                "department": c.get("department", "All"),
                "snippet": c.get("content", "")[:180] + ("..." if len(c.get("content", "")) > 180 else "")
            })
        return sources
