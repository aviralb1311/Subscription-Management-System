from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.modules.auth.models import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthService:
    @staticmethod
    async def register(
        db: AsyncSession,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
    ):
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        full_name = " ".join(part for part in (first_name, last_name) if part) or None
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User inactive",
            )

        subject = {"sub": str(user.id)}
        return {
            "access_token": create_access_token(data=subject),
            "refresh_token": create_refresh_token(data=subject),
            "token_type": "bearer",
        }

    @staticmethod
    async def refresh(db: AsyncSession, refresh_token: str):
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        subject = {"sub": str(user.id)}
        return {
            "access_token": create_access_token(data=subject),
            "refresh_token": create_refresh_token(data=subject),
            "token_type": "bearer",
        }

    @staticmethod
    async def logout(db: AsyncSession, refresh_token: str):
        # Refresh tokens are stateless JWTs in this implementation. They expire
        # naturally; immediate server-side revocation requires persistent storage.
        return {"message": "Logged out successfully. Discard the refresh token."}
