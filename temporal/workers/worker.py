import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from temporal.workflows.incident_triage import IncidentTriageWorkflow
from temporal.activities.observability import collect_observability_snapshot


async def main():
    temporal_address = os.getenv(
        "TEMPORAL_ADDRESS",
        "localhost:7233",
    )

    client = await Client.connect(
        temporal_address,
        namespace="default",
    )

    worker = Worker(
        client,
        task_queue="incident-triage",
        workflows=[IncidentTriageWorkflow],
        activities=[collect_observability_snapshot],
    )

    print(f"Connected to Temporal at {temporal_address}")
    print("Listening on task queue: incident-triage")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
