from app.core.celery import celery_app
import time

from app.util.log import get_logger

logger = get_logger()

"""
This file contains a sample celery task
"""

@celery_app.task()
def test_celery() -> str:
    """
    Sample celery task
    """
    logger.info("GOT TASK")
    time.sleep(3)
    logger.info("TASK DONE")
    return "Test task finished successfully!"
