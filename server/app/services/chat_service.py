import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc
from fastapi import HTTPException
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.feedback import MessageSource
from app.services.rag_service import RAGService

class ChatService:
    def __init__(self):
        self.rag_service = RAGService()

    async def get_user_conversations(self, db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
        )
        result = await db.execute(stmt)
        convs = result.scalars().all()
        return [c.to_dict() for c in convs]

    async def create_conversation(self, db: AsyncSession, user_id: str, title: str = "New Chat") -> Conversation:
        conv = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    async def get_conversation_messages(self, db: AsyncSession, conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
        # Verify conversation belongs to user (or admin)
        conv = await db.get(Conversation, conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        return [m.to_dict() for m in messages]

    async def delete_conversation(self, db: AsyncSession, conversation_id: str, user_id: str) -> bool:
        conv = await db.get(Conversation, conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        if conv.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this conversation.")

        await db.delete(conv)
        await db.commit()
        return True

    async def rename_conversation(self, db: AsyncSession, conversation_id: str, user_id: str, new_title: str) -> Conversation:
        conv = await db.get(Conversation, conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        conv.title = new_title.strip()
        conv.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(conv)
        return conv

    async def send_message(
        self,
        db: AsyncSession,
        user_id: str,
        content: str,
        conversation_id: Optional[str] = None,
        category: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Get or create conversation
        if conversation_id:
            conv = await db.get(Conversation, conversation_id)
            if not conv:
                conv = await self.create_conversation(db, user_id, title=content[:40])
        else:
            conv = await self.create_conversation(db, user_id, title=content[:40])

        # 2. Fetch conversation history for follow-up resolution
        history_msgs = await self.get_conversation_messages(db, conv.id, user_id)
        conv_history = [{"role": m["role"], "content": m["content"]} for m in history_msgs[-6:]]

        # 3. Save User Message
        user_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conv.id,
            role="user",
            content=content,
            created_at=datetime.utcnow()
        )
        db.add(user_msg)
        await db.commit()

        # 4. Perform RAG query
        rag_output = await self.rag_service.query(
            db=db,
            question=content,
            category=category,
            department=department,
            conversation_history=conv_history
        )

        # 5. Save Assistant Message
        assistant_meta = {
            "sources": rag_output.get("sources", []),
            "model": rag_output.get("model", "local"),
            "latency_ms": rag_output.get("latency_ms", 0),
            "grounded": rag_output.get("grounded", False)
        }
        assistant_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conv.id,
            role="assistant",
            content=rag_output.get("answer", ""),
            created_at=datetime.utcnow()
        )
        assistant_msg.set_metadata(assistant_meta)
        db.add(assistant_msg)

        # 6. Save message sources for granular citation auditing
        for s in rag_output.get("sources", []):
            ms = MessageSource(
                id=str(uuid.uuid4()),
                message_id=assistant_msg.id,
                document_id=s.get("documentId"),
                page_number=s.get("page", 1),
                similarity_score=s.get("similarityScore", 0.0),
                created_at=datetime.utcnow()
            )
            db.add(ms)

        # Update conversation timestamp
        conv.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(assistant_msg)

        return {
            "conversationId": conv.id,
            "userMessage": user_msg.to_dict(),
            "assistantMessage": assistant_msg.to_dict(),
            "answer": assistant_msg.content,
            "sources": rag_output.get("sources", []),
            "latency_ms": rag_output.get("latency_ms", 0)
        }
