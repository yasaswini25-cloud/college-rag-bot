from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.services.feedback_service import FeedbackService
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackRequest(BaseModel):
    messageId: str
    rating: int  # 1 or -1
    comment: Optional[str] = None

@router.post("")
async def submit_feedback(
    req: FeedbackRequest,
    user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await FeedbackService.submit_feedback(
        db=db,
        message_id=req.messageId,
        rating=req.rating,
        user_id=user.id,
        comment=req.comment
    )
