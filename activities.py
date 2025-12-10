from temporalio import activity
import asyncio
import os
from temporalio import activity
from shared import EmailInputPayload, EmailOutputPayload

@activity.defn
async def process_message_activity(message: str):
    activity.logger.info(f"Activity started for: {message} ")
    await asyncio.sleep(1)  # simulate work
    return f"Processed: {message}"


@activity.defn
async def process_email_activity(new_mail: EmailInputPayload) -> EmailOutputPayload:
    print(f"Processing ID: {new_mail.id}")
    print(f"Processing subject: {new_mail.subject}")
    print(f"Processing body: {new_mail.body}")
    return EmailOutputPayload(new_mail.id, new_mail.subject, new_mail.body, True)