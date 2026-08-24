import re
from typing import List, Dict, Any, AsyncGenerator

from app.config.settings import settings
from app.rag.prompt import PromptBuilder


class LLMGenerator:
    """
    Generates answers from retrieved context using Gemini, OpenAI,
    or local synthesis fallback.

    Includes a grounding gate to prevent the LLM from answering
    when the retrieved context is not sufficiently relevant.
    """

    def __init__(self, provider: str = None):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

        # Minimum confidence required before sending context to the LLM.
        self.grounding_threshold = getattr(
            settings,
            "GROUNDING_THRESHOLD",
            0.35
        )

    # ---------------------------------------------------------
    # Grounding check
    # ---------------------------------------------------------

    def _is_grounded(
        self,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> bool:
        """
        Determines whether the retrieved context is strong enough
        to answer the question.

        The retriever/reranker produces similarity scores. We use
        the highest available score as the grounding signal.
        """

        if not retrieved_chunks:
            return False

        scores = []

        for chunk in retrieved_chunks:
            score = chunk.get(
                "hybrid_score",
                chunk.get(
                    "similarity_score",
                    0.0
                )
            )

            try:
                scores.append(float(score))
            except (TypeError, ValueError):
                continue

        if not scores:
            return False

        best_score = max(scores)

        return best_score >= self.grounding_threshold

    # ---------------------------------------------------------
    # Non-streaming generation
    # ---------------------------------------------------------

    async def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete grounded answer.
        """

        # -----------------------------------------------------
        # 1. No retrieval result
        # -----------------------------------------------------

        if not retrieved_chunks:
            return {
                "answer": PromptBuilder.FALLBACK_UNKNOWN_MESSAGE,
                "sources": [],
                "model": "rule-based-guardrail",
                "grounded": False
            }

        # -----------------------------------------------------
        # 2. Grounding gate
        # -----------------------------------------------------

        if not self._is_grounded(retrieved_chunks):
            return {
                "answer": PromptBuilder.FALLBACK_UNKNOWN_MESSAGE,
                "sources": self._format_sources(retrieved_chunks),
                "model": "grounding-guardrail",
                "grounded": False
            }

        # -----------------------------------------------------
        # 3. Build grounded prompt
        # -----------------------------------------------------

        prompt = PromptBuilder.build_rag_prompt(
            query,
            retrieved_chunks,
            conversation_history
        )

        sources = self._format_sources(retrieved_chunks)

        # -----------------------------------------------------
        # 4. Gemini
        # -----------------------------------------------------

        if self.gemini_key and (
            self.provider == "gemini"
            or self.provider == "auto"
        ):
            try:
                import google.generativeai as genai

                genai.configure(
                    api_key=self.gemini_key
                )

                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=PromptBuilder.SYSTEM_PROMPT
                )

                response = model.generate_content(prompt)

                answer_text = (
                    response.text.strip()
                    if response.text
                    else PromptBuilder.FALLBACK_UNKNOWN_MESSAGE
                )

                return {
                    "answer": answer_text,
                    "sources": sources,
                    "model": "gemini-1.5-flash",
                    "grounded": True
                }

            except Exception as e:
                print(
                    f"[LLMGenerator] Gemini error: {e}. "
                    f"Falling back..."
                )

        # -----------------------------------------------------
        # 5. OpenAI
        # -----------------------------------------------------

        if self.openai_key and (
            self.provider == "openai"
            or self.provider == "auto"
        ):
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(
                    api_key=self.openai_key
                )

                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": PromptBuilder.SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.2
                )

                answer_text = (
                    response.choices[0]
                    .message.content
                    .strip()
                )

                return {
                    "answer": answer_text,
                    "sources": sources,
                    "model": "gpt-4o-mini",
                    "grounded": True
                }

            except Exception as e:
                print(
                    f"[LLMGenerator] OpenAI error: {e}. "
                    f"Falling back..."
                )

        # -----------------------------------------------------
        # 6. Local grounded synthesis
        # -----------------------------------------------------

        local_answer = self._local_grounded_synthesis(
            query,
            retrieved_chunks
        )

        return {
            "answer": local_answer,
            "sources": sources,
            "model": "local-rag-synthesizer",
            "grounded": True
        }

    # ---------------------------------------------------------
    # Streaming generation
    # ---------------------------------------------------------

    async def stream_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams grounded response tokens asynchronously.
        """

        # -----------------------------------------------------
        # 1. No retrieved context
        # -----------------------------------------------------

        if not retrieved_chunks:
            yield {
                "type": "token",
                "content": PromptBuilder.FALLBACK_UNKNOWN_MESSAGE
            }

            yield {
                "type": "sources",
                "sources": []
            }

            yield {
                "type": "done"
            }

            return

        # -----------------------------------------------------
        # 2. Grounding gate
        # -----------------------------------------------------

        if not self._is_grounded(retrieved_chunks):
            yield {
                "type": "token",
                "content": PromptBuilder.FALLBACK_UNKNOWN_MESSAGE
            }

            yield {
                "type": "sources",
                "sources": self._format_sources(
                    retrieved_chunks
                )
            }

            yield {
                "type": "done"
            }

            return

        # -----------------------------------------------------
        # 3. Prepare grounded request
        # -----------------------------------------------------

        sources = self._format_sources(
            retrieved_chunks
        )

        prompt = PromptBuilder.build_rag_prompt(
            query,
            retrieved_chunks,
            conversation_history
        )

        # -----------------------------------------------------
        # 4. Gemini streaming
        # -----------------------------------------------------

        if self.gemini_key and (
            self.provider == "gemini"
            or self.provider == "auto"
        ):
            try:
                import google.generativeai as genai

                genai.configure(
                    api_key=self.gemini_key
                )

                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=PromptBuilder.SYSTEM_PROMPT
                )

                response = model.generate_content(
                    prompt,
                    stream=True
                )

                for chunk in response:
                    if chunk.text:
                        yield {
                            "type": "token",
                            "content": chunk.text
                        }

                yield {
                    "type": "sources",
                    "sources": sources
                }

                yield {
                    "type": "done"
                }

                return

            except Exception as e:
                print(
                    f"[LLMGenerator] Gemini streaming error: "
                    f"{e}. Falling back..."
                )

        # -----------------------------------------------------
        # 5. Local streaming fallback
        # -----------------------------------------------------

        full_res = await self.generate_answer(
            query,
            retrieved_chunks,
            conversation_history
        )

        answer = full_res.get("answer", "")

        words = answer.split(" ")

        for i, word in enumerate(words):
            token = word

            if i < len(words) - 1:
                token += " "

            yield {
                "type": "token",
                "content": token
            }

        yield {
            "type": "sources",
            "sources": sources
        }

        yield {
            "type": "done"
        }

    # ---------------------------------------------------------
    # Local grounded synthesis
    # ---------------------------------------------------------

    def _local_grounded_synthesis(
        self,
        query: str,
        chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Creates a simple extractive answer using only retrieved
        college-document content.
        """

        if not chunks:
            return PromptBuilder.FALLBACK_UNKNOWN_MESSAGE

        query_words = set(
            re.findall(
                r"\w+",
                query.lower()
            )
        )

        best_sentences = []

        for chunk in chunks[:3]:

            content = chunk.get(
                "content",
                ""
            )

            doc_name = chunk.get(
                "document_name",
                "College Document"
            )

            page_num = chunk.get(
                "page_number",
                1
            )

            lines = [
                line.strip()
                for line in content.split("\n")
                if line.strip()
            ]

            for line in lines:

                line_lower = line.lower()

                matches = sum(
                    1
                    for word in query_words
                    if (
                        len(word) > 2
                        and word in line_lower
                    )
                )

                if matches > 0:
                    best_sentences.append(
                        (
                            matches,
                            line,
                            doc_name,
                            page_num
                        )
                    )

        # -----------------------------------------------------
        # Nothing matched strongly
        # -----------------------------------------------------

        if not best_sentences:

            top = chunks[0]

            return (
                f"According to **"
                f"{top.get('document_name')}"
                f"** (Page "
                f"{top.get('page_number')}"
                f"):\n\n"
                f"{top.get('content')}"
            )

        # -----------------------------------------------------
        # Sort by query-term matches
        # -----------------------------------------------------

        best_sentences.sort(
            key=lambda x: x[0],
            reverse=True
        )

        top_lines = [
            item[1]
            for item in best_sentences[:6]
        ]

        # -----------------------------------------------------
        # Remove duplicates
        # -----------------------------------------------------

        seen = set()
        deduped = []

        for line in top_lines:

            if line not in seen:
                seen.add(line)
                deduped.append(line)

        formatted_lines = []

        for line in deduped:

            if (
                not line.startswith("Section")
                and not line.startswith("Chapter")
                and not line.startswith("-")
                and not line.startswith("•")
            ):
                formatted_lines.append(
                    f"• {line}"
                )
            else:
                formatted_lines.append(line)

        formatted_body = "\n\n".join(
            formatted_lines
        )

        top_doc = chunks[0]

        return (
            f"Based on the official **"
            f"{top_doc.get('document_name')}"
            f"** (Page "
            f"{top_doc.get('page_number')}"
            f"):\n\n"
            f"{formatted_body}"
        )

    # ---------------------------------------------------------
    # Source formatting
    # ---------------------------------------------------------

    def _format_sources(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        sources = []
        seen = set()

        for chunk in chunks:

            key = (
                chunk.get("document_id"),
                chunk.get("page_number")
            )

            if key in seen:
                continue

            seen.add(key)

            content = chunk.get(
                "content",
                ""
            )

            sources.append({
                "documentId": chunk.get(
                    "document_id"
                ),

                "documentName": (
                    chunk.get("document_name")
                    or chunk.get("filename")
                ),

                "filename": chunk.get(
                    "filename"
                ),

                "page": chunk.get(
                    "page_number",
                    1
                ),

                "similarityScore": chunk.get(
                    "similarity_score",
                    0.0
                ),

                "category": chunk.get(
                    "category",
                    "General"
                ),

                "department": chunk.get(
                    "department",
                    "All"
                ),

                "snippet": (
                    content[:180]
                    + (
                        "..."
                        if len(content) > 180
                        else ""
                    )
                )
            })

        return sources