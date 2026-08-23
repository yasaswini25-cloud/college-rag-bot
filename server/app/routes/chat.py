from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.controllers.chat_controller import ChatController, SendMessageRequest, RenameConversationRequest
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["Chat"])
controller = ChatController()

@router.post("")
async def send_message(
    req: SendMessageRequest,
    user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await controller.send_message(db, user, req)

@router.get("/history")
async def get_history(
    user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await controller.get_history(db, user)

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await controller.get_conversation(db, user, conversation_id)

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await controller.delete_conversation(db, user, conversation_id)

@router.put("/{conversation_id}")
async def rename_conversation(
    conversation_id: str,
    req: RenameConversationRequest,
    user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await controller.rename_conversation(db, user, conversation_id, req)
