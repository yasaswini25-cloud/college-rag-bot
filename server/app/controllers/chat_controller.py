from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.chat_service import ChatService
from app.models.user import User

class SendMessageRequest(BaseModel):
    content: str
    conversationId: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None

class RenameConversationRequest(BaseModel):
    title: str

class ChatController:
    def __init__(self):
        self.chat_service = ChatService()

    async def send_message(self, db: AsyncSession, user: User, req: SendMessageRequest):
        return await self.chat_service.send_message(
            db=db,
            user_id=user.id,
            content=req.content,
            conversation_id=req.conversationId,
            category=req.category,
            department=req.department
        )

    async def get_history(self, db: AsyncSession, user: User):
        return await self.chat_service.get_user_conversations(db=db, user_id=user.id)

    async def get_conversation(self, db: AsyncSession, user: User, conversation_id: str):
        return await self.chat_service.get_conversation_messages(db=db, conversation_id=conversation_id, user_id=user.id)

    async def delete_conversation(self, db: AsyncSession, user: User, conversation_id: str):
        return await self.chat_service.delete_conversation(db=db, conversation_id=conversation_id, user_id=user.id)

    async def rename_conversation(self, db: AsyncSession, user: User, conversation_id: str, req: RenameConversationRequest):
        return await self.chat_service.rename_conversation(db=db, conversation_id=conversation_id, user_id=user.id, new_title=req.title)
