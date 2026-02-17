"""SQLAlchemy base and model imports."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "role"
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "user"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.role_id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(200))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    role = relationship("Role", back_populates="users")
    actions = relationship("AlertAction", back_populates="user")


class Patient(Base):
    __tablename__ = "patient"
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_ref = Column(String(100))
    display_name = Column(String(200))
    sessions = relationship("Session", back_populates="patient")


class Session(Base):
    __tablename__ = "session"
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patient.patient_id"))
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime(timezone=True))
    source_type = Column(String(50), default="replay")
    status = Column(String(20), default="RUNNING")
    record_name = Column(String(100))
    patient = relationship("Patient", back_populates="sessions")
    predictions = relationship("PredictionBeat", back_populates="session")
    alerts = relationship("Alert", back_populates="session")


class ModelVersion(Base):
    __tablename__ = "model_version"
    model_version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    artifact_uri = Column(String(500))
    metrics_json = Column(JSON)
    deployed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)


class PredictionBeat(Base):
    __tablename__ = "prediction_beat"
    pred_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session.session_id"), nullable=False)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_version.model_version_id"))
    beat_ts_sec = Column(Float, nullable=False)
    pred_class = Column(String(5), nullable=False)
    confidence = Column(Float)
    p_a = Column(Float)
    probs_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    session = relationship("Session", back_populates="predictions")


class Alert(Base):
    __tablename__ = "alert"
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session.session_id"), nullable=False)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_version.model_version_id"))
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_update = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    alert_type = Column(String(5), nullable=False)
    status = Column(String(20), default="NEW")
    severity = Column(Float, default=0.0)
    evidence_json = Column(JSON)
    session = relationship("Session", back_populates="alerts")
    actions = relationship("AlertAction", back_populates="alert")


class AlertAction(Base):
    __tablename__ = "alert_action"
    action_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alert.alert_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False)
    action_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    action_type = Column(String(20), nullable=False)
    reason = Column(Text)
    note = Column(Text)
    alert = relationship("Alert", back_populates="actions")
    user = relationship("User", back_populates="actions")


class SystemSetting(Base):
    __tablename__ = "system_setting"
    setting_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False)
    current_value_json = Column(JSON)
    versions = relationship("SettingVersion", back_populates="setting")


class SettingVersion(Base):
    __tablename__ = "setting_version"
    setting_version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_id = Column(UUID(as_uuid=True), ForeignKey("system_setting.setting_id"), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("user.user_id"))
    changed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    value_json = Column(JSON)
    setting = relationship("SystemSetting", back_populates="versions")
