import time

# pyrefly: ignore [missing-import]
from celery import shared_task


@shared_task
def test_task():
    time.sleep(5)

    return "Celery task completed successfully"