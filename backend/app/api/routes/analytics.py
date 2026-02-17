"""Analytics routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.db.session import get_db
from app.db.base import Alert
from app.schemas.schemas import AnalyticsSummary
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/alerts_hourly")
async def alerts_hourly(
    session_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = text("""
        SELECT date_trunc('hour', start_time) as hour, alert_type, COUNT(*) as count
        FROM alert
        WHERE start_time >= NOW() - INTERVAL '24 hours'
        GROUP BY hour, alert_type
        ORDER BY hour DESC
    """)
    result = await db.execute(query)
    rows = result.fetchall()
    return [
        {"hour": str(r[0]), "alert_type": r[1], "count": r[2]}
        for r in rows
    ]


@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    total_result = await db.execute(select(func.count(Alert.alert_id)))
    total = total_result.scalar() or 0

    ack_result = await db.execute(select(func.count(Alert.alert_id)).where(Alert.status == "ACK"))
    ack_count = ack_result.scalar() or 0

    dismiss_result = await db.execute(select(func.count(Alert.alert_id)).where(Alert.status == "DISMISSED"))
    dismiss_count = dismiss_result.scalar() or 0

    new_result = await db.execute(select(func.count(Alert.alert_id)).where(Alert.status == "NEW"))
    new_count = new_result.scalar() or 0

    dismiss_rate = dismiss_count / total if total > 0 else 0.0

    return AnalyticsSummary(
        total_alerts=total,
        ack_count=ack_count,
        dismiss_count=dismiss_count,
        new_count=new_count,
        dismiss_rate=round(dismiss_rate, 3),
        avg_response_time_sec=None,
    )
