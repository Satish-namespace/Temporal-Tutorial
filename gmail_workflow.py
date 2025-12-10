from temporalio import workflow
from datetime import timedelta
from activities import process_email_activity
from temporalio.common import RetryPolicy
from shared import EmailInputPayload
import json


@workflow.defn
class GmailWorkflow:
    def __init__(self):
        self.new_emails = []
        self.counter = 0

    @workflow.signal # signal are used to trigger / send changes to the workflow without requiring a response to be waited for 
    async def email_received(self, new_mail: EmailInputPayload):
        """Signal to add a new message to workflow queue"""
        self.new_emails.append(new_mail)
        
    @workflow.run
    async def run(self):
        # Activity Retry Policy Example
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=5), # wait 5 seconds before retrying if the activity fails
            backoff_coefficient=2.0, # double the delay of retry after each retry attempt
            maximum_interval=timedelta(seconds=60), # maximum of 60 seconds will be the interval of each retry attempt
            maximum_attempts=10 # fail the activity completely after 10 retry attempts
        )
        while True:
            
            await workflow.wait_condition(lambda: len(self.new_emails) > 0) # using wait_continue to ensure that workflow is in sleep until some trigger is generated
            self.counter += 1
            
            mail = self.new_emails.pop(0)
            # Execute the activity for the new message
            result = await workflow.execute_activity(
                process_email_activity,
                mail,
                task_queue="gmail-activity-task-queue",
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )
        
            workflow.logger.info(f"Activity result: {result}")
            if self.counter >= 5: # event history can get larger as the workflow is long running, (history lenght max 51200, hisotyr size > 50 MB will terminate workflow)
                self.counter = 0 
                workflow.logger.info("Continuing as new...") 
                # continue as new will help us to create the same workflow with same id but with different runId to keep the workflow efficient
                return workflow.continue_as_new()