from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from temporal.activities.observability import (
        collect_observability_snapshot,
    )


@workflow.defn
class IncidentTriageWorkflow:

    @workflow.run
    async def run(self, incident_id: str) -> dict:
        snapshot = await workflow.execute_activity(
            collect_observability_snapshot,
            incident_id,
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "incident_id": incident_id,
            "status": "triage_completed",
            "evidence": snapshot,
        }
