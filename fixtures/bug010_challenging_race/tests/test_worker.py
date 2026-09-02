from src.task_worker import TaskWorker

def test_task_failure_status():
    worker = TaskWorker()
    worker.process_task("task-100", should_fail=True)
    assert worker.get_status("task-100") == "FAILED"
