from typing import List, Dict, Any

class PromptBuilder:
    """
    Constructs prompts for the College Information Assistant with strict grounding.
    """
    FALLBACK_UNKNOWN_MESSAGE = "I couldn't find reliable information about this in the college knowledge base."

    SYSTEM_PROMPT = """You are the official College Information Assistant for our institution.
Your primary objective is to provide clear, accurate, and completely grounded answers to college-related queries from students, faculty, and visitors.

STRICT OPERATIONAL GUIDELINES:
1. Grounding: Answer ONLY using the provided college knowledge base context below. Do NOT use outside general knowledge or make assumptions.
2. Accuracy: If the answer cannot be directly determined from the provided context, you MUST output:
   "I couldn't find reliable information about this in the college knowledge base."
3. Formatting: Use clean markdown with clear headings, bullet points, and numbered lists where appropriate.
4. Tone: Professional, helpful, concise, and student-friendly.
5. Citations: At the end of your answer, reference the relevant document name(s) and page number(s) from the context.
"""

    QUERY_REWRITE_PROMPT = """Given the following conversation history and a follow-up question from a student, rewrite the follow-up question into a standalone query that contains all necessary context for document retrieval.

Conversation History:
{history}

Follow-up Question: {question}

Standalone Query:"""

    @staticmethod
    def build_rag_prompt(query: str, chunks: List[Dict[str, Any]], conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Builds the complete prompt sent to the LLM.
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            doc_name = chunk.get("document_name", "Unknown Document")
            page_num = chunk.get("page_number", 1)
            content = chunk.get("content", "").strip()
            context_parts.append(
                f"--- SOURCE [{i}]: {doc_name} (Page {page_num}) ---\n{content}"
            )

        context_text = "\n\n".join(context_parts) if context_parts else "NO MATCHING DOCUMENTS FOUND."

        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-4:]  # Last 4 turns
            history_lines = []
            for msg in recent_history:
                role = "Student" if msg.get("role") == "user" else "Assistant"
                history_lines.append(f"{role}: {msg.get('content', '')}")
            history_text = "\n\nPREVIOUS CONVERSATION CONTEXT:\n" + "\n".join(history_lines)

        prompt = f"""KNOWLEDGE BASE CONTEXT:
{context_text}
{history_text}

STUDENT QUESTION:
{query}

ANSWER (grounded strictly in the context above):"""
        return prompt
