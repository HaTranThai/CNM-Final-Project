"""User management routes (Admin)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.base import User, Role
from app.core.security import hash_password
from app.schemas.users import UserCreate, UserUpdate, UserOut
from app.api.deps import require_admin

router = APIRouter()


@router.get("", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    out = []
    for u in users:
        role_result = await db.execute(select(Role).where(Role.role_id == u.role_id))
        role = role_result.scalar_one_or_none()
        out.append(UserOut(
            user_id=str(u.user_id),
            username=u.username,
            display_name=u.display_name,
            role_id=str(u.role_id),
            role_name=role.name if role else None,
            is_active=u.is_active,
            created_at=str(u.created_at) if u.created_at else None,
        ))
    return out


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
        role_id=body.role_id,
    )
    db.add(user)
    await db.flush()
    return UserOut(
        user_id=str(user.user_id),
        username=user.username,
        display_name=user.display_name,
        role_id=str(user.role_id),
        is_active=user.is_active,
        created_at=str(user.created_at) if user.created_at else None,
    )


@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: str, body: UserUpdate, db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.display_name is not None:
        user.display_name = body.display_name
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.role_id is not None:
        user.role_id = body.role_id
    if body.password is not None:
        user.password_hash = hash_password(body.password)

    await db.flush()
    return UserOut(
        user_id=str(user.user_id),
        username=user.username,
        display_name=user.display_name,
        role_id=str(user.role_id),
        is_active=user.is_active,
        created_at=str(user.created_at) if user.created_at else None,
    )


@router.delete("/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.flush()
    return {"detail": "User deactivated"}
