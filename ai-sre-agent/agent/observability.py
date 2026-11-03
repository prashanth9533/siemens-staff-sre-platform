import json
import os
import urllib.parse
import urllib.request


PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://localhost:9090"
)

LOKI_URL = os.getenv(
    "LOKI_URL",
    "http://localhost:3101"
)

TEMPO_URL = os.getenv(
    "TEMPO_URL",
    "http://localhost:3200"
)


def get_json(url):
    try:
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def query_prometheus(promql):
    params = urllib.parse.urlencode({"query": promql})
    return get_json(f"{PROMETHEUS_URL}/api/v1/query?{params}")


def query_loki():
    params = urllib.parse.urlencode({
        "query": '{namespace="sample-api"} |= "Orders endpoint failed"',
        "limit": "10"
    })
    return get_json(f"{LOKI_URL}/loki/api/v1/query_range?{params}")


def query_tempo():
    params = urllib.parse.urlencode({
        "service.name": "siemens-sample-api",
        "name": "GET /api/orders",
        "limit": "10"
    })
    return get_json(f"{TEMPO_URL}/api/search?{params}")


def collect_incident_evidence():
    return {
        "incident": "HighApiErrorRate",
        "metrics": query_prometheus(
            '100 * sum(rate(sample_api_requests_total{status=~"5.."}[5m])) '
            '/ clamp_min(sum(rate(sample_api_requests_total[5m])), 1)'
        ),
        "logs": query_loki(),
        "traces": query_tempo()
    }
