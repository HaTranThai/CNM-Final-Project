FROM python:3.11-slim

WORKDIR /app

COPY common/src /app/common
COPY preprocess-buffer-service/pyproject.toml .
RUN pip install --no-cache-dir .

COPY preprocess-buffer-service/src/ /app/src/

ENV PYTHONPATH=/app:/app/common
CMD ["python", "-m", "src.main"]
