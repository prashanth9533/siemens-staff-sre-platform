import json

from agent.observability import collect_incident_evidence
from agent.rca import analyze_incident


def main():
    print("Starting AI SRE Incident RCA Agent...")

    evidence = collect_incident_evidence()

    print("Observability evidence collected.")

    report = analyze_incident(evidence)

    print("\n========== INCIDENT RCA REPORT ==========")
    print(json.dumps(report, indent=4))
    print("=========================================")


if __name__ == "__main__":
    main()
