import os
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config.settings import settings
from app.config.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Fallback to sha256 check
            h = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
            return h == hashed_password

    @staticmethod
    def get_password_hash(password: str) -> str:
        try:
            return pwd_context.hash(password)
        except Exception:
            return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def register_user(db: AsyncSession, name: str, email: str, password: str, role: str = "STUDENT") -> Dict[str, Any]:
        email_clean = email.strip().lower()
        stmt = select(User).where(User.email == email_clean)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        new_user = User(
            id=str(uuid.uuid4()),
            name=name.strip(),
            email=email_clean,
            password_hash=AuthService.get_password_hash(password),
            role=role.upper() if role.upper() in ["ADMIN", "STUDENT"] else "STUDENT",
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        token = AuthService.create_access_token({"sub": new_user.id, "email": new_user.email, "role": new_user.role})
        return {
            "user": new_user.to_dict(),
            "token": token
        }

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        stmt = select(User).where(User.email == email_clean)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user or not AuthService.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        user.last_login = datetime.utcnow()
        await db.commit()

        token = AuthService.create_access_token({"sub": user.id, "email": user.email, "role": user.role})
        return {
            "user": user.to_dict(),
            "token": token
        }

    @staticmethod
    async def get_current_user(
        token: Optional[str] = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials required."
            )
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")

        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    @staticmethod
    async def require_admin(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required."
            )
        return current_user
