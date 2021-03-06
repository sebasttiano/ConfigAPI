"""
The collection of main executable functions
"""

import logging
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql import func
from models import Tasks, Devices
from tools.nocexec import JuniperExec, CiscoExec
from decorators import CheckExceptions
from exceptions import DeviceConnectionError, ExecutionCommandError

logger = logging.getLogger('CApi')


def _execute_on_device(device_info: list, command: str) -> bool:
    """Func to connect and execute commands"""

    device_call = None
    if device_info.vendor == "juniper":
        device_call = JuniperExec(device_info.name, device_info.ip)
    elif device_info.vendor == "cisco":
        device_call = CiscoExec(device_info.name, device_info.ip)
    return device_call.send_cmd(device_info.vendor, command)


@CheckExceptions((OperationalError, IntegrityError))
def _create_task(session: scoped_session, device_id: int,
                 command: str, status: str = "new") -> Tasks:
    """Creates a task with status and returns its id"""

    data = Tasks(status=status, device_id=device_id, command=command)
    session.add(data)
    session.commit()
    return data


@CheckExceptions((OperationalError, IntegrityError))
def _update_task(session: scoped_session, task: Tasks,
                 new_status: str, msg='', close_session: bool = True) -> None:
    """ After configuration updates the status of the tasks"""

    if msg:
        task.msg = msg
    task.last_changed = func.now()
    task.status = new_status
    session.commit()
    if close_session:
        session.close()


@CheckExceptions((OperationalError, IntegrityError))
def _get_devices(session: scoped_session, device_id: int = 0) -> list:
    """Fetches info about devices from DB. Loads all if device_id == 0"""

    if device_id == 0:
        return session.query(Devices).all()
    return session.query(Devices).filter(Devices.id == device_id).first()


def get_devices(session: scoped_session) -> list:
    """ Makes query to db and returns existing devices"""

    result = []
    records = _get_devices(session)
    for record in records:
        record.__dict__.pop("_sa_instance_state")
        result.append(record.__dict__)
    session.close()
    return result


@CheckExceptions((OperationalError, IntegrityError))
def check_status(session: scoped_session, task_id: int):
    """Get current (last) status of tasks"""

    res = session.query(Tasks).filter(Tasks.task_id == task_id).first()
    res.__dict__.pop("_sa_instance_state")
    session.close()
    return res.__dict__


def execute_command(session: scoped_session, request: dict, task: Tasks) -> None:
    """
    Handles configuration process.
    Returns created task id
    """

    device_info = _get_devices(session, (request["id"]))
    _update_task(session, task, new_status="in_progress", close_session=False)
    try:
        if _execute_on_device(device_info, request["command"]):
            _update_task(session, task, "success")
            logger.info(f"The execution was successful")
    except (DeviceConnectionError, ExecutionCommandError) as err:
        logger.error(f"Configuration FAILED!!!\n{err.__class__.__name__}")
        _update_task(session, task, "error", msg=err.__class__.__name__)
