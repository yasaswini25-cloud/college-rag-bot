import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from app.config.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, default=1, nullable=False)
    embedding = Column(Text, nullable=True)  # JSON-encoded array of floats for broad compatibility
    metadata_json = Column(Text, nullable=True)  # JSON object storing category, dept, tags, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def get_embedding(self):
        if not self.embedding:
            return []
        try:
            return json.loads(self.embedding)
        except Exception:
            return []

    def set_embedding(self, emb_list):
        self.embedding = json.dumps(emb_list)

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "page_number": self.page_number,
            "metadata": json.loads(self.metadata_json) if self.metadata_json else {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
