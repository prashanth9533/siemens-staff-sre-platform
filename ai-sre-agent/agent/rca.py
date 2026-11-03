from datetime import datetime, timezone


def analyze_incident(evidence):
    metrics = evidence.get("metrics", {})
    logs = evidence.get("logs", {})
    traces = evidence.get("traces", {})

    # Validate observability source availability
    unavailable_sources = []

    if metrics.get("status") != "success":
        unavailable_sources.append("Prometheus")

    if logs.get("status") != "success":
        unavailable_sources.append("Loki")

    if "traces" not in traces:
        unavailable_sources.append("Tempo")

    metric_result = metrics.get("data", {}).get("result", [])

    # Do not interpret missing metrics as zero errors
    if not metric_result:
        unavailable_sources.append("Prometheus metrics")

    log_streams = logs.get("data", {}).get("result", [])
    log_count = sum(
        len(stream.get("values", []))
        for stream in log_streams
    )

    trace_list = traces.get("traces", [])
    trace_count = len(trace_list)

    # Return UNKNOWN if evidence collection is incomplete
    if unavailable_sources:
        return {
            "incident_id": evidence.get("incident", "unknown"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "severity": "UNKNOWN",
            "error_rate_percent": None,
            "error_log_entries": log_count,
            "trace_count": trace_count,
            "probable_root_cause": (
                "Unable to determine incident status because "
                "observability evidence is incomplete."
            ),
            "confidence": "LOW",
            "unavailable_sources": unavailable_sources,
            "recommendation": (
                "Restore observability connectivity and retry "
                "incident analysis."
            )
        }

    error_rate = float(metric_result[0]["value"][1])

    if error_rate > 5 and log_count > 0 and trace_count > 0:
        severity = "HIGH"
        confidence = "HIGH"
        root_cause = (
            "The sample API is experiencing simulated order-service "
            "failures. HTTP 500 responses are visible in metrics, "
            "application error logs, and distributed traces."
        )

    elif error_rate > 5:
        severity = "HIGH"
        confidence = "MEDIUM"
        root_cause = (
            "Elevated API error rate detected. "
            "Additional logs and traces are required."
        )

    else:
        severity = "NORMAL"
        confidence = "MEDIUM"
        root_cause = (
            "No elevated API error rate detected "
            "in the collected evidence."
        )

    return {
        "incident_id": evidence.get("incident", "unknown"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "severity": severity,
        "error_rate_percent": round(error_rate, 2),
        "error_log_entries": log_count,
        "trace_count": trace_count,
        "probable_root_cause": root_cause,
        "confidence": confidence,
        "recommendation": (
            "Inspect the order-service failure configuration "
            "and application exception. Restore normal operation "
            "through the GitOps deployment after validation."
        )
    }
