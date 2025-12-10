from temporalio import workflow
from datetime import timedelta
from activities import process_message_activity
from temporalio.common import RetryPolicy

@workflow.defn
class MessageWorkflow:
    def __init__(self):
        self.messages = []
        self.counter = 0

    @workflow.signal # signal are used to trigger / send changes to the workflow without requiring a response to be waited for 
    async def new_message(self, message: str):
        """Signal to add a new message to workflow queue"""
        self.messages.append(message)
        workflow.logger.info(f"Signal received: {message}")
        
    
    @workflow.query # query are used to read the state of the workflow
    def get_counter(self) -> int:
        return self.counter
    
    @workflow.update # signal + acknowldement but current haven't understood the working completely
    def new_message_and_receive_result(self, message: str):
        "Update interaction to add new message to workflow queue and receive result form workflow"
        self.messages.append(message)
        workflow.logger.info(f"Update interaction received: {message}")

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
            
            await workflow.wait_condition(lambda: len(self.messages) > 0) # using wait_continue to ensure that workflow is in sleep until some trigger is generated
            
            message = self.messages.pop(0)
            # Execute the activity for the new message
            result = await workflow.execute_activity(
                process_message_activity,
                message,
                task_queue="activity-task-queue",
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )
            workflow.logger.info(f"Activity result: {result}")
            self.counter += 1
            
            if self.counter >= 5: # event history can get larger as the workflow is long running, (history lenght max 51200, hisotyr size > 50 MB will terminate workflow)
                self.counter = 0 
                workflow.logger.info("Continuing as new...") 
                # continue as new will help us to create the same workflow with same id but with different runId to keep the workflow efficient
                return workflow.continue_as_new()
