FROM python:3.11-slim

WORKDIR /app

COPY common/src /app/common
COPY replay-producer/pyproject.toml .
RUN pip install --no-cache-dir .

COPY replay-producer/src/ /app/src/

ENV PYTHONPATH=/app:/app/common
CMD ["python", "-m", "src.main"]
