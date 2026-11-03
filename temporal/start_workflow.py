import asyncio
import os
import uuid

from temporalio.client import Client
from temporal.workflows.incident_triage import IncidentTriageWorkflow


async def main():
    temporal_address = os.getenv(
        "TEMPORAL_ADDRESS",
        "localhost:7233",
    )

    client = await Client.connect(
        temporal_address,
        namespace="default",
    )

    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"

    handle = await client.start_workflow(
        IncidentTriageWorkflow.run,
        incident_id,
        id=f"incident-triage-{incident_id}",
        task_queue="incident-triage",
    )

    print(f"Workflow started: {handle.id}")
    print(f"Workflow run ID: {handle.first_execution_run_id}")


if __name__ == "__main__":
    asyncio.run(main())
