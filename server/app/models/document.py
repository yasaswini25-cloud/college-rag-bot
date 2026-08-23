import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from app.config.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    category = Column(String(100), default="General", nullable=False)  # Admissions, Regulations, Fees, Hostel, Library, Placements, etc.
    department = Column(String(100), default="All", nullable=False)   # CSE, ECE, MECH, General, etc.
    version = Column(String(50), default="1.0", nullable=False)
    file_url = Column(String(500), nullable=True)
    status = Column(String(50), default="PENDING", nullable=False)    # PENDING, PROCESSING, INDEXED, FAILED
    total_chunks = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "category": self.category,
            "department": self.department,
            "version": self.version,
            "file_url": self.file_url,
            "status": self.status,
            "total_chunks": self.total_chunks,
            "file_size_bytes": self.file_size_bytes,
            "uploaded_by": self.uploaded_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
