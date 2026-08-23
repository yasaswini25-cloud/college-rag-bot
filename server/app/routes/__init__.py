from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router
from app.routes.rag import router as rag_router
from app.routes.admin import router as admin_router
from app.routes.feedback import router as feedback_router
from app.routes.health import router as health_router

__all__ = [
    "auth_router",
    "chat_router",
    "documents_router",
    "rag_router",
    "admin_router",
    "feedback_router",
    "health_router"
]
