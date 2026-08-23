from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.models.feedback import Feedback

class AdminService:
    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession) -> Dict[str, Any]:
        # Count Documents
        doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
        chunk_count = (await db.execute(select(func.count(DocumentChunk.id)))).scalar() or 0
        user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
        conv_count = (await db.execute(select(func.count(Conversation.id)))).scalar() or 0
        msg_count = (await db.execute(select(func.count(Message.id)))).scalar() or 0

        # Status distribution
        status_stmt = select(Document.status, func.count(Document.id)).group_by(Document.status)
        status_res = (await db.execute(status_stmt)).all()
        status_counts = {s: cnt for s, cnt in status_res}

        # Category distribution
        cat_stmt = select(Document.category, func.count(Document.id)).group_by(Document.category)
        cat_res = (await db.execute(cat_stmt)).all()
        cat_counts = {c: cnt for c, cnt in cat_res}

        # Feedback stats
        pos_fb = (await db.execute(select(func.count(Feedback.id)).where(Feedback.rating == 1))).scalar() or 0
        neg_fb = (await db.execute(select(func.count(Feedback.id)).where(Feedback.rating == -1))).scalar() or 0

        return {
            "totalDocuments": doc_count,
            "totalChunks": chunk_count,
            "totalUsers": user_count,
            "totalConversations": conv_count,
            "totalQueries": msg_count // 2 if msg_count else 0,
            "documentStatus": status_counts,
            "categories": cat_counts,
            "feedback": {
                "positive": pos_fb,
                "negative": neg_fb,
                "total": pos_fb + neg_fb
            }
        }
