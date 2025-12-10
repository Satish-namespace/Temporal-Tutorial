import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import MessageWorkflow
from gmail_workflow import GmailWorkflow
import activities

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: \n%(message)s\n",
)

async def main():
    client = await Client.connect("localhost:7233")

    workflow_worker = Worker(
        client,
        task_queue="message-task-queue",
        workflows=[MessageWorkflow],
    )
    
    activity_worker = Worker(
        client,
        task_queue="activity-task-queue",
        activities=[activities.process_message_activity]
    )
    
    # task_queue for the gmail_workflow.py
    gmail_workflow_worker = Worker(
        client,
        task_queue="gmail-workflow-task-queue",
        workflows=[GmailWorkflow]
    )
    
    gmail_process_activity_worker = Worker(
        client,
        task_queue="gmail-activity-task-queue",
        activities=[activities.process_email_activity]
    )

    print("Workers started...")
    # await asyncio.gather(
    #     workflow_worker.run(),
    #     activity_worker.run()
    # )
    
    await asyncio.gather(
        gmail_workflow_worker.run(),
        gmail_process_activity_worker.run()
    )


if __name__ == "__main__":
    asyncio.run(main())
