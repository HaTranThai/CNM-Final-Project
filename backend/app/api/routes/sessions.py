"""Sessions routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.base import Session, PredictionBeat, Alert
from app.schemas.schemas import SessionOut, PredictionOut, AlertOut
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = select(Session).order_by(Session.start_time.desc()).offset(offset).limit(limit)
    if status:
        query = query.where(Session.status == status)
    result = await db.execute(query)
    sessions = result.scalars().all()
    return [
        SessionOut(
            session_id=str(s.session_id),
            patient_id=str(s.patient_id) if s.patient_id else None,
            start_time=str(s.start_time) if s.start_time else None,
            end_time=str(s.end_time) if s.end_time else None,
            source_type=s.source_type,
            status=s.status,
            record_name=s.record_name,
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    result = await db.execute(select(Session).where(Session.session_id == session_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionOut(
        session_id=str(s.session_id),
        patient_id=str(s.patient_id) if s.patient_id else None,
        start_time=str(s.start_time) if s.start_time else None,
        end_time=str(s.end_time) if s.end_time else None,
        source_type=s.source_type,
        status=s.status,
        record_name=s.record_name,
    )


@router.post("/{session_id}/stop")
async def stop_session(session_id: str, db: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    result = await db.execute(select(Session).where(Session.session_id == session_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    s.status = "STOPPED"
    s.end_time = datetime.now(timezone.utc)
    await db.flush()
    return {"detail": "Session stopped"}


@router.get("/{session_id}/predictions", response_model=list[PredictionOut])
async def get_session_predictions(
    session_id: str,
    limit: int = 1000,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await db.execute(
        select(PredictionBeat)
        .where(PredictionBeat.session_id == session_id)
        .order_by(PredictionBeat.beat_ts_sec.desc())
        .limit(limit)
    )
    preds = result.scalars().all()
    return [
        PredictionOut(
            pred_id=str(p.pred_id),
            session_id=str(p.session_id),
            beat_ts_sec=p.beat_ts_sec,
            pred_class=p.pred_class,
            confidence=p.confidence,
            p_a=p.p_a,
            probs_json=p.probs_json,
            created_at=str(p.created_at) if p.created_at else None,
        )
        for p in preds
    ]


@router.get("/{session_id}/alerts", response_model=list[AlertOut])
async def get_session_alerts(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await db.execute(
        select(Alert)
        .where(Alert.session_id == session_id)
        .order_by(Alert.start_time.desc())
    )
    alerts_list = result.scalars().all()
    return [
        AlertOut(
            alert_id=str(a.alert_id),
            session_id=str(a.session_id),
            start_time=str(a.start_time) if a.start_time else None,
            last_update=str(a.last_update) if a.last_update else None,
            alert_type=a.alert_type,
            status=a.status,
            severity=a.severity,
            evidence_json=a.evidence_json,
        )
        for a in alerts_list
    ]
