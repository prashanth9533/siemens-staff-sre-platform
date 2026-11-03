
import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger("sample-api")

# OpenTelemetry configuration
resource = Resource.create({
    "service.name": "siemens-sample-api",
    "deployment.environment": "local",
})

tracer_provider = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "tempo.observability.svc.cluster.local:4317",
    ),
    insecure=True,
)

tracer_provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

trace.set_tracer_provider(tracer_provider)

# Prometheus metrics
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
    tracer_provider.force_flush()
    tracer_provider.shutdown()


app = FastAPI(
    title="Siemens SRE Sample API",
    version="1.0.0",
    lifespan=lifespan,
)

# Automatically instrument FastAPI requests
FastAPIInstrumentor.instrument_app(app)


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

        return {
            "orders": [
                {"id": 1, "item": "Laptop"},
                {"id": 2, "item": "Monitor"},
            ]
        }

    except RuntimeError:
        logger.exception("Orders endpoint failed")
        raise

    finally:
        duration = time.perf_counter() - start

        REQUEST_COUNT.labels(
            "GET", "/api/orders", status
        ).inc()

        REQUEST_LATENCY.labels(
            "/api/orders"
        ).observe(duration)


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
