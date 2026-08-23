import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.feedback import Feedback

class FeedbackService:
    @staticmethod
    async def submit_feedback(
        db: AsyncSession,
        message_id: str,
        rating: int,
        user_id: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        fb = Feedback(
            id=str(uuid.uuid4()),
            message_id=message_id,
            user_id=user_id,
            rating=1 if rating > 0 else -1,
            comment=comment,
            created_at=datetime.utcnow()
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)
        return fb.to_dict()
