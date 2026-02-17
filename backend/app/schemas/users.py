"""Pydantic schemas for users."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    role_id: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[str] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    user_id: str
    username: str
    display_name: str | None
    role_id: str
    role_name: str | None = None
    is_active: bool
    created_at: str | None

    class Config:
        from_attributes = True
