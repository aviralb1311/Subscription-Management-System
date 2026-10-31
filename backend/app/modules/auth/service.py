from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.modules.auth.models import User, Role, RefreshToken
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, email: str, password: str, first_name: str = None, last_name: str = None):
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        hashed_password = get_password_hash(password)
        user = User(email=email, password_hash=hashed_password, first_name=first_name, last_name=last_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def login(db: AsyncSession, email: str, password: str):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
        
        user.last_login_at = datetime.utcnow()
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        refresh_token_db = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        )
        db.add(refresh_token_db)
        await db.commit()
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
    @staticmethod
    async def refresh(db: AsyncSession, refresh_token: str):
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
        result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token, RefreshToken.is_revoked == False))
        token_db = result.scalar_one_or_none()
        if not token_db or token_db.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        
        token_db.is_revoked = True
        user_id = payload.get("sub")
        access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        new_refresh_token_db = RefreshToken(
            user_id=token_db.user_id,
            token=new_refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        )
        db.add(new_refresh_token_db)
        await db.commit()
        
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
    
    @staticmethod
    async def logout(db: AsyncSession, refresh_token: str):
        result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
        token_db = result.scalar_one_or_none()
        if token_db:
            token_db.is_revoked = True
            await db.commit()
        return {"message": "Logged out successfully"}
