import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("sample-api")

REQUEST_COUNT = Counter(
    "sample_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "sample_api_request_duration_seconds",
    "API request duration in seconds",
    ["endpoint"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Sample API starting")
    yield
    logger.info("Sample API shutting down")

app = FastAPI(
    title="Siemens SRE Sample API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.get("/api/orders")
def get_orders():
    start = time.perf_counter()
    status = "200"

    try:
        delay = float(os.getenv("SIMULATED_LATENCY_SECONDS", "0"))
        if delay > 0:
            time.sleep(min(delay, 10))

        if os.getenv("SIMULATE_FAILURE", "false").lower() == "true":
            status = "500"
            raise RuntimeError("Simulated order service failure")

        logger.info("Orders endpoint completed successfully")
        return {"orders": [{"id": 1, "item": "Laptop"}, {"id": 2, "item": "Monitor"}]}

    except RuntimeError:
        logger.exception("Orders endpoint failed")
        raise

    finally:
        duration = time.perf_counter() - start
        REQUEST_COUNT.labels("GET", "/api/orders", status).inc()
        REQUEST_LATENCY.labels("/api/orders").observe(duration)

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
