import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.config.database import AsyncSessionLocal
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.rag.loader import DocumentLoader
from app.rag.splitter import RecursiveTextSplitter
from app.rag.embeddings import EmbeddingGenerator
from app.config.settings import settings

class ProcessingService:
    @staticmethod
    async def process_document(document_id: str):
        """
        Runs the end-to-end ingestion pipeline:
        Extraction -> Cleaning -> Chunking -> Embedding -> Vector Storage
        """
        async with AsyncSessionLocal() as db:
            doc = await db.get(Document, document_id)
            if not doc:
                print(f"[ProcessingService] Document {document_id} not found.")
                return

            try:
                doc.status = "PROCESSING"
                await db.commit()

                file_path = doc.file_url
                if not file_path or not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found at path: {file_path}")

                # 1. Text Extraction
                pages = DocumentLoader.load(file_path)
                if not pages:
                    raise ValueError("No extractable text found in the document.")

                # 2. Chunking
                splitter = RecursiveTextSplitter(
                    chunk_size=settings.CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP
                )
                metadata = {
                    "document_id": doc.id,
                    "title": doc.title,
                    "filename": doc.filename,
                    "category": doc.category,
                    "department": doc.department,
                    "version": doc.version
                }
                chunks = splitter.split_pages(pages, metadata=metadata)
                if not chunks:
                    raise ValueError("Failed to create text chunks from extracted pages.")

                # 3. Clean any existing chunks for this document
                await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))

                # 4. Generate Embeddings in batch
                embedder = EmbeddingGenerator()
                chunk_texts = [c["content"] for c in chunks]
                embeddings = await embedder.get_embeddings_batch(chunk_texts)

                # 5. Save Chunks to Database
                chunk_records = []
                for i, c in enumerate(chunks):
                    emb_list = embeddings[i] if i < len(embeddings) else []
                    chunk_obj = DocumentChunk(
                        id=str(uuid.uuid4()),
                        document_id=doc.id,
                        chunk_index=c["chunk_index"],
                        content=c["content"],
                        page_number=c["page_number"],
                        metadata_json=json.dumps(c["metadata"]),
                        created_at=datetime.utcnow()
                    )
                    chunk_obj.set_embedding(emb_list)
                    chunk_records.append(chunk_obj)

                db.add_all(chunk_records)

                # 6. Update Document Status
                doc.status = "INDEXED"
                doc.total_chunks = len(chunk_records)
                doc.updated_at = datetime.utcnow()
                await db.commit()
                print(f"[ProcessingService] Successfully indexed '{doc.title}' with {len(chunk_records)} chunks.")

            except Exception as e:
                print(f"[ProcessingService] Error processing document {document_id}: {e}")
                doc.status = "FAILED"
                doc.updated_at = datetime.utcnow()
                await db.commit()
