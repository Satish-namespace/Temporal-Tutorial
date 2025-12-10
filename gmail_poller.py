# poller.py
import asyncio
from temporalio.client import Client
from gmail_workflow import GmailWorkflow
from shared import EmailInputPayload

WORKFLOW_ID = "gmail-received-workflow-1"

# starting the workflow but polling is external to the workflow and poller will send the signal when some new email is generated
async def start_gmail_workflow(client: Client):
    # Start the workflow if not already running
    try:
        await client.start_workflow(
            GmailWorkflow,
            id=WORKFLOW_ID,
            task_queue="gmail-workflow-task-queue",
        )
        print(f"Workflow started with ID: {WORKFLOW_ID}")
    except Exception as e:
        print(f"Workflow already running: {e}")

# ----- custom email checker -----
async def check_for_new_email():
    import random, datetime, uuid

    email_found = random.choice([True, False])

    if email_found:
        return EmailInputPayload(
            id=str(uuid.uuid4()),
            subject=f"New Email Found at {datetime.datetime.now()}",
            body="Hello this is the new mail received"
        )
        


# ----- Poller to send signals if new mail has been received-----
async def poll_gmail():
    client = await Client.connect("localhost:7233")
    
    # start the workflow 
    await start_gmail_workflow(client)
    
    handle = client.get_workflow_handle(WORKFLOW_ID) # handle provides methods(signal, query, update) to interact with the workflow (of mentioned workflow id)
    
    while True:
        mail_received = await check_for_new_email()  # Check for any new emails with custom login

        if mail_received:
            print(f"\nNew email received: \nID: {mail_received.id}\nSubject: {mail_received.subject}\nBody: {mail_received.body}")
            
            # any new email generation will trigger the signal in the workflow
            await handle.signal(
                "email_received",
                mail_received
            )

        await asyncio.sleep(30)


async def main():
    await poll_gmail()

if __name__ == "__main__":
    asyncio.run(main())
