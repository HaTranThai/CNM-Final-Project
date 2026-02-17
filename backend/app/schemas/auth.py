"""Pydantic schemas for auth."""
from __future__ import annotations
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    user_id: str
    username: str
    display_name: str | None
    role: str

    class Config:
        from_attributes = True
