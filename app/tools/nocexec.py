""" Stub module simulating the connection and configuration of the device """
import logging
import time
import random
from exceptions import DeviceConnectionError, ExecutionCommandError


LOGIN = "admin"
PASS = "password"
CONN_SUCCESS_CHANCE = 0.8
EXEC_SUCCESS_CHANCE = 0.8

logger = logging.getLogger("CApi")


class NetExec:  # pylint: disable=too-few-public-methods
    """Class of the execution on the net devices"""

    def __init__(self, name: str, ip: str, login: str = LOGIN, password: str = PASS):
        self.name = name
        self.ip = ip
        self.login = login
        self.password = password

    def _connect(self) -> bool:
        time.sleep(1)
        if random.random() < CONN_SUCCESS_CHANCE:
            logger.info(f"Connection to {self.name} established via {self.ip}")
            return True
        raise DeviceConnectionError

    def send_cmd(self, command: str = 'show version') -> bool | None:
        """
         Emulates execution of command and returns True if succeeds
         or raises Exception
        """
        logger.info(f"Starting to execute {command} on the {self.name}")
        if self._connect():
            time.sleep(2)
            if random.random() < EXEC_SUCCESS_CHANCE:
                logger.info(f"The execution was successful")
                return True
            raise ExecutionCommandError
        return None


class JuniperExec(NetExec):  # pylint: disable=too-few-public-methods
    """For juniper devices"""


class CiscoExec(NetExec):  # pylint: disable=too-few-public-methods
    """For Cisco devices"""
