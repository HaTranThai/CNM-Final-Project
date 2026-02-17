FROM python:3.11-slim

WORKDIR /app

COPY common/src /app/common
COPY alert-engine-service/pyproject.toml .
RUN pip install --no-cache-dir .

COPY alert-engine-service/src/ /app/src/

ENV PYTHONPATH=/app:/app/common
CMD ["python", "-m", "src.main"]
