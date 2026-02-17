# API Reference — ECG Real-time CDSS

Base URL: `http://localhost:8000`

## Authentication

### POST `/api/auth/login`
Login and receive JWT token.

**Request Body:**
```json
{ "username": "admin", "password": "admin123" }
```

**Response:**
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

### GET `/api/me`
Get current user profile. Requires `Authorization: Bearer <token>`.

**Response:**
```json
{
  "user_id": "uuid",
  "username": "admin",
  "display_name": "Administrator",
  "role": "admin"
}
```

---

## Sessions

### GET `/api/sessions`
List all sessions.

**Query:** `?status=RUNNING|STOPPED&limit=50&offset=0`

### GET `/api/sessions/{session_id}`
Get session detail.

### POST `/api/sessions/{session_id}/stop`
Stop a running session.

---

## Alerts

### GET `/api/alerts`
List alerts with filters.

**Query:** `?status=NEW|ACK|DISMISSED&session_id=uuid&from=ISO8601&to=ISO8601&limit=50&offset=0`

### GET `/api/alerts/{alert_id}`
Get alert detail with actions.

### POST `/api/alerts/{alert_id}/ack`
Acknowledge an alert.

**Request Body:**
```json
{ "reason": "Confirmed PVC pattern", "note": "Will monitor closely" }
```

### POST `/api/alerts/{alert_id}/dismiss`
Dismiss an alert.

**Request Body:**
```json
{ "reason": "Artifact/noise", "note": "Motion artifact detected" }
```

---

## History

### GET `/api/sessions/{session_id}/predictions`
Get prediction history for a session.

**Query:** `?from=ISO8601&to=ISO8601&limit=1000`

### GET `/api/sessions/{session_id}/alerts`
Get alerts for a session.

---

## Admin — Settings

### GET `/api/admin/settings`
Get all system settings. Requires Admin role.

### PUT `/api/admin/settings`
Update system settings. Requires Admin role.

**Request Body:**
```json
{
  "thr_A": 0.65,
  "V_WINDOW": 10,
  "V_THRESH": 5,
  "COOLDOWN_V": 20,
  "A_WINDOW": 30,
  "A_THRESH": 4,
  "COOLDOWN_A": 45,
  "STREAM_CHUNK_SEC": 1.0,
  "REALTIME_SPEED": 1.0
}
```

---

## Admin — Users

### GET `/api/admin/users`
List all users. Requires Admin role.

### POST `/api/admin/users`
Create a new user. Requires Admin role.

### PUT `/api/admin/users/{user_id}`
Update user. Requires Admin role.

### DELETE `/api/admin/users/{user_id}`
Delete (deactivate) user. Requires Admin role.

---

## Analytics

### GET `/api/analytics/alerts_hourly`
Get alerts per hour.

**Query:** `?from=ISO8601&to=ISO8601&session_id=uuid`

### GET `/api/analytics/summary`
Get summary statistics.

**Query:** `?from=ISO8601&to=ISO8601`

**Response:**
```json
{
  "total_alerts": 42,
  "ack_count": 30,
  "dismiss_count": 8,
  "new_count": 4,
  "dismiss_rate": 0.19,
  "avg_response_time_sec": 12.5
}
```

---

## WebSocket

### WS `/ws/live?session_id={session_id}&token={jwt_token}`

Server pushes 3 message types:

**Waveform:**
```json
{
  "type": "waveform",
  "data": {
    "ts_start": "ISO8601",
    "fs": 360,
    "lead": ["MLII", "V1"],
    "samples": [[...], [...]]
  }
}
```

**Prediction:**
```json
{
  "type": "prediction",
  "data": {
    "beat_ts_sec": 218.24,
    "pred_class": "N",
    "confidence": 0.95,
    "pA": 0.02,
    "probs": {"N": 0.95, "A": 0.02, "V": 0.03}
  }
}
```

**Alert:**
```json
{
  "type": "alert",
  "data": {
    "alert_id": "uuid",
    "alert_type": "V",
    "status": "NEW",
    "severity": 0.85,
    "evidence": { "window_sec": 10, "count": 5, "threshold": 5 }
  }
}
```
