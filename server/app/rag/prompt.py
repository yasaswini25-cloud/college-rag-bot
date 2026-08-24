from typing import List, Dict, Any


class PromptBuilder:
    """
    Constructs prompts for the College Information Assistant
    with strict grounding in the college knowledge base.
    """

    FALLBACK_UNKNOWN_MESSAGE = (
        "I couldn't find reliable information about this in the college knowledge base."
    )

    SYSTEM_PROMPT = """You are the official College Information Assistant for our institution.

Your primary objective is to provide clear, accurate, and completely grounded answers using ONLY the retrieved college knowledge base context.

STRICT OPERATIONAL GUIDELINES:

1. GROUNDING:
   Answer ONLY from the information explicitly present in the provided knowledge base context.
   Do NOT use outside knowledge, general knowledge, assumptions, or prior knowledge.

2. INSUFFICIENT CONTEXT:
   If the provided context does not contain enough information to answer the question, respond exactly with:
   "I couldn't find reliable information about this in the college knowledge base."

3. IRRELEVANT CONTEXT:
   Do not force an answer from context merely because some words are similar to the question.
   If the retrieved documents are not relevant to the specific question, use the fallback response.

4. OTHER INSTITUTIONS:
   If the question asks about another college, university, organization, or institution and the provided context does not contain information about it, do not answer using general knowledge.
   Use the fallback response.

5. NO HALLUCINATION:
   Never invent facts, numbers, dates, fees, policies, eligibility criteria, or procedures that are not explicitly present in the context.

6. ANSWER QUALITY:
   When the context contains the answer, provide a concise and direct response.
   Do not include unrelated information from the retrieved chunks.

7. FORMATTING:
   Use clean markdown with clear headings, bullet points, and numbered lists where appropriate.

8. TONE:
   Be professional, helpful, concise, and student-friendly.

9. CITATIONS:
   Reference the relevant document name and page number from the provided context.
   Do not cite documents or pages that do not support the answer.
"""

    QUERY_REWRITE_PROMPT = """Given the following conversation history and a follow-up question from a student, rewrite the follow-up question into a standalone query that contains all necessary context for document retrieval.

Conversation History:
{history}

Follow-up Question: {question}

Standalone Query:"""

    @staticmethod
    def build_rag_prompt(
        query: str,
        chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Builds the complete prompt sent to the LLM.
        """

        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            doc_name = chunk.get("document_name", "Unknown Document")
            page_num = chunk.get("page_number", 1)
            content = chunk.get("content", "").strip()

            context_parts.append(
                f"--- SOURCE [{i}]: {doc_name} (Page {page_num}) ---\n"
                f"{content}"
            )

        context_text = (
            "\n\n".join(context_parts)
            if context_parts
            else "NO MATCHING DOCUMENTS FOUND."
        )

        history_text = ""

        if conversation_history:
            recent_history = conversation_history[-4:]
            history_lines = []

            for msg in recent_history:
                role = (
                    "Student"
                    if msg.get("role") == "user"
                    else "Assistant"
                )

                history_lines.append(
                    f"{role}: {msg.get('content', '')}"
                )

            history_text = (
                "\n\nPREVIOUS CONVERSATION CONTEXT:\n"
                + "\n".join(history_lines)
            )

        prompt = f"""KNOWLEDGE BASE CONTEXT:
{context_text}
{history_text}

STUDENT QUESTION:
{query}

IMPORTANT:
Answer ONLY using the knowledge base context above.
If the context does not contain enough information to answer the question,
respond exactly with:

"I couldn't find reliable information about this in the college knowledge base."

Do not use outside knowledge or make assumptions.

ANSWER:
"""

        return prompt