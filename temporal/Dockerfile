FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY temporal/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 app

COPY temporal/ /app/temporal/
COPY ai-sre-agent/agent/ /app/agent/

USER 10001:10001

CMD ["python", "-m", "temporal.workers.worker"]
