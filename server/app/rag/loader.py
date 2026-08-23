import os
import re
from typing import List, Dict, Any

class DocumentLoader:
    """
    Extracts text and page numbers from PDF, DOCX, TXT, and Markdown files.
    """
    @staticmethod
    def load(file_path: str) -> List[Dict[str, Any]]:
        """
        Returns a list of dicts: [{"page_number": int, "text": str}]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return DocumentLoader._load_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return DocumentLoader._load_docx(file_path)
        elif ext in [".txt", ".md"]:
            return DocumentLoader._load_text(file_path)
        else:
            # Attempt plain text read as fallback
            return DocumentLoader._load_text(file_path)

    @staticmethod
    def _load_pdf(file_path: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                text = page.get_text("text")
                cleaned_text = DocumentLoader._clean_text(text)
                if cleaned_text:
                    pages.append({
                        "page_number": page_idx + 1,
                        "text": cleaned_text
                    })
            doc.close()
        except ImportError:
            # Fallback if PyMuPDF not available
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                pages.append({"page_number": 1, "text": DocumentLoader._clean_text(f.read())})
        return pages

    @staticmethod
    def _load_docx(file_path: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            
            # Group into synthetic pages of ~500 words
            text_block = "\n".join(full_text)
            words = text_block.split()
            page_size = 400
            for i in range(0, max(len(words), 1), page_size):
                page_words = words[i:i+page_size]
                pages.append({
                    "page_number": (i // page_size) + 1,
                    "text": DocumentLoader._clean_text(" ".join(page_words))
                })
        except Exception:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                pages.append({"page_number": 1, "text": DocumentLoader._clean_text(f.read())})
        return pages

    @staticmethod
    def _load_text(file_path: str) -> List[Dict[str, Any]]:
        pages = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Check if text contains explicit page markers like "Page X" or "CHAPTER"
        paragraphs = content.split("\n\n")
        current_page_text = []
        page_num = 1
        current_len = 0

        for para in paragraphs:
            para_clean = para.strip()
            if not para_clean:
                continue
            
            # Start new page on major section headers or ~2000 chars
            if (para_clean.startswith("CHAPTER") or para_clean.startswith("Section") or current_len > 2500) and current_page_text:
                pages.append({
                    "page_number": page_num,
                    "text": DocumentLoader._clean_text("\n\n".join(current_page_text))
                })
                page_num += 1
                current_page_text = [para_clean]
                current_len = len(para_clean)
            else:
                current_page_text.append(para_clean)
                current_len += len(para_clean)

        if current_page_text:
            pages.append({
                "page_number": page_num,
                "text": DocumentLoader._clean_text("\n\n".join(current_page_text))
            })

        if not pages:
            pages.append({"page_number": 1, "text": DocumentLoader._clean_text(content)})

        return pages

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        # Remove repeated whitespace and null bytes
        text = text.replace("\x00", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
