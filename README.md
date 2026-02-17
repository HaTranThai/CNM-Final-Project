# ECG Real-time Clinical Decision Support System (CDSS)

Real-time AI-powered arrhythmia detection from ECG signals using MIT-BIH Arrhythmia Database.

## Architecture

```
MIT-BIH Files → Replay Producer → Kafka → Preprocess Buffer → Inference (PyTorch) → Alert Engine → FastAPI (WS) → React UI
```

## Quick Start

```bash
# 1. Copy your model checkpoint
cp best_mitbih_v25.pt services/inference-service/artifacts/

# 2. Copy MIT-BIH data (e.g., record 223)
cp 223.dat 223.hea 223.atr services/replay-producer/data/

# 3. Copy .env
cp .env.example .env

# 4. Start everything
docker-compose up --build
```

Open http://localhost:3000 → Login with `admin` / `admin123`

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React + Vite + Ant Design |
| Backend | 8000 | FastAPI REST + WebSocket |
| Kafka | 9092 | Message broker |
| Postgres | 5432 | Database |
| Replay Producer | — | MIT-BIH ECG stream simulator |
| Preprocess Buffer | — | Waveform processing |
| Inference Service | — | PyTorch CNN inference |
| Alert Engine | — | Clinical alert rules |

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Runbook](docs/runbook.md)
- Diagrams: `docs/diagrams/` (use case, ERD, class)

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Ant Design, ECharts, TanStack Query
- **Backend**: FastAPI, SQLAlchemy 2.0, Alembic, JWT Auth
- **Services**: Python, PyTorch, WFDB, NumPy, SciPy
- **Infra**: Docker Compose, Kafka, PostgreSQL
