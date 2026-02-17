"""Auth routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.base import User, Role
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse, UserProfile
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    token = create_access_token(data={"sub": str(user.user_id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserProfile)
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).where(Role.role_id == user.role_id))
    role = result.scalar_one_or_none()
    return UserProfile(
        user_id=str(user.user_id),
        username=user.username,
        display_name=user.display_name,
        role=role.name if role else "unknown",
    )
