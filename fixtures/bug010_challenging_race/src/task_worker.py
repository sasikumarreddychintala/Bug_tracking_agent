class TaskWorker:
    def __init__(self):
        self.task_states = {}

    def process_task(self, task_id: str, should_fail: bool):
        self.task_states[task_id] = "RUNNING"
        if should_fail:
            self.task_states[task_id] = "FAILED"
            # BUG: Missing return statement causes execution to fall through and overwrite status with 'COMPLETED'
        self.task_states[task_id] = "COMPLETED"

    def get_status(self, task_id: str) -> str:
        return self.task_states.get(task_id, "UNKNOWN")
