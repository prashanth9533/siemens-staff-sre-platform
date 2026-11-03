import unittest

from agent.rca import analyze_incident


class TestRCAAgent(unittest.TestCase):

    def setUp(self):
        self.healthy_metrics = {
            "status": "success",
            "data": {
                "result": [
                    {"value": [1793727000, "12.5"]}
                ]
            }
        }

        self.logs = {
            "status": "success",
            "data": {
                "result": [
                    {"values": [["123", "Orders endpoint failed"]]}
                ]
            }
        }

        self.traces = {
            "traces": [{"traceID": "abc123"}]
        }

    def test_high_severity_incident(self):
        evidence = {
            "incident": "HighApiErrorRate",
            "metrics": self.healthy_metrics,
            "logs": self.logs,
            "traces": self.traces
        }

        report = analyze_incident(evidence)

        self.assertEqual(report["severity"], "HIGH")
        self.assertEqual(report["confidence"], "HIGH")
        self.assertGreater(report["error_rate_percent"], 5)

    def test_unavailable_prometheus_returns_unknown(self):
        evidence = {
            "incident": "HighApiErrorRate",
            "metrics": {"error": "Connection refused"},
            "logs": self.logs,
            "traces": self.traces
        }

        report = analyze_incident(evidence)

        self.assertEqual(report["severity"], "UNKNOWN")
        self.assertIn("Prometheus", report["unavailable_sources"])

    def test_missing_metrics_returns_unknown(self):
        evidence = {
            "incident": "HighApiErrorRate",
            "metrics": {
                "status": "success",
                "data": {"result": []}
            },
            "logs": self.logs,
            "traces": self.traces
        }

        report = analyze_incident(evidence)

        self.assertEqual(report["severity"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
