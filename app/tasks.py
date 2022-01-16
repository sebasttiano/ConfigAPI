""" Celery tasks module """
import time
import logging
from celery_app import make_celery
from sqlalchemy.orm import scoped_session
from sqlalchemy import select, or_
from models import Tasks
from main import execute_command
from database import SessionLocal
from celery.result import AsyncResult

celery = make_celery()
logger = logging.getLogger('CApi')


def _check_race_condition(session: scoped_session, request: dict, task_id: int) -> bool:
    """ Checking that the task is not running on this device """
    response = session.query(Tasks).filter(Tasks.device_id == request["id"])\
        .filter(Tasks.task_id != task_id)\
        .filter(or_(Tasks.status == value for value in ("new", "in_progress")))
    if len(response.all()) > 0:
        logger.info("The device is busy... Waiting")
        for task in response.all():
            res = AsyncResult(str(task.task_id))
            for _ in range(5):
                if res.ready():  # TODO
                    break
                logger.info("Device re-checking in 3 seconds...")
                time.sleep(3)
    return True


@celery.task
def async_execute(request: dict, task_id: int):
    """
    Handles configuration process
    """
    session = scoped_session(SessionLocal)
    task = session.execute(select(Tasks).filter_by(task_id=task_id)).scalar_one()  # pylint: disable=E1101
    if _check_race_condition(session, request, task_id):
        time.sleep(3)
        execute_command(session, request, task)
