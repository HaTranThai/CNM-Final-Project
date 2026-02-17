# Runbook — ECG Real-time CDSS

## Prerequisites

- Docker & Docker Compose installed
- MIT-BIH data files (e.g., `223.dat`, `223.hea`, `223.atr`)
- Trained model checkpoint `best_mitbih_v25.pt`

## Setup

### 1. Clone & Configure

```bash
cd ecg-realtime-cdss
cp .env.example .env
# Edit .env if needed (default values work for local dev)
```

### 2. Place Data Files

```bash
# Copy MIT-BIH record files
cp 223.dat 223.hea 223.atr services/replay-producer/data/

# Copy model checkpoint
cp best_mitbih_v25.pt services/inference-service/artifacts/
```

### 3. Build & Start

```bash
docker-compose up --build
```

This starts all services:
- **Kafka** (Zookeeper + Broker) — port 9092
- **PostgreSQL** — port 5432
- **Backend (FastAPI)** — port 8000
- **Frontend (React)** — port 3000
- **Replay Producer** — internal
- **Preprocess Buffer** — internal
- **Inference Service** — internal
- **Alert Engine** — internal

### 4. Wait for Ready

Watch logs for:
```
backend    | INFO: Uvicorn running on http://0.0.0.0:8000
frontend   | Local: http://localhost:3000/
```

### 5. Create Kafka Topics (auto on first start)

Topics are auto-created by the init script. To manually create:
```bash
docker-compose exec kafka bash /scripts/create-topics.sh
```

## Demo Flow

### Step 1: Login
Open http://localhost:3000 → Login with:
- Username: `admin`
- Password: `admin123`

### Step 2: Live Monitor
Navigate to `/live` to see:
- ECG waveform streaming in real-time
- Current prediction badge (N/A/V with confidence)
- Active alerts panel
- Signal quality indicator

### Step 3: Alerts
When the system detects arrhythmia patterns:
- V alert: ≥ 5 PVC beats in 10-second window
- A alert: ≥ 4 PAC beats (pA ≥ thr_A) in 30-second window

Navigate to `/alerts` to:
- View alert list with filters
- Click an alert for details
- **ACK**: Acknowledge with reason/note
- **DISMISS**: Dismiss with reason/note

### Step 4: Analytics
Navigate to `/analytics` to view:
- Alerts per hour chart
- Dismiss rate
- Summary statistics

### Step 5: Admin
Navigate to `/admin/settings` to adjust:
- A-threshold (thr_A)
- Window sizes, thresholds, cooldowns
- Stream speed

Navigate to `/admin/users` to manage user accounts.

## Troubleshooting

### Kafka not ready
Services may restart a few times while Kafka initializes. This is normal.

### No waveform showing
- Check that MIT-BIH data files are in `services/replay-producer/data/`
- Check replay-producer logs: `docker-compose logs replay-producer`

### No predictions
- Check that model checkpoint is in `services/inference-service/artifacts/`
- Check inference-service logs: `docker-compose logs inference-service`

### Database issues
Reset database:
```bash
docker-compose down -v
docker-compose up --build
```

## Stopping

```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop & remove volumes (reset DB)
```
