import re
from typing import List, Dict, Any

class RecursiveTextSplitter:
    """
    Splits text into chunks of 500-800 tokens with 50-100 token overlap,
    preserving page numbers and sentence boundaries.
    """
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 80):
        # 1 token approx 4 characters
        self.chunk_char_size = chunk_size * 4
        self.chunk_char_overlap = chunk_overlap * 4
        self.separators = ["\n\n", "\n", ". ", "; ", ", ", " "]

    def split_pages(self, pages: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Takes pages [{"page_number": 1, "text": "..."}] and splits them into chunks.
        """
        chunks = []
        global_chunk_idx = 0

        for page in pages:
            page_num = page.get("page_number", 1)
            text = page.get("text", "").strip()
            if not text:
                continue

            page_chunks = self._split_text(text)
            for chunk_text in page_chunks:
                if len(chunk_text.strip()) < 20:
                    continue
                
                chunk_meta = {
                    **(metadata or {}),
                    "page_number": page_num,
                    "chunk_index": global_chunk_idx,
                    "char_count": len(chunk_text),
                    "approx_tokens": len(chunk_text) // 4
                }
                chunks.append({
                    "chunk_index": global_chunk_idx,
                    "content": chunk_text.strip(),
                    "page_number": page_num,
                    "metadata": chunk_meta
                })
                global_chunk_idx += 1

        return chunks

    def _split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_char_size:
            return [text]

        splits = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_char_size

            if end >= text_len:
                splits.append(text[start:])
                break

            # Find best separator before end
            best_split = -1
            chunk_candidate = text[start:end]

            for sep in self.separators:
                pos = chunk_candidate.rfind(sep)
                if pos != -1 and pos > (self.chunk_char_size // 2):
                    best_split = start + pos + len(sep)
                    break

            if best_split == -1 or best_split <= start:
                best_split = end

            splits.append(text[start:best_split])
            start = max(best_split - self.chunk_char_overlap, start + 1)

        return splits
