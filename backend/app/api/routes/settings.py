"""Settings routes (Admin)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.base import SystemSetting, SettingVersion, User
from app.schemas.schemas import SettingsUpdate, SettingOut
from app.api.deps import require_admin

router = APIRouter()


@router.get("", response_model=list[SettingOut])
async def get_settings(db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    result = await db.execute(select(SystemSetting).order_by(SystemSetting.key))
    settings_list = result.scalars().all()
    return [
        SettingOut(key=s.key, value=s.current_value_json)
        for s in settings_list
    ]


@router.put("")
async def update_settings(
    body: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No settings to update")

    updated = []
    for key, value in updates.items():
        result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.current_value_json = value
            # Create audit version
            version = SettingVersion(
                setting_id=setting.setting_id,
                changed_by=admin.user_id,
                value_json=value,
            )
            db.add(version)
            updated.append(key)

    await db.flush()
    return {"detail": f"Updated settings: {updated}"}
