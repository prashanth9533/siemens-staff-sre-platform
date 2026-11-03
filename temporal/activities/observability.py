import asyncio

from temporalio import activity

from agent.observability import collect_incident_evidence
from agent.rca import analyze_incident


@activity.defn
async def collect_observability_snapshot(incident_id: str) -> dict:
    evidence = await asyncio.to_thread(
        collect_incident_evidence
    )

    evidence["incident"] = incident_id

    rca_report = analyze_incident(evidence)

    return {
        "incident_id": incident_id,
        "evidence": evidence,
        "rca_report": rca_report,
    }
